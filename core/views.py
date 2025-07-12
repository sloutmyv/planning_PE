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
                     ShiftSchedule, ShiftSchedulePeriod, ShiftScheduleWeek, ShiftScheduleDailyPlan)
from .forms import (AgentForm, FunctionForm, ScheduleTypeForm, DailyRotationPlanForm, RotationPeriodForm,
                    ShiftScheduleForm, ShiftSchedulePeriodForm, ShiftScheduleWeekForm, ShiftScheduleDailyPlanForm, WeeklyPlanFormSet)
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
                    f'<script>setTimeout(() => {{ document.getElementById("period-modal").style.display = "none"; refreshPlanPeriods({plan_id}); }}, 1000)</script>'
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
                    return HttpResponse(
                        f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Planning de poste "{schedule.name}" créé avec succès.</div>'
                        '<script>setTimeout(() => { document.getElementById("schedule-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                    )
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
                    return HttpResponse(
                        f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Planning de poste "{schedule.name}" modifié avec succès.</div>'
                        '<script>setTimeout(() => { document.getElementById("schedule-modal").style.display = "none"; location.reload(); }, 1000)</script>'
                    )
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


@login_required
@admin_required
def shift_schedule_detail(request, schedule_id):
    """Display shift schedule details with periods"""
    schedule = get_object_or_404(ShiftSchedule, id=schedule_id)
    periods = schedule.periods.all().order_by('start_date')
    
    context = {
        'schedule': schedule,
        'periods': periods,
        'current_agent': get_agent_from_user(request.user),
    }
    
    return render(request, 'core/shift_schedules/shift_schedule_detail.html', context)


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
                messages.success(request, f'Période créée avec succès pour "{schedule.name}".')
                return redirect('shift_schedule_detail', schedule_id=schedule.id)
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
                messages.success(request, f'Période modifiée avec succès.')
                return redirect('shift_schedule_detail', schedule_id=period.shift_schedule.id)
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
    
    return redirect('shift_schedule_detail', schedule_id=schedule.id)


@login_required
@admin_required
def shift_schedule_period_detail(request, period_id):
    """Display period details with weeks"""
    period = get_object_or_404(ShiftSchedulePeriod, id=period_id)
    weeks = period.weeks.all().order_by('week_number')
    
    context = {
        'period': period,
        'weeks': weeks,
        'current_agent': get_agent_from_user(request.user),
    }
    
    return render(request, 'core/shift_schedules/shift_schedule_period_detail.html', context)


# Shift Schedule Week Views

@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def shift_schedule_week_create(request, period_id):
    """Create a new week for a shift schedule period"""
    period = get_object_or_404(ShiftSchedulePeriod, id=period_id)
    
    if request.method == 'POST':
        form = ShiftScheduleWeekForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                week = form.save(commit=False)
                week.period = period
                week.save()
                messages.success(request, f'Semaine {week.week_number} créée avec succès.')
                return redirect('shift_schedule_period_detail', period_id=period.id)
    else:
        # Auto-generate next week number
        existing_weeks = period.weeks.all()
        next_week_number = existing_weeks.count() + 1
        form = ShiftScheduleWeekForm(initial={'period': period, 'week_number': next_week_number})
        form.fields['period'].widget = forms.HiddenInput()
    
    return render(request, 'core/shift_schedules/shift_schedule_week_form_htmx.html', {
        'form': form,
        'period': period,
        'week': None,
        'current_agent': get_agent_from_user(request.user),
    })


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
    """Delete a shift schedule week"""
    week = get_object_or_404(ShiftScheduleWeek, id=week_id)
    period = week.period
    
    with transaction.atomic():
        week.delete()
        messages.success(request, f'Semaine {week.week_number} supprimée avec succès.')
    
    return redirect('shift_schedule_period_detail', period_id=period.id)


@login_required
@admin_required
def shift_schedule_week_detail(request, week_id):
    """Display week details with daily plans"""
    week = get_object_or_404(ShiftScheduleWeek, id=week_id)
    daily_plans = week.daily_plans.all().order_by('weekday')
    
    # Create a list of weekdays with their plans
    weekday_data = []
    for weekday_num, weekday_name in ShiftScheduleDailyPlan.WEEKDAY_CHOICES:
        plan = daily_plans.filter(weekday=weekday_num).first()
        weekday_data.append({
            'weekday_num': weekday_num,
            'weekday_name': weekday_name,
            'plan': plan,
            'has_plan': plan is not None
        })
    
    # Get all rotation plans for the form
    rotation_plans = DailyRotationPlan.objects.all().order_by('designation')
    
    context = {
        'week': week,
        'daily_plans': daily_plans,
        'weekday_data': weekday_data,
        'rotation_plans': rotation_plans,
        'weekday_choices': ShiftScheduleDailyPlan.WEEKDAY_CHOICES,
        'current_agent': get_agent_from_user(request.user),
    }
    
    return render(request, 'core/shift_schedules/shift_schedule_week_detail.html', context)


# Shift Schedule Daily Plan Views

@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def shift_schedule_daily_plan_create(request, week_id):
    """Create or update daily plans for a week"""
    week = get_object_or_404(ShiftScheduleWeek, id=week_id)
    
    if request.method == 'POST':
        form = ShiftScheduleDailyPlanForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                daily_plan = form.save(commit=False)
                daily_plan.week = week
                daily_plan.save()
                weekday_name = daily_plan.get_weekday_display_french()
                messages.success(request, f'Plan quotidien pour {weekday_name} créé avec succès.')
                return redirect('shift_schedule_week_detail', week_id=week.id)
    else:
        form = ShiftScheduleDailyPlanForm(initial={'week': week})
        form.fields['week'].widget = forms.HiddenInput()
    
    return render(request, 'core/shift_schedules/shift_schedule_daily_plan_form_htmx.html', {
        'form': form,
        'week': week,
        'daily_plan': None,
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
                return redirect('shift_schedule_week_detail', week_id=daily_plan.week.id)
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
    weekday_name = daily_plan.get_weekday_display_french()
    
    with transaction.atomic():
        daily_plan.delete()
        messages.success(request, f'Plan quotidien pour {weekday_name} supprimé avec succès.')
    
    return redirect('shift_schedule_week_detail', week_id=week.id)
