from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import transaction
from django import forms
from .models import (Agent, Function, ScheduleType, DailyRotationPlan, RotationPeriod,
                     ShiftSchedule, ShiftSchedulePeriod, ShiftScheduleWeek, ShiftScheduleDailyPlan, PublicHoliday, Department)
from .forms import (AgentForm, FunctionForm, ScheduleTypeForm, DailyRotationPlanForm, RotationPeriodForm,
                    ShiftScheduleForm, ShiftSchedulePeriodForm, ShiftScheduleWeekForm, ShiftScheduleDailyPlanForm, WeeklyPlanFormSet, PublicHolidayForm, DepartmentForm)
from .decorators import permission_required, admin_required, viewer_required, get_agent_from_user


# Authentication Views
def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Check if user needs to change password
            agent = get_agent_from_user(user)
            if agent and not agent.password_changed:
                return redirect('change_password')
            
            # Redirect to next URL or home
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.error(request, 'Matricule ou mot de passe incorrect.')
    
    return render(request, 'core/auth/login.html')


def logout_view(request):
    """Custom logout view"""
    logout(request)
    return redirect('login')


@login_required
@transaction.atomic
def change_password(request):
    """Change password view"""
    agent = get_agent_from_user(request.user)
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            
            # Mark password as changed for agent
            if agent:
                agent.password_changed = True
                agent.save(update_fields=['password_changed'])
            
            messages.success(request, 'Votre mot de passe a été changé avec succès.')
            
            # Re-authenticate user to keep them logged in
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            
            return redirect('index')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/auth/change_password.html', {'form': form})


@viewer_required
def index(request):
    """Homepage with schedule placeholder"""
    return render(request, 'core/index.html')


def is_staff_user(user):
    """Check if user is staff member (for Django admin compatibility)"""
    return user.is_authenticated and user.is_staff


@admin_required
def agent_count(request):
    """HTMX endpoint for agent count"""
    count = Agent.objects.count()
    return HttpResponse(f'<p class="text-2xl font-semibold text-gray-900" id="agent-count">{count}</p>')


@admin_required
def function_count(request):
    """HTMX endpoint for function count"""
    count = Function.objects.count()
    return HttpResponse(f'<p class="text-2xl font-semibold text-gray-900" id="function-count">{count}</p>')


@admin_required
def schedule_type_count(request):
    """HTMX endpoint for schedule type count"""
    count = ScheduleType.objects.count()
    return HttpResponse(f'<p class="text-2xl font-semibold text-gray-900" id="schedule-type-count">{count}</p>')


# Agent Views
@admin_required
def agent_list(request):
    """List all agents with search and pagination"""
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'matricule')
    order = request.GET.get('order', 'asc')
    hide_departed = request.GET.get('hide_departed', 'false') == 'true'
    
    agents = Agent.objects.all()
    
    # Filter out departed agents if requested
    if hide_departed:
        agents = agents.filter(departure_date__isnull=True)
    
    if search_query:
        agents = agents.filter(
            Q(matricule__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Apply sorting
    valid_sorts = ['matricule', 'last_name', 'first_name', 'grade', 'hire_date', 'permission_level']
    if sort_by in valid_sorts:
        if order == 'desc':
            sort_by = f'-{sort_by}'
        agents = agents.order_by(sort_by)
    else:
        agents = agents.order_by('matricule')
    
    paginator = Paginator(agents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'matricule')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/agents/agent_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order,
            'hide_departed': hide_departed
        })
    
    return render(request, 'core/agents/agent_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_sort': current_sort,
        'current_order': current_order,
        'hide_departed': hide_departed
    })


@admin_required
@transaction.atomic
def agent_create(request):
    """Create new agent"""
    if request.method == 'POST':
        form = AgentForm(request.POST, user=request.user)
        if form.is_valid():
            agent = form.save()
            messages.success(request, f'Agent {agent.matricule} créé avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Agent {agent.matricule} créé avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("agent-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('agent_list')
    else:
        form = AgentForm(user=request.user)
    
    template = 'core/agents/agent_form_htmx.html' if request.headers.get('HX-Request') else 'core/agents/agent_form.html'
    return render(request, template, {
        'form': form,
        'title': 'Créer un Agent',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
def agent_detail(request, pk):
    """Agent detail view"""
    agent = get_object_or_404(Agent, pk=pk)
    return render(request, 'core/agents/agent_detail.html', {'agent': agent})


@admin_required
@transaction.atomic
def agent_edit(request, pk):
    """Edit existing agent"""
    agent = get_object_or_404(Agent, pk=pk)
    
    if request.method == 'POST':
        form = AgentForm(request.POST, instance=agent, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Agent {agent.matricule} modifié avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Agent {agent.matricule} modifié avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("agent-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('agent_list')
    else:
        form = AgentForm(instance=agent, user=request.user)
    
    template = 'core/agents/agent_form_htmx.html' if request.headers.get('HX-Request') else 'core/agents/agent_form.html'
    return render(request, template, {
        'form': form,
        'agent': agent,
        'title': f'Modifier {agent.matricule}',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
@require_http_methods(["DELETE"])
@transaction.atomic
def agent_delete(request, pk):
    """Delete agent"""
    agent = get_object_or_404(Agent, pk=pk)
    matricule = agent.matricule
    agent.delete()
    
    if request.headers.get('HX-Request'):
        # Return updated agent list with same filters and sorting
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort', 'matricule')
        order = request.GET.get('order', 'asc')
        
        agents = Agent.objects.all()
        if search_query:
            agents = agents.filter(
                Q(matricule__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        
        # Apply same sorting
        valid_sorts = ['matricule', 'last_name', 'first_name', 'grade', 'hire_date', 'permission_level']
        if sort_by in valid_sorts:
            if order == 'desc':
                sort_by = f'-{sort_by}'
            agents = agents.order_by(sort_by)
        else:
            agents = agents.order_by('matricule')
        
        paginator = Paginator(agents, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        messages.success(request, f'Agent {matricule} supprimé avec succès.')
        return render(request, 'core/agents/agent_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': request.GET.get('sort', 'matricule'),
            'current_order': request.GET.get('order', 'asc')
        })
    
    messages.success(request, f'Agent {matricule} supprimé avec succès.')
    return redirect('agent_list')


# Function Views
@admin_required
def function_list(request):
    """List all functions with search, sorting and pagination"""
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'designation')
    order = request.GET.get('order', 'asc')
    hide_inactive = request.GET.get('hide_inactive', 'false') == 'true'
    
    functions = Function.objects.all()
    
    # Filter out inactive functions if requested
    if hide_inactive:
        functions = functions.filter(status=True)
    
    if search_query:
        functions = functions.filter(
            Q(designation__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply sorting
    valid_sorts = ['designation', 'description', 'status']
    if sort_by in valid_sorts:
        if order == 'desc':
            sort_by = f'-{sort_by}'
        functions = functions.order_by(sort_by)
    else:
        functions = functions.order_by('designation')
    
    paginator = Paginator(functions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'designation')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/functions/function_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order,
            'hide_inactive': hide_inactive
        })
    
    return render(request, 'core/functions/function_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_sort': current_sort,
        'current_order': current_order,
        'hide_inactive': hide_inactive
    })


@admin_required
def function_create(request):
    """Create new function"""
    if request.method == 'POST':
        form = FunctionForm(request.POST)
        if form.is_valid():
            function = form.save()
            messages.success(request, f'Fonction "{function.designation}" créée avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Fonction "{function.designation}" créée avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("function-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('function_list')
    else:
        form = FunctionForm()
    
    template = 'core/functions/function_form_htmx.html' if request.headers.get('HX-Request') else 'core/functions/function_form.html'
    return render(request, template, {
        'form': form,
        'title': 'Créer une Fonction',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
def function_detail(request, pk):
    """Function detail view"""
    function = get_object_or_404(Function, pk=pk)
    return render(request, 'core/functions/function_detail.html', {'function': function})


@admin_required
def function_edit(request, pk):
    """Edit existing function"""
    function = get_object_or_404(Function, pk=pk)
    
    if request.method == 'POST':
        form = FunctionForm(request.POST, instance=function)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fonction "{function.designation}" modifiée avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Fonction "{function.designation}" modifiée avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("function-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('function_list')
    else:
        form = FunctionForm(instance=function)
    
    template = 'core/functions/function_form_htmx.html' if request.headers.get('HX-Request') else 'core/functions/function_form.html'
    return render(request, template, {
        'form': form,
        'function': function,
        'title': f'Modifier "{function.designation}"',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
@require_http_methods(["DELETE"])
def function_delete(request, pk):
    """Delete function"""
    function = get_object_or_404(Function, pk=pk)
    designation = function.designation
    function.delete()
    
    if request.headers.get('HX-Request'):
        # Return updated function list with same filters and sorting
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort', 'designation')
        order = request.GET.get('order', 'asc')
        hide_inactive = request.GET.get('hide_inactive', 'false') == 'true'
        
        functions = Function.objects.all()
        
        # Filter out inactive functions if requested
        if hide_inactive:
            functions = functions.filter(status=True)
            
        if search_query:
            functions = functions.filter(
                Q(designation__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Apply same sorting
        valid_sorts = ['designation', 'description', 'status']
        if sort_by in valid_sorts:
            if order == 'desc':
                sort_by = f'-{sort_by}'
            functions = functions.order_by(sort_by)
        else:
            functions = functions.order_by('designation')
        
        paginator = Paginator(functions, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        messages.success(request, f'Fonction "{designation}" supprimée avec succès.')
        return render(request, 'core/functions/function_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': request.GET.get('sort', 'designation'),
            'current_order': request.GET.get('order', 'asc'),
            'hide_inactive': hide_inactive
        })
    
    messages.success(request, f'Fonction "{designation}" supprimée avec succès.')
    return redirect('function_list')


@permission_required('admin')
@require_http_methods(["POST"])
@transaction.atomic
def change_agent_permission(request, pk):
    """Change agent permission level"""
    agent = get_object_or_404(Agent, pk=pk)
    current_user_agent = get_agent_from_user(request.user)
    
    new_permission = request.POST.get('permission_level')
    
    # Validation
    if not new_permission or new_permission not in [choice[0] for choice in Agent.PERMISSION_CHOICES]:
        return HttpResponse('<div class="text-red-600 text-sm">Niveau de permission invalide</div>', status=400)
    
    # Only allow super admins to change super admin permissions
    if agent.permission_level == 'S' and not current_user_agent.is_super_admin():
        return HttpResponse('<div class="text-red-600 text-sm">Permission refusée</div>', status=403)
    
    # Regular admins cannot create super admins
    if new_permission == 'S' and not current_user_agent.is_super_admin():
        return HttpResponse('<div class="text-red-600 text-sm">Permission refusée</div>', status=403)
    
    # Prevent agents from removing their own admin rights
    if agent.user == request.user and new_permission not in ['A', 'S']:
        return HttpResponse(
            '<div class="text-red-600 text-sm">Vous ne pouvez pas retirer vos propres droits d\'administration.</div>',
            status=400
        )
    
    agent.permission_level = new_permission
    agent.save(update_fields=['permission_level'])
    
    # Update Django user permissions if needed
    if agent.user:
        if new_permission == 'S':
            agent.user.is_staff = True
            agent.user.is_superuser = True
        else:
            agent.user.is_staff = False
            agent.user.is_superuser = False
        agent.user.save()
    
    return HttpResponse('<div class="text-green-600 text-sm">Permission mise à jour avec succès</div>')


# ScheduleType Views
@admin_required
def schedule_type_list(request):
    """List all schedule types with search, sorting and pagination"""
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'designation')
    order = request.GET.get('order', 'asc')
    
    schedule_types = ScheduleType.objects.annotate(
        plans_count=Count('dailyrotationplan')
    ).all()
    
    if search_query:
        schedule_types = schedule_types.filter(
            Q(designation__icontains=search_query) |
            Q(short_designation__icontains=search_query)
        )
    
    # Apply sorting
    valid_sorts = ['designation', 'short_designation', 'color']
    if sort_by in valid_sorts:
        if order == 'desc':
            sort_by = f'-{sort_by}'
        schedule_types = schedule_types.order_by(sort_by)
    else:
        schedule_types = schedule_types.order_by('designation')
    
    paginator = Paginator(schedule_types, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'designation')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/schedule_types/schedule_type_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order
        })
    
    return render(request, 'core/schedule_types/schedule_type_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_sort': current_sort,
        'current_order': current_order
    })


@admin_required
def schedule_type_create(request):
    """Create new schedule type"""
    if request.method == 'POST':
        form = ScheduleTypeForm(request.POST)
        if form.is_valid():
            schedule_type = form.save()
            messages.success(request, f'Type de planning "{schedule_type.designation}" créé avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Type de planning "{schedule_type.designation}" créé avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("schedule-type-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('schedule_type_list')
    else:
        form = ScheduleTypeForm()
    
    template = 'core/schedule_types/schedule_type_form_htmx.html' if request.headers.get('HX-Request') else 'core/schedule_types/schedule_type_form.html'
    return render(request, template, {
        'form': form,
        'title': 'Créer un Type de Planning',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
def schedule_type_detail(request, pk):
    """Schedule type detail view"""
    schedule_type = get_object_or_404(ScheduleType, pk=pk)
    return render(request, 'core/schedule_types/schedule_type_detail.html', {'schedule_type': schedule_type})


@admin_required
def schedule_type_edit(request, pk):
    """Edit existing schedule type"""
    schedule_type = get_object_or_404(ScheduleType, pk=pk)
    
    if request.method == 'POST':
        form = ScheduleTypeForm(request.POST, instance=schedule_type)
        if form.is_valid():
            form.save()
            messages.success(request, f'Type de planning "{schedule_type.designation}" modifié avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Type de planning "{schedule_type.designation}" modifié avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("schedule-type-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('schedule_type_list')
    else:
        form = ScheduleTypeForm(instance=schedule_type)
    
    template = 'core/schedule_types/schedule_type_form_htmx.html' if request.headers.get('HX-Request') else 'core/schedule_types/schedule_type_form.html'
    return render(request, template, {
        'form': form,
        'schedule_type': schedule_type,
        'title': f'Modifier "{schedule_type.designation}"',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
@require_http_methods(["DELETE"])
def schedule_type_delete(request, pk):
    """Delete schedule type"""
    schedule_type = get_object_or_404(ScheduleType, pk=pk)
    designation = schedule_type.designation
    
    # Check if schedule type is linked to any rotation plans
    linked_plans = DailyRotationPlan.objects.filter(schedule_type=schedule_type)
    if linked_plans.exists():
        plan_names = ", ".join([plan.designation for plan in linked_plans[:3]])
        if linked_plans.count() > 3:
            plan_names += f" et {linked_plans.count() - 3} autre(s)"
        
        error_message = f'Impossible de supprimer le type d\'horaire "{designation}". Il est utilisé par les rythmes quotidiens suivants : {plan_names}.'
        
        if request.headers.get('HX-Request'):
            return HttpResponse(
                f'<div class="p-4 mb-4 text-red-800 bg-red-100 rounded-lg border border-red-200">'
                f'<div class="flex items-center">'
                f'<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">'
                f'<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>'
                f'</svg>'
                f'<strong>Erreur de suppression</strong>'
                f'</div>'
                f'<p class="mt-2">{error_message}</p>'
                f'<p class="text-sm mt-2">Veuillez d\'abord supprimer ou modifier ces rythme quotidien avant de supprimer ce type d\'horaire.</p>'
                f'</div>',
                status=400
            )
        
        messages.error(request, error_message)
        return redirect('schedule_type_list')
    
    schedule_type.delete()
    
    if request.headers.get('HX-Request'):
        # Return updated schedule type list with same filters and sorting
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort', 'designation')
        order = request.GET.get('order', 'asc')
        
        schedule_types = ScheduleType.objects.all()
            
        if search_query:
            schedule_types = schedule_types.filter(
                Q(designation__icontains=search_query) |
                Q(short_designation__icontains=search_query)
            )
        
        # Apply same sorting
        valid_sorts = ['designation', 'short_designation', 'color']
        if sort_by in valid_sorts:
            if order == 'desc':
                sort_by = f'-{sort_by}'
            schedule_types = schedule_types.order_by(sort_by)
        else:
            schedule_types = schedule_types.order_by('designation')
        
        paginator = Paginator(schedule_types, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        messages.success(request, f'Type de planning "{designation}" supprimé avec succès.')
        return render(request, 'core/schedule_types/schedule_type_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': request.GET.get('sort', 'designation'),
            'current_order': request.GET.get('order', 'asc')
        })
    
    messages.success(request, f'Type de planning "{designation}" supprimé avec succès.')
    return redirect('schedule_type_list')


# DailyRotationPlan Views
@admin_required
def daily_rotation_plan_list(request):
    """List all daily rotation plans with search, sorting and pagination"""
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'designation')
    order = request.GET.get('order', 'asc')
    
    plans = DailyRotationPlan.objects.select_related('schedule_type').all()
    
    if search_query:
        plans = plans.filter(
            Q(designation__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(schedule_type__designation__icontains=search_query)
        )
    
    # Apply sorting
    valid_sorts = ['designation', 'schedule_type__designation', 'created_at']
    if sort_by in valid_sorts:
        if order == 'desc':
            sort_by = f'-{sort_by}'
        plans = plans.order_by(sort_by)
    else:
        plans = plans.order_by('designation')
    
    paginator = Paginator(plans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'designation')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/daily_rotation_plans/daily_rotation_plan_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order
        })
    
    return render(request, 'core/daily_rotation_plans/daily_rotation_plan_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_sort': current_sort,
        'current_order': current_order
    })


@admin_required
@transaction.atomic
def daily_rotation_plan_create(request):
    """Create new daily rotation plan"""
    if request.method == 'POST':
        form = DailyRotationPlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Plan de rotation "{plan.designation}" créé avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Plan de rotation "{plan.designation}" créé avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("plan-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('daily_rotation_plan_list')
        # If form is invalid and it's an HTMX request, return the form with errors
        elif request.headers.get('HX-Request'):
            template = 'core/daily_rotation_plans/daily_rotation_plan_form_htmx.html'
            return render(request, template, {
                'form': form,
                'title': 'Créer un Plan de Rotation',
                'is_htmx': True
            })
    else:
        form = DailyRotationPlanForm()
    
    template = 'core/daily_rotation_plans/daily_rotation_plan_form_htmx.html' if request.headers.get('HX-Request') else 'core/daily_rotation_plans/daily_rotation_plan_form.html'
    return render(request, template, {
        'form': form,
        'title': 'Créer un Plan de Rotation',
        'is_htmx': request.headers.get('HX-Request')
    })


@viewer_required
def daily_rotation_plan_detail(request, pk):
    """Daily rotation plan detail view with periods"""
    plan = get_object_or_404(DailyRotationPlan.objects.select_related('schedule_type'), pk=pk)
    periods = plan.periods.all().order_by('start_date', 'start_time')
    
    return render(request, 'core/daily_rotation_plans/daily_rotation_plan_detail.html', {
        'plan': plan,
        'periods': periods
    })


@admin_required
@transaction.atomic
def daily_rotation_plan_edit(request, pk):
    """Edit existing daily rotation plan"""
    plan = get_object_or_404(DailyRotationPlan, pk=pk)
    
    if request.method == 'POST':
        form = DailyRotationPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f'Plan de rotation "{plan.designation}" modifié avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Plan de rotation "{plan.designation}" modifié avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("plan-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('daily_rotation_plan_list')
        # If form is invalid and it's an HTMX request, return the form with errors
        elif request.headers.get('HX-Request'):
            template = 'core/daily_rotation_plans/daily_rotation_plan_form_htmx.html'
            return render(request, template, {
                'form': form,
                'plan': plan,
                'title': f'Modifier "{plan.designation}"',
                'is_htmx': True
            })
    else:
        form = DailyRotationPlanForm(instance=plan)
    
    template = 'core/daily_rotation_plans/daily_rotation_plan_form_htmx.html' if request.headers.get('HX-Request') else 'core/daily_rotation_plans/daily_rotation_plan_form.html'
    return render(request, template, {
        'form': form,
        'plan': plan,
        'title': f'Modifier "{plan.designation}"',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
@require_http_methods(["DELETE"])
@transaction.atomic
def daily_rotation_plan_delete(request, pk):
    """Delete daily rotation plan"""
    plan = get_object_or_404(DailyRotationPlan, pk=pk)
    designation = plan.designation
    plan.delete()
    
    if request.headers.get('HX-Request'):
        # Return updated plan list with same filters and sorting
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort', 'designation')
        order = request.GET.get('order', 'asc')
        
        plans = DailyRotationPlan.objects.select_related('schedule_type').all()
            
        if search_query:
            plans = plans.filter(
                Q(designation__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(schedule_type__designation__icontains=search_query)
            )
        
        # Apply same sorting
        valid_sorts = ['designation', 'schedule_type__designation', 'created_at']
        if sort_by in valid_sorts:
            if order == 'desc':
                sort_by = f'-{sort_by}'
            plans = plans.order_by(sort_by)
        else:
            plans = plans.order_by('designation')
        
        paginator = Paginator(plans, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        messages.success(request, f'Plan de rotation "{designation}" supprimé avec succès.')
        return render(request, 'core/daily_rotation_plans/daily_rotation_plan_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': request.GET.get('sort', 'designation'),
            'current_order': request.GET.get('order', 'asc')
        })
    
    messages.success(request, f'Plan de rotation "{designation}" supprimé avec succès.')
    return redirect('daily_rotation_plan_list')


# RotationPeriod Views
@admin_required
def rotation_period_list(request):
    """List all rotation periods with search, sorting and pagination"""
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'start_date')
    order = request.GET.get('order', 'asc')
    plan_filter = request.GET.get('plan_filter', '')
    
    periods = RotationPeriod.objects.select_related('daily_rotation_plan', 'daily_rotation_plan__schedule_type').all()
    
    # Filter by plan if specified
    if plan_filter:
        periods = periods.filter(daily_rotation_plan_id=plan_filter)
    
    if search_query:
        periods = periods.filter(
            Q(daily_rotation_plan__designation__icontains=search_query)
        )
    
    # Apply sorting
    valid_sorts = ['start_date', 'end_date', 'start_time', 'end_time', 'daily_rotation_plan__designation']
    if sort_by in valid_sorts:
        if order == 'desc':
            sort_by = f'-{sort_by}'
        periods = periods.order_by(sort_by)
    else:
        periods = periods.order_by('start_date', 'start_time')
    
    paginator = Paginator(periods, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get plans for filter dropdown
    plans = DailyRotationPlan.objects.all().order_by('designation')
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'start_date')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/rotation_periods/rotation_period_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order,
            'plan_filter': plan_filter,
            'plans': plans
        })
    
    return render(request, 'core/rotation_periods/rotation_period_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_sort': current_sort,
        'current_order': current_order,
        'plan_filter': plan_filter,
        'plans': plans
    })


@admin_required
@transaction.atomic
def rotation_period_create(request):
    """Create new rotation period"""
    plan_id = request.GET.get('plan_id')
    
    if request.method == 'POST':
        form = RotationPeriodForm(request.POST)
        if form.is_valid():
            period = form.save()
            messages.success(request, f'Période de rotation créée avec succès.')
            if request.headers.get('HX-Request'):
                plan_id = period.daily_rotation_plan.pk
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Période de rotation créée avec succès.</div>'
                    f'<script>refreshPlanPeriods({plan_id}); setTimeout(() => {{ document.querySelector("form[hx-post*=\'rotation_period\']").reset(); }}, 500);</script>'
                )
            # Redirect to plan detail if creating from plan view
            if plan_id:
                return redirect('daily_rotation_plan_detail', pk=plan_id)
            return redirect('rotation_period_list')
        # If form is invalid and it's an HTMX request, return the form with errors
        elif request.headers.get('HX-Request'):
            template = 'core/rotation_periods/rotation_period_form_htmx.html'
            return render(request, template, {
                'form': form,
                'title': 'Créer une Période de Rotation',
                'is_htmx': True,
                'plan_id': plan_id
            })
    else:
        form = RotationPeriodForm()
        # Pre-select plan if creating from plan detail view
        if plan_id:
            form.initial['daily_rotation_plan'] = plan_id
    
    template = 'core/rotation_periods/rotation_period_form_htmx.html' if request.headers.get('HX-Request') else 'core/rotation_periods/rotation_period_form.html'
    return render(request, template, {
        'form': form,
        'title': 'Créer une Période de Rotation',
        'is_htmx': request.headers.get('HX-Request'),
        'plan_id': plan_id
    })


@admin_required
@transaction.atomic
def rotation_period_edit(request, pk):
    """Edit existing rotation period"""
    period = get_object_or_404(RotationPeriod, pk=pk)
    
    if request.method == 'POST':
        form = RotationPeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            messages.success(request, f'Période de rotation modifiée avec succès.')
            if request.headers.get('HX-Request'):
                plan_id = period.daily_rotation_plan.pk
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Période de rotation modifiée avec succès.</div>'
                    f'<script>setTimeout(() => {{ document.getElementById("period-modal").style.display = "none"; refreshPlanPeriods({plan_id}); }}, 1000)</script>'
                )
            return redirect('rotation_period_list')
        # If form is invalid and it's an HTMX request, return the form with errors
        elif request.headers.get('HX-Request'):
            template = 'core/rotation_periods/rotation_period_form_htmx.html'
            return render(request, template, {
                'form': form,
                'period': period,
                'title': f'Modifier la période',
                'is_htmx': True
            })
    else:
        form = RotationPeriodForm(instance=period)
    
    template = 'core/rotation_periods/rotation_period_form_htmx.html' if request.headers.get('HX-Request') else 'core/rotation_periods/rotation_period_form.html'
    return render(request, template, {
        'form': form,
        'period': period,
        'title': f'Modifier la période',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
@require_http_methods(["POST", "DELETE"])
@transaction.atomic
def rotation_period_delete(request, pk):
    """Delete rotation period"""
    period = get_object_or_404(RotationPeriod, pk=pk)
    plan_designation = period.daily_rotation_plan.designation
    plan_id = period.daily_rotation_plan.pk
    period.delete()
    
    if request.headers.get('HX-Request'):
        # Return updated period list with same filters and sorting
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort', 'start_date')
        order = request.GET.get('order', 'asc')
        plan_filter = request.GET.get('plan_filter', '')
        
        periods = RotationPeriod.objects.select_related('daily_rotation_plan', 'daily_rotation_plan__schedule_type').all()
        
        # Filter by plan if specified
        if plan_filter:
            periods = periods.filter(daily_rotation_plan_id=plan_filter)
            
        if search_query:
            periods = periods.filter(
                Q(daily_rotation_plan__designation__icontains=search_query)
            )
        
        # Apply same sorting
        valid_sorts = ['start_date', 'end_date', 'start_time', 'end_time', 'daily_rotation_plan__designation']
        if sort_by in valid_sorts:
            if order == 'desc':
                sort_by = f'-{sort_by}'
            periods = periods.order_by(sort_by)
        else:
            periods = periods.order_by('start_date', 'start_time')
        
        paginator = Paginator(periods, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get plans for filter dropdown
        plans = DailyRotationPlan.objects.all().order_by('designation')
        
        messages.success(request, f'Période de rotation supprimée avec succès.')
        return render(request, 'core/rotation_periods/rotation_period_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': request.GET.get('sort', 'start_date'),
            'current_order': request.GET.get('order', 'asc'),
            'plan_filter': plan_filter,
            'plans': plans
        })
    
    messages.success(request, f'Période de rotation supprimée avec succès.')
    # For periods accessed from plan detail, redirect back to plan
    if plan_id:
        return redirect('daily_rotation_plan_detail', pk=plan_id)
    return redirect('rotation_period_list')


# Count views for dashboard
@admin_required
def daily_rotation_plan_count(request):
    """HTMX endpoint for daily rotation plan count"""
    count = DailyRotationPlan.objects.count()
    return HttpResponse(f'<p class="text-2xl font-semibold text-gray-900" id="plan-count">{count}</p>')


@admin_required
def rotation_period_count(request):
    """HTMX endpoint for rotation period count"""
    count = RotationPeriod.objects.count()
    return HttpResponse(f'<p class="text-2xl font-semibold text-gray-900" id="period-count">{count}</p>')


# API Views
@admin_required
def api_daily_rotation_plans(request):
    """API endpoint to get all daily rotation plans"""
    plans = DailyRotationPlan.objects.all().order_by('designation')
    
    plans_data = []
    for plan in plans:
        plans_data.append({
            'id': plan.id,
            'designation': plan.designation,
            'description': plan.description or '',
            'short_name': plan.designation[:10] + '...' if len(plan.designation) > 10 else plan.designation
        })
    
    return JsonResponse({'plans': plans_data})

@login_required
@admin_required
@require_http_methods(["POST"])
def api_assign_daily_plan(request, week_id, weekday):
    """API endpoint to directly assign a daily plan"""
    week = get_object_or_404(ShiftScheduleWeek, id=week_id)
    
    try:
        plan_id = request.POST.get('plan_id')
        if not plan_id:
            return JsonResponse({'error': 'Plan ID is required'}, status=400)
        
        plan = get_object_or_404(DailyRotationPlan, id=plan_id)
        
        with transaction.atomic():
            # Check if daily plan already exists for this week/weekday
            daily_plan, created = ShiftScheduleDailyPlan.objects.get_or_create(
                week=week,
                weekday=weekday,
                defaults={'daily_rotation_plan': plan}
            )
            
            if not created:
                # Update existing plan
                daily_plan.daily_rotation_plan = plan
                daily_plan.save()
                action = 'modifié'
            else:
                action = 'créé'
        
        weekday_names = {1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi', 5: 'Vendredi', 6: 'Samedi', 7: 'Dimanche'}
        weekday_name = weekday_names.get(weekday, f'Jour {weekday}')
        
        return JsonResponse({
            'success': True,
            'message': f'Plan quotidien pour {weekday_name} {action} avec succès.',
            'daily_plan': {
                'id': daily_plan.id,
                'plan_name': plan.designation,
                'short_name': plan.designation[:10] + '...' if len(plan.designation) > 10 else plan.designation
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@admin_required
def api_plan_periods(request, plan_id):
    """API endpoint to get periods for a specific plan"""
    plan = get_object_or_404(DailyRotationPlan, pk=plan_id)
    periods = plan.periods.all().order_by('start_date', 'start_time')
    
    periods_data = []
    for period in periods:
        periods_data.append({
            'id': period.pk,
            'date_range': f"{period.start_date.strftime('%d/%m/%Y')} - {period.end_date.strftime('%d/%m/%Y')}",
            'duration_text': f"{(period.end_date - period.start_date).days + 1} jours",
            'time_range': f"{period.start_time.strftime('%H:%M')} - {period.end_time.strftime('%H:%M')}",
            'is_night_shift': period.is_night_shift(),
            'shift_type': 'Équipe de nuit' if period.is_night_shift() else 'Équipe de jour',
            'duration_hours': f"{period.get_duration_hours():.1f}",
            'is_active': period.is_active(),
            'status_text': 'Actif' if period.is_active() else 'Expiré',
        })
    
    return JsonResponse({
        'periods': periods_data,
        'count': len(periods_data)
    })


@admin_required
def api_shift_schedule_periods(request, schedule_id):
    """API endpoint to get periods for a specific shift schedule"""
    schedule = get_object_or_404(ShiftSchedule, pk=schedule_id)
    periods = schedule.periods.all().order_by('start_date')
    
    periods_data = []
    for period in periods:
        # Calculate duration in days
        duration_days = (period.end_date - period.start_date).days + 1
        
        # Check if period is active (end date is today or in the future)
        from django.utils import timezone
        today = timezone.now().date()
        is_active = period.end_date >= today
        
        periods_data.append({
            'id': period.pk,
            'schedule_id': period.shift_schedule.pk,
            'date_range': f"{period.start_date.strftime('%d/%m/%Y')} - {period.end_date.strftime('%d/%m/%Y')}",
            'duration_text': f"{duration_days} jours",
            'duration_days': duration_days,
            'is_active': is_active,
            'status_text': 'Actif' if is_active else 'Expiré',
            'weeks_count': period.weeks.count(),
        })
    
    return JsonResponse({
        'periods': periods_data,
        'count': len(periods_data)
    })


@admin_required
def api_shift_schedule_period_weeks(request, period_id):
    """API endpoint to get weeks for a specific shift schedule period"""
    period = get_object_or_404(ShiftSchedulePeriod, pk=period_id)
    weeks = period.weeks.all().order_by('week_number')
    
    weeks_data = []
    for week in weeks:
        # Get daily plans for this week, organized by weekday (supporting multiple plans per day)
        daily_plans_by_weekday = {}
        for daily_plan in week.daily_plans.all():
            weekday = daily_plan.weekday
            if weekday not in daily_plans_by_weekday:
                daily_plans_by_weekday[weekday] = []
            
            daily_plans_by_weekday[weekday].append({
                'id': daily_plan.pk,
                'short_name': daily_plan.daily_rotation_plan.designation[:3] if daily_plan.daily_rotation_plan else '?',
                'full_name': daily_plan.daily_rotation_plan.designation if daily_plan.daily_rotation_plan else 'Non défini',
                'designation': daily_plan.daily_rotation_plan.designation if daily_plan.daily_rotation_plan else 'Non défini',
                'description': daily_plan.daily_rotation_plan.description if daily_plan.daily_rotation_plan else '',
                'weekday': daily_plan.weekday,
                'plan_id': daily_plan.daily_rotation_plan.id if daily_plan.daily_rotation_plan else None,
                'schedule_type_color': daily_plan.daily_rotation_plan.schedule_type.color if daily_plan.daily_rotation_plan and daily_plan.daily_rotation_plan.schedule_type else '#6B7280',
            })
        
        weeks_data.append({
            'id': week.pk,
            'week_number': week.week_number,
            'daily_plans_count': week.daily_plans.count(),
            'daily_plans': daily_plans_by_weekday,  # Now contains arrays of plans per weekday
            'date_range': f"Semaine {week.week_number}",
        })
    
    return JsonResponse({
        'weeks': weeks_data,
        'count': len(weeks_data)
    })


# Shift Schedule Views

@login_required
@admin_required
def shift_schedule_list(request):
    """Display paginated list of shift schedules with search and filtering"""
    # Get search parameters
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    
    # Build query
    schedules = ShiftSchedule.objects.all()
    
    if search_query:
        schedules = schedules.filter(
            Q(name__icontains=search_query)
        )
    
    if type_filter:
        schedules = schedules.filter(type=type_filter)
    
    # Order by name
    schedules = schedules.order_by('name')
    
    # Pagination
    paginator = Paginator(schedules, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'type_choices': ShiftSchedule.TYPE_CHOICES,
        'current_agent': get_agent_from_user(request.user),
    }
    
    return render(request, 'core/shift_schedules/shift_schedule_list.html', context)


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def shift_schedule_create(request):
    """Create a new shift schedule"""
    if request.method == 'POST':
        form = ShiftScheduleForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                schedule = form.save()
                messages.success(request, f'Planning de poste "{schedule.name}" créé avec succès.')
                if request.headers.get('HX-Request'):
                    return HttpResponse("""
                        <script>
                            document.getElementById('schedule-modal').style.display = 'none';
                            location.reload();
                        </script>
                    """)
                return redirect('shift_schedule_list')
        # If form is invalid and it's an HTMX request, return the form with errors
        elif request.headers.get('HX-Request'):
            return render(request, 'core/shift_schedules/shift_schedule_form_htmx.html', {
                'form': form,
                'schedule': None
            })
    else:
        form = ShiftScheduleForm()
    
    return render(request, 'core/shift_schedules/shift_schedule_form_htmx.html', {
        'form': form,
        'schedule': None
    })


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def shift_schedule_edit(request, schedule_id):
    """Edit an existing shift schedule"""
    schedule = get_object_or_404(ShiftSchedule, id=schedule_id)
    
    if request.method == 'POST':
        form = ShiftScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            with transaction.atomic():
                schedule = form.save()
                messages.success(request, f'Planning de poste "{schedule.name}" modifié avec succès.')
                if request.headers.get('HX-Request'):
                    return HttpResponse("""
                        <script>
                            document.getElementById('schedule-modal').style.display = 'none';
                            location.reload();
                        </script>
                    """)
                return redirect('shift_schedule_list')
        # If form is invalid and it's an HTMX request, return the form with errors
        elif request.headers.get('HX-Request'):
            return render(request, 'core/shift_schedules/shift_schedule_form_htmx.html', {
                'form': form,
                'schedule': schedule
            })
    else:
        form = ShiftScheduleForm(instance=schedule)
    
    return render(request, 'core/shift_schedules/shift_schedule_form_htmx.html', {
        'form': form,
        'schedule': schedule
    })


@login_required
@admin_required
@require_http_methods(["POST"])
def shift_schedule_delete(request, schedule_id):
    """Delete a shift schedule"""
    schedule = get_object_or_404(ShiftSchedule, id=schedule_id)
    schedule_name = schedule.name
    
    with transaction.atomic():
        schedule.delete()
        messages.success(request, f'Planning de poste "{schedule_name}" supprimé avec succès.')
    
    return redirect('shift_schedule_list')




# Shift Schedule Period Views

@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def shift_schedule_period_create(request, schedule_id):
    """Create a new period for a shift schedule"""
    schedule = get_object_or_404(ShiftSchedule, id=schedule_id)
    
    if request.method == 'POST':
        form = ShiftSchedulePeriodForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                period = form.save(commit=False)
                period.shift_schedule = schedule
                period.save()
                
                if request.headers.get('HX-Request'):
                    return HttpResponse("""
                        <script>
                            document.getElementById('period-modal').style.display = 'none';
                            if (typeof refreshSchedulePeriods === 'function') {
                                refreshSchedulePeriods(%d);
                            }
                        </script>
                    """ % (schedule.id))
                
                messages.success(request, f'Période créée avec succès pour "{schedule.name}".')
                return redirect('shift_schedule_list')
    else:
        form = ShiftSchedulePeriodForm(initial={'shift_schedule': schedule})
        form.fields['shift_schedule'].widget = forms.HiddenInput()
    
    return render(request, 'core/shift_schedules/shift_schedule_period_form_htmx.html', {
        'form': form,
        'schedule': schedule,
        'period': None,
        'current_agent': get_agent_from_user(request.user),
    })


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def shift_schedule_period_edit(request, period_id):
    """Edit an existing shift schedule period"""
    period = get_object_or_404(ShiftSchedulePeriod, id=period_id)
    
    if request.method == 'POST':
        form = ShiftSchedulePeriodForm(request.POST, instance=period)
        if form.is_valid():
            with transaction.atomic():
                period = form.save()
                
                if request.headers.get('HX-Request'):
                    return HttpResponse("""
                        <script>
                            document.getElementById('period-modal').style.display = 'none';
                            location.reload();
                        </script>
                    """)
                
                messages.success(request, f'Période modifiée avec succès.')
                return redirect('shift_schedule_list')
        else:
            # Form has validation errors - return the form with errors for HTMX
            if request.headers.get('HX-Request'):
                return render(request, 'core/shift_schedules/shift_schedule_period_form_htmx.html', {
                    'form': form,
                    'schedule': period.shift_schedule,
                    'period': period,
                    'current_agent': get_agent_from_user(request.user),
                })
    else:
        form = ShiftSchedulePeriodForm(instance=period)
        form.fields['shift_schedule'].widget = forms.HiddenInput()
    
    return render(request, 'core/shift_schedules/shift_schedule_period_form_htmx.html', {
        'form': form,
        'schedule': period.shift_schedule,
        'period': period,
        'current_agent': get_agent_from_user(request.user),
    })


@login_required
@admin_required
@require_http_methods(["POST"])
def shift_schedule_period_delete(request, period_id):
    """Delete a shift schedule period"""
    period = get_object_or_404(ShiftSchedulePeriod, id=period_id)
    schedule = period.shift_schedule
    
    with transaction.atomic():
        period.delete()
        messages.success(request, f'Période supprimée avec succès.')
    
    # For HTMX requests (frontend fetch), return empty success response to allow frontend refresh
    if request.headers.get('HX-Request') or 'application/json' in request.headers.get('Accept', ''):
        return HttpResponse('', status=200)
    
    return redirect('shift_schedule_list')


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def shift_schedule_period_duplicate(request, period_id):
    """Duplicate a shift schedule period with all its weeks and daily plans"""
    original_period = get_object_or_404(ShiftSchedulePeriod, id=period_id)
    
    if request.method == 'POST':
        form = ShiftSchedulePeriodForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create new period with new dates
                new_period = form.save(commit=False)
                new_period.shift_schedule = original_period.shift_schedule
                new_period.save()
                
                # Copy all weeks from original period
                original_weeks = original_period.weeks.all().order_by('week_number')
                for original_week in original_weeks:
                    # Create new week
                    new_week = ShiftScheduleWeek.objects.create(
                        period=new_period,
                        week_number=original_week.week_number
                    )
                    
                    # Copy all daily plans from original week
                    original_daily_plans = original_week.daily_plans.all()
                    for original_daily_plan in original_daily_plans:
                        ShiftScheduleDailyPlan.objects.create(
                            week=new_week,
                            weekday=original_daily_plan.weekday,
                            daily_rotation_plan=original_daily_plan.daily_rotation_plan
                        )
                
                if request.headers.get('HX-Request'):
                    return HttpResponse(f"""
                        <script>
                            document.getElementById('period-modal').style.display = 'none';
                            if (typeof refreshSchedulePeriods === 'function') {{
                                refreshSchedulePeriods({original_period.shift_schedule.id});
                            }}
                        </script>
                    """)
                
                messages.success(request, f'Période dupliquée avec succès avec {original_weeks.count()} semaines.')
                return redirect('shift_schedule_list')
    else:
        # Pre-fill form with original period data but empty dates for user to set
        initial_data = {
            'shift_schedule': original_period.shift_schedule,
            'start_date': '',  # User must set new dates
            'end_date': ''
        }
        form = ShiftSchedulePeriodForm(initial=initial_data)
        form.fields['shift_schedule'].widget = forms.HiddenInput()
    
    return render(request, 'core/shift_schedules/shift_schedule_period_duplicate_form_htmx.html', {
        'form': form,
        'original_period': original_period,
        'schedule': original_period.shift_schedule,
        'current_agent': get_agent_from_user(request.user),
    })




# Shift Schedule Week Views

@login_required
@admin_required
@require_http_methods(["POST"])
def shift_schedule_week_create(request, period_id):
    """Create a new week for a shift schedule period instantly"""
    period = get_object_or_404(ShiftSchedulePeriod, id=period_id)
    
    with transaction.atomic():
        # Auto-generate next week number
        existing_weeks = period.weeks.all()
        next_week_number = existing_weeks.count() + 1
        
        # Create the week directly
        week = ShiftScheduleWeek.objects.create(
            period=period,
            week_number=next_week_number
        )
        
        # Handle HTMX requests - return the period ID
        if request.headers.get('HX-Request'):
            return HttpResponse(str(period.id), status=200)
        
        messages.success(request, f'Semaine S{week.week_number} créée avec succès.')
        return redirect('shift_schedule_list')


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def shift_schedule_week_edit(request, week_id):
    """Edit an existing shift schedule week"""
    week = get_object_or_404(ShiftScheduleWeek, id=week_id)
    
    if request.method == 'POST':
        form = ShiftScheduleWeekForm(request.POST, instance=week)
        if form.is_valid():
            with transaction.atomic():
                week = form.save()
                messages.success(request, f'Semaine {week.week_number} modifiée avec succès.')
                
                # Handle HTMX requests
                if request.headers.get('HX-Request'):
                    return HttpResponse("""
                        <script>
                            document.getElementById('week-modal').style.display = 'none';
                            // Refresh the period weeks if we're in the list view
                            if (typeof refreshPeriodWeeks === 'function') {
                                refreshPeriodWeeks(%d);
                            }
                            // Show success message
                            if (typeof showSuccessMessage === 'function') {
                                showSuccessMessage('Semaine %d modifiée avec succès.');
                            }
                        </script>
                    """ % (week.period.id, week.week_number))
                
                return redirect('shift_schedule_period_detail', period_id=week.period.id)
    else:
        form = ShiftScheduleWeekForm(instance=week)
        form.fields['period'].widget = forms.HiddenInput()
    
    return render(request, 'core/shift_schedules/shift_schedule_week_form_htmx.html', {
        'form': form,
        'period': week.period,
        'week': week,
        'current_agent': get_agent_from_user(request.user),
    })


@login_required
@admin_required
@require_http_methods(["POST"])
def shift_schedule_week_delete(request, week_id):
    """Delete a shift schedule week and renumber remaining weeks"""
    week = get_object_or_404(ShiftScheduleWeek, id=week_id)
    period = week.period
    schedule = period.shift_schedule
    deleted_week_number = week.week_number
    
    with transaction.atomic():
        # Delete the week
        week.delete()
        
        # Renumber all remaining weeks in this period that come after the deleted week
        remaining_weeks = period.weeks.filter(week_number__gt=deleted_week_number).order_by('week_number')
        for remaining_week in remaining_weeks:
            remaining_week.week_number -= 1
            remaining_week.save(update_fields=['week_number'])
        
        messages.success(request, f'Semaine {deleted_week_number} supprimée avec succès. Les semaines suivantes ont été renumérotées.')
    
    # For HTMX requests (frontend fetch), return empty success response to allow frontend refresh
    if request.headers.get('HX-Request') or 'application/json' in request.headers.get('Accept', ''):
        return HttpResponse('', status=200)
    
    return redirect('shift_schedule_list')


@login_required
@admin_required
@require_http_methods(["POST"])
def shift_schedule_week_duplicate(request, week_id):
    """Duplicate a shift schedule week with all its daily plans instantly"""
    original_week = get_object_or_404(ShiftScheduleWeek, id=week_id)
    
    with transaction.atomic():
        # Duplicate to the same period and calculate next week number
        target_period = original_week.period
        existing_weeks = ShiftScheduleWeek.objects.filter(period=target_period)
        next_week_number = existing_weeks.count() + 1
        
        # Create new week
        new_week = ShiftScheduleWeek.objects.create(
            period=target_period,
            week_number=next_week_number
        )
        
        # Copy all daily plans from original week
        original_daily_plans = original_week.daily_plans.all()
        for original_daily_plan in original_daily_plans:
            ShiftScheduleDailyPlan.objects.create(
                week=new_week,
                weekday=original_daily_plan.weekday,
                daily_rotation_plan=original_daily_plan.daily_rotation_plan
            )
        
        if request.headers.get('HX-Request'):
            return HttpResponse(str(target_period.id), status=200)
        
        messages.success(request, f'Semaine S{original_week.week_number} dupliquée avec succès comme S{next_week_number} avec {original_daily_plans.count()} rythmes quotidiens.')
        return redirect('shift_schedule_list')




# Shift Schedule Daily Plan Views

@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def shift_schedule_daily_plan_create(request, week_id, weekday):
    """Create or update daily plans for a week"""
    week = get_object_or_404(ShiftScheduleWeek, id=week_id)
    
    if request.method == 'POST':
        form = ShiftScheduleDailyPlanForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                daily_plan = form.save(commit=False)
                daily_plan.week = week
                daily_plan.weekday = weekday
                daily_plan.save()
                
                if request.headers.get('HX-Request'):
                    period_id = week.period.id
                    return HttpResponse(f"""
                        <script>
                            // Close modal immediately
                            document.getElementById('daily-plan-modal').style.display = 'none';
                            // Refresh the weeks data for the specific period to show the new rhythm
                            fetch('/api/shift-schedule-periods/{period_id}/weeks/')
                                .then(response => response.json())
                                .then(data => {{
                                    // Find the Alpine.js component for this specific period and update its weeks data
                                    const periodElements = document.querySelectorAll('[x-data]');
                                    for (let element of periodElements) {{
                                        if (element._x_dataStack && element._x_dataStack[0].periodId === {period_id}) {{
                                            const alpineData = element._x_dataStack[0];
                                            alpineData.weeks = data.weeks;
                                            alpineData.weeksLoaded = true;
                                            break;
                                        }}
                                    }}
                                }})
                                .catch(error => {{
                                    console.error('Error refreshing weeks:', error);
                                    // Fallback: reload the page if API call fails
                                    location.reload();
                                }});
                        </script>
                    """)
                
                weekday_name = daily_plan.get_weekday_display_french()
                messages.success(request, f'Plan quotidien pour {weekday_name} créé avec succès.')
                return redirect('shift_schedule_list')
        else:
            # Form has validation errors - return the form with errors for HTMX
            if request.headers.get('HX-Request'):
                return render(request, 'core/shift_schedules/shift_schedule_daily_plan_form_htmx.html', {
                    'form': form,
                    'week': week,
                    'daily_plan': None,
                    'weekday': weekday,
                    'current_agent': get_agent_from_user(request.user),
                })
    else:
        form = ShiftScheduleDailyPlanForm(initial={'week': week, 'weekday': weekday})
        form.fields['week'].widget = forms.HiddenInput()
        form.fields['weekday'].widget = forms.HiddenInput()
    
    return render(request, 'core/shift_schedules/shift_schedule_daily_plan_form_htmx.html', {
        'form': form,
        'week': week,
        'daily_plan': None,
        'weekday': weekday,
        'current_agent': get_agent_from_user(request.user),
    })


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def shift_schedule_daily_plan_edit(request, daily_plan_id):
    """Edit an existing daily plan"""
    daily_plan = get_object_or_404(ShiftScheduleDailyPlan, id=daily_plan_id)
    
    if request.method == 'POST':
        form = ShiftScheduleDailyPlanForm(request.POST, instance=daily_plan)
        if form.is_valid():
            with transaction.atomic():
                daily_plan = form.save()
                weekday_name = daily_plan.get_weekday_display_french()
                messages.success(request, f'Plan quotidien pour {weekday_name} modifié avec succès.')
                return redirect('shift_schedule_list')
    else:
        form = ShiftScheduleDailyPlanForm(instance=daily_plan)
        form.fields['week'].widget = forms.HiddenInput()
    
    return render(request, 'core/shift_schedules/shift_schedule_daily_plan_form_htmx.html', {
        'form': form,
        'week': daily_plan.week,
        'daily_plan': daily_plan,
        'current_agent': get_agent_from_user(request.user),
    })


@login_required
@admin_required
@require_http_methods(["POST"])
def shift_schedule_daily_plan_delete(request, daily_plan_id):
    """Delete a daily plan"""
    daily_plan = get_object_or_404(ShiftScheduleDailyPlan, id=daily_plan_id)
    week = daily_plan.week
    period_id = week.period.id
    weekday_name = daily_plan.get_weekday_display_french()
    
    with transaction.atomic():
        daily_plan.delete()
        messages.success(request, f'Plan quotidien pour {weekday_name} supprimé avec succès.')
    
    if request.headers.get('HX-Request') or request.headers.get('Accept') == 'application/json':
        # Return JSON response with period ID for targeted refresh
        return JsonResponse({
            'success': True,
            'period_id': period_id,
            'message': f'Plan quotidien pour {weekday_name} supprimé avec succès.'
        })
    
    return redirect('shift_schedule_list')


# Public Holiday Views
@admin_required
def public_holiday_list(request):
    """List all public holidays with search, sorting and pagination"""
    from django.db.models import Count
    from django.db.models.functions import Extract
    
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'asc')
    
    holidays = PublicHoliday.objects.all()
    
    if search_query:
        holidays = holidays.filter(
            Q(designation__icontains=search_query) |
            Q(date__icontains=search_query)
        )
    
    # Apply sorting with automatic year sorting when sorting by date
    valid_sorts = ['designation', 'date']
    if sort_by in valid_sorts:
        if sort_by == 'date':
            # Sort by year first, then by date within year
            if order == 'desc':
                holidays = holidays.order_by('-date__year', '-date')
            else:
                holidays = holidays.order_by('date__year', 'date')
        else:
            if order == 'desc':
                sort_by = f'-{sort_by}'
            holidays = holidays.order_by(sort_by)
    else:
        holidays = holidays.order_by('date__year', 'date')
    
    # Get count by year for display
    holidays_by_year = PublicHoliday.objects.values(
        year=Extract('date', 'year')
    ).annotate(
        count=Count('id')
    ).order_by('-year')
    
    paginator = Paginator(holidays, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'date')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/public_holidays/public_holiday_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order,
            'holidays_by_year': holidays_by_year
        })
    
    return render(request, 'core/public_holidays/public_holiday_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_sort': current_sort,
        'current_order': current_order,
        'holidays_by_year': holidays_by_year
    })


@admin_required
def public_holiday_create(request):
    """Create new public holiday"""
    if request.method == 'POST':
        form = PublicHolidayForm(request.POST)
        if form.is_valid():
            holiday = form.save()
            messages.success(request, f'Jour férié "{holiday.designation}" créé avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Jour férié "{holiday.designation}" créé avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("public-holiday-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('public_holiday_list')
    else:
        form = PublicHolidayForm()
    
    template = 'core/public_holidays/public_holiday_form_htmx.html' if request.headers.get('HX-Request') else 'core/public_holidays/public_holiday_form.html'
    return render(request, template, {
        'form': form,
        'title': 'Créer un Jour Férié',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
def public_holiday_detail(request, pk):
    """Public holiday detail view"""
    holiday = get_object_or_404(PublicHoliday, pk=pk)
    return render(request, 'core/public_holidays/public_holiday_detail.html', {'holiday': holiday})


@admin_required
def public_holiday_edit(request, pk):
    """Edit existing public holiday"""
    holiday = get_object_or_404(PublicHoliday, pk=pk)
    
    if request.method == 'POST':
        form = PublicHolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(request, f'Jour férié "{holiday.designation}" modifié avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Jour férié "{holiday.designation}" modifié avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("public-holiday-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('public_holiday_list')
    else:
        form = PublicHolidayForm(instance=holiday)
    
    template = 'core/public_holidays/public_holiday_form_htmx.html' if request.headers.get('HX-Request') else 'core/public_holidays/public_holiday_form.html'
    return render(request, template, {
        'form': form,
        'holiday': holiday,
        'title': f'Modifier "{holiday.designation}"',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
@require_http_methods(["DELETE"])
def public_holiday_delete(request, pk):
    """Delete public holiday"""
    from django.db.models import Count
    from django.db.models.functions import Extract
    
    holiday = get_object_or_404(PublicHoliday, pk=pk)
    designation = holiday.designation
    holiday.delete()
    
    if request.headers.get('HX-Request'):
        # Return updated holiday list with same filters and sorting
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort', 'date')
        order = request.GET.get('order', 'asc')
        
        holidays = PublicHoliday.objects.all()
            
        if search_query:
            holidays = holidays.filter(
                Q(designation__icontains=search_query) |
                Q(date__icontains=search_query)
            )
        
        # Apply sorting with automatic year sorting when sorting by date
        valid_sorts = ['designation', 'date']
        if sort_by in valid_sorts:
            if sort_by == 'date':
                # Sort by year first, then by date within year
                if order == 'desc':
                    holidays = holidays.order_by('-date__year', '-date')
                else:
                    holidays = holidays.order_by('date__year', 'date')
            else:
                if order == 'desc':
                    sort_by = f'-{sort_by}'
                holidays = holidays.order_by(sort_by)
        else:
            holidays = holidays.order_by('date__year', 'date')
        
        # Get count by year for display
        holidays_by_year = PublicHoliday.objects.values(
            year=Extract('date', 'year')
        ).annotate(
            count=Count('id')
        ).order_by('-year')
        
        paginator = Paginator(holidays, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'core/public_holidays/public_holiday_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': request.GET.get('sort', 'date'),
            'current_order': request.GET.get('order', 'asc'),
            'holidays_by_year': holidays_by_year,
            'success_message': f'Jour férié "{designation}" supprimé avec succès.'
        })
    
    messages.success(request, f'Jour férié "{designation}" supprimé avec succès.')
    return redirect('public_holiday_list')


@admin_required
def public_holiday_duplicate(request, pk):
    """Duplicate public holiday with same name but different date"""
    original_holiday = get_object_or_404(PublicHoliday, pk=pk)
    
    if request.method == 'POST':
        form = PublicHolidayForm(request.POST)
        if form.is_valid():
            new_holiday = form.save()
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Jour férié "{new_holiday.designation}" dupliqué avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("public-holiday-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('public_holiday_list')
    else:
        # Pre-populate form with original holiday's data but clear the date
        form = PublicHolidayForm(initial={
            'designation': original_holiday.designation,
            'date': None  # User must set a new date
        })
    
    template = 'core/public_holidays/public_holiday_form_htmx.html' if request.headers.get('HX-Request') else 'core/public_holidays/public_holiday_form.html'
    return render(request, template, {
        'form': form,
        'title': f'Dupliquer "{original_holiday.designation}"',
        'is_htmx': request.headers.get('HX-Request'),
        'is_duplicate': True
    })


@admin_required
def public_holiday_count(request):
    """HTMX endpoint for public holiday count"""
    count = PublicHoliday.objects.count()
    return HttpResponse(f'<p class="text-2xl font-semibold text-gray-900" id="public-holiday-count">{count}</p>')


# Department Views
@admin_required
def department_count(request):
    """HTMX endpoint for department count"""
    count = Department.objects.count()
    return HttpResponse(f'<p class="text-2xl font-semibold text-gray-900" id="department-count">{count}</p>')


@admin_required
def department_list(request):
    """List all departments with search, sorting and pagination"""
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'order')
    order = request.GET.get('order', 'asc')
    
    departments = Department.objects.all()
    
    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query)
        )
    
    # Apply sorting
    valid_sorts = ['name', 'order']
    if sort_by in valid_sorts:
        if order == 'desc':
            sort_by = f'-{sort_by}'
        departments = departments.order_by(sort_by)
    else:
        departments = departments.order_by('order', 'name')
    
    paginator = Paginator(departments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'order')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/departments/department_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order
        })
    
    return render(request, 'core/departments/department_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_sort': current_sort,
        'current_order': current_order
    })


@admin_required
def department_create(request):
    """Create new department"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Département "{department.name}" créé avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Département "{department.name}" créé avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("department-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('department_list')
    else:
        form = DepartmentForm()
    
    template = 'core/departments/department_form_htmx.html' if request.headers.get('HX-Request') else 'core/departments/department_form.html'
    return render(request, template, {
        'form': form,
        'title': 'Créer un Département',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
def department_detail(request, pk):
    """Department detail view"""
    department = get_object_or_404(Department, pk=pk)
    return render(request, 'core/departments/department_detail.html', {'department': department})


@admin_required
def department_edit(request, pk):
    """Edit existing department"""
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f'Département "{department.name}" modifié avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Département "{department.name}" modifié avec succès.</div>'
                    '<script>setTimeout(() => { document.getElementById("department-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                )
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    
    template = 'core/departments/department_form_htmx.html' if request.headers.get('HX-Request') else 'core/departments/department_form.html'
    return render(request, template, {
        'form': form,
        'department': department,
        'title': f'Modifier "{department.name}"',
        'is_htmx': request.headers.get('HX-Request')
    })


@admin_required
@require_http_methods(["DELETE"])
def department_delete(request, pk):
    """Delete department"""
    department = get_object_or_404(Department, pk=pk)
    name = department.name
    department.delete()
    
    if request.headers.get('HX-Request'):
        # Return updated department list with same filters and sorting
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort', 'order')
        order = request.GET.get('order', 'asc')
        
        departments = Department.objects.all()
            
        if search_query:
            departments = departments.filter(
                Q(name__icontains=search_query)
            )
        
        # Apply same sorting
        valid_sorts = ['name', 'order']
        if sort_by in valid_sorts:
            if order == 'desc':
                sort_by = f'-{sort_by}'
            departments = departments.order_by(sort_by)
        else:
            departments = departments.order_by('order', 'name')
        
        paginator = Paginator(departments, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'core/departments/department_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query,
            'current_sort': request.GET.get('sort', 'order'),
            'current_order': request.GET.get('order', 'asc'),
            'success_message': f'Département "{name}" supprimé avec succès.'
        })
    
    messages.success(request, f'Département "{name}" supprimé avec succès.')
    return redirect('department_list')
