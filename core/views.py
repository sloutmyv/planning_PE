from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.db import transaction
from django import forms
from django.core.serializers import serialize
from django.contrib.auth.models import User
from django.utils import timezone
import json
import datetime


def is_superuser(user):
    """Check if user is a superuser"""
    return user.is_authenticated and user.is_superuser
from .models import (Agent, Function, ScheduleType, DailyRotationPlan, RotationPeriod,
                     ShiftSchedule, ShiftSchedulePeriod, ShiftScheduleWeek, ShiftScheduleDailyPlan, PublicHoliday, Department, Team, TeamPosition, TeamPositionAgentAssignment, TeamPositionRotationAssignment)
from .forms import (AgentForm, FunctionForm, ScheduleTypeForm, DailyRotationPlanForm, RotationPeriodForm,
                    ShiftScheduleForm, ShiftSchedulePeriodForm, ShiftScheduleWeekForm, ShiftScheduleDailyPlanForm, WeeklyPlanFormSet, PublicHolidayForm, DepartmentForm, TeamForm, TeamPositionForm)
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


@admin_required
def user_manual(request):
    """User manual explaining how to use the application"""
    return render(request, 'core/user_manual.html')


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
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'matricule')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/agents/agent_list_partial.html', {
            'agents': agents,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order,
            'hide_departed': hide_departed
        })
    
    return render(request, 'core/agents/agent_list.html', {
        'agents': agents,
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
        
        messages.success(request, f'Agent {matricule} supprimé avec succès.')
        return render(request, 'core/agents/agent_list_partial.html', {
            'agents': agents,
            'search_query': search_query,
            'current_sort': request.GET.get('sort', 'matricule'),
            'current_order': request.GET.get('order', 'asc')
        })
    
    messages.success(request, f'Agent {matricule} supprimé avec succès.')
    return redirect('agent_list')


@user_passes_test(is_superuser)
def agent_export(request):
    """Export agents to JSON file - only accessible to superusers"""
    agents = Agent.objects.all()
    
    # Prepare data for export
    export_data = []
    for agent in agents:
        agent_data = {
            'matricule': agent.matricule,
            'first_name': agent.first_name,
            'last_name': agent.last_name,
            'grade': agent.grade,
            'hire_date': agent.hire_date.isoformat() if agent.hire_date else None,
            'departure_date': agent.departure_date.isoformat() if agent.departure_date else None,
            'permission_level': agent.permission_level,
            'password_changed': agent.password_changed,
            'created_at': agent.created_at.isoformat() if hasattr(agent, 'created_at') and agent.created_at else None,
            'updated_at': agent.updated_at.isoformat() if hasattr(agent, 'updated_at') and agent.updated_at else None,
        }
        export_data.append(agent_data)
    
    # Generate filename with current date (timezone-aware)
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_agents.json"
    
    # Create response
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def agent_import(request):
    """Import agents from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        confirm_overwrite = request.POST.get('confirm_overwrite', False)
        confirm_action = request.POST.get('confirm_action', False)
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('agent_list')
        
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('agent_list')
        
        if not confirm_overwrite or not confirm_action:
            messages.error(request, 'Confirmation requise pour remplacer la base de données.')
            return redirect('agent_list')
        
        try:
            # Read and parse JSON data
            file_content = import_file.read().decode('utf-8')
            import_data = json.loads(file_content)
            
            if not isinstance(import_data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste d\'agents.')
                return redirect('agent_list')
            
            # Count existing agents before deletion
            existing_count = Agent.objects.count()
            
            # STEP 1: Delete ALL existing agents and their user accounts
            messages.info(request, f'Suppression de {existing_count} agents existants...')
            
            # Get all agents with their user accounts
            agents_with_users = Agent.objects.select_related('user').all()
            deleted_users = 0
            preserved_superusers = []
            
            for agent in agents_with_users:
                if agent.user and agent.user.is_superuser:
                    # Preserve superuser info for recreation
                    preserved_superusers.append({
                        'matricule': agent.matricule,
                        'username': agent.user.username,
                        'email': agent.user.email,
                        'first_name': agent.user.first_name,
                        'last_name': agent.user.last_name,
                        'is_staff': agent.user.is_staff,
                        'is_superuser': agent.user.is_superuser,
                    })
                    # Delete the agent but keep the user account
                    agent.user = None
                    agent.save()
                    agent.delete()
                else:
                    # Delete both user and agent for non-superusers
                    if agent.user:
                        agent.user.delete()
                        deleted_users += 1
                    else:
                        agent.delete()
            
            # Delete any remaining agents (those without users)
            Agent.objects.all().delete()
            
            # Also delete any orphaned users that might have the same matricule as imported agents
            import_matricules = [agent_data.get('matricule') for agent_data in import_data if agent_data.get('matricule')]
            for matricule in import_matricules:
                # Delete any existing user with this matricule (except preserved superusers)
                preserved_usernames = [su['username'] for su in preserved_superusers]
                User.objects.filter(username=matricule).exclude(username__in=preserved_usernames).delete()
            
            # STEP 2: Import new agents
            imported_count = 0
            errors = []
            
            for agent_data in import_data:
                try:
                    matricule = agent_data.get('matricule')
                    if not matricule:
                        errors.append('Matricule manquant dans un enregistrement.')
                        continue
                    
                    # Check if this matricule corresponds to a preserved superuser
                    existing_superuser = None
                    for su in preserved_superusers:
                        if su['matricule'] == matricule:
                            existing_superuser = User.objects.get(username=su['username'])
                            break
                    
                    # Create new agent
                    agent = Agent.objects.create(
                        matricule=matricule,
                        first_name=agent_data.get('first_name', ''),
                        last_name=agent_data.get('last_name', ''),
                        grade=agent_data.get('grade', 'Agent'),
                        hire_date=datetime.datetime.fromisoformat(agent_data['hire_date']).date() if agent_data.get('hire_date') else timezone.now().date(),
                        departure_date=datetime.datetime.fromisoformat(agent_data['departure_date']).date() if agent_data.get('departure_date') else None,
                        permission_level=agent_data.get('permission_level', 'R'),
                        password_changed=False,  # Force password reset
                    )
                    
                    # If this is a preserved superuser, link them back
                    if existing_superuser:
                        agent.user = existing_superuser
                        agent.save()
                        # Update user info from import data
                        existing_superuser.first_name = agent.first_name
                        existing_superuser.last_name = agent.last_name
                        existing_superuser.save()
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f'Erreur pour l\'agent {matricule}: {str(e)}')
            
            # Show results
            messages.success(request, f'✅ Base de données remplacée avec succès!')
            messages.success(request, f'📊 {existing_count} agents supprimés, {imported_count} agents importés.')
            messages.warning(request, f'🔐 Tous les mots de passe ont été réinitialisés à "azerty".')
            
            if errors:
                messages.error(request, f'❌ {len(errors)} erreurs lors de l\'importation:')
                for error in errors[:3]:  # Show first 3 errors
                    messages.error(request, f'  • {error}')
                if len(errors) > 3:
                    messages.error(request, f'  • ... et {len(errors) - 3} autres erreurs.')
            
        except json.JSONDecodeError:
            messages.error(request, 'Le fichier JSON n\'est pas valide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation: {str(e)}')
    
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
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'designation')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/functions/function_list_partial.html', {
            'functions': functions,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order,
            'hide_inactive': hide_inactive
        })
    
    return render(request, 'core/functions/function_list.html', {
        'functions': functions,
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
        
        messages.success(request, f'Fonction "{designation}" supprimée avec succès.')
        return render(request, 'core/functions/function_list_partial.html', {
            'functions': functions,
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
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'designation')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/schedule_types/schedule_type_list_partial.html', {
            'schedule_types': schedule_types,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order
        })
    
    return render(request, 'core/schedule_types/schedule_type_list.html', {
        'schedule_types': schedule_types,
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
        
        messages.success(request, f'Type de planning "{designation}" supprimé avec succès.')
        return render(request, 'core/schedule_types/schedule_type_list_partial.html', {
            'schedule_types': schedule_types,
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
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'designation')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/daily_rotation_plans/daily_rotation_plan_list_partial.html', {
            'plans': plans,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order
        })
    
    return render(request, 'core/daily_rotation_plans/daily_rotation_plan_list.html', {
        'plans': plans,
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
        
        messages.success(request, f'Plan de rotation "{designation}" supprimé avec succès.')
        return render(request, 'core/daily_rotation_plans/daily_rotation_plan_list_partial.html', {
            'plans': plans,
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
    
    # Get plans for filter dropdown
    plans = DailyRotationPlan.objects.all().order_by('designation')
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'start_date')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/rotation_periods/rotation_period_list_partial.html', {
            'periods': periods,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order,
            'plan_filter': plan_filter,
            'plans': plans
        })
    
    return render(request, 'core/rotation_periods/rotation_period_list.html', {
        'periods': periods,
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
                period_count = period.daily_rotation_plan.periods.count()
                plural = '' if period_count == 1 else 's'
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Période de rotation créée avec succès.</div>'
                    f'<script>'
                    f'refreshPlanPeriods({plan_id}); '
                    f'document.getElementById("period-count-{plan_id}").innerHTML = "{period_count} période{plural}"; '
                    f'setTimeout(() => {{ document.querySelector("form[hx-post*=\'rotation_period\']").reset(); }}, 500);'
                    f'</script>'
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
                period_count = period.daily_rotation_plan.periods.count()
                plural = '' if period_count == 1 else 's'
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Période de rotation modifiée avec succès.</div>'
                    f'<script>'
                    f'setTimeout(() => {{ '
                    f'document.getElementById("period-modal").style.display = "none"; '
                    f'refreshPlanPeriods({plan_id}); '
                    f'document.getElementById("period-count-{plan_id}").innerHTML = "{period_count} période{plural}"; '
                    f'}}, 1000)'
                    f'</script>'
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
        
        # Get plans for filter dropdown
        plans = DailyRotationPlan.objects.all().order_by('designation')
        
        messages.success(request, f'Période de rotation supprimée avec succès.')
        return render(request, 'core/rotation_periods/rotation_period_list_partial.html', {
            'periods': periods,
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
    
    context = {
        'schedules': schedules,
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
    
    # Validate that the period belongs to a shift schedule
    if not hasattr(period, 'shift_schedule') or not period.shift_schedule:
        messages.error(request, "Cette période n'appartient à aucun roulement hebdomadaire valide.")
        return redirect('shift_schedule_list')
    
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
    
    # Validate that the week belongs to a period and shift schedule has periods
    if not hasattr(week, 'period') or not week.period:
        messages.error(request, "Cette semaine n'appartient à aucune période définie.")
        return redirect('shift_schedule_list')
    
    # Validate that the period still exists and belongs to a valid shift schedule
    try:
        period = week.period
        period.refresh_from_db()
        if not period.pk:
            messages.error(request, "La période de cette semaine n'existe plus.")
            return redirect('shift_schedule_list')
            
        shift_schedule = period.shift_schedule
        shift_schedule.refresh_from_db()
        if not shift_schedule.pk:
            messages.error(request, "Le roulement hebdomadaire de cette période n'existe plus.")
            return redirect('shift_schedule_list')
            
        # Verify the period is still associated with the schedule
        if not shift_schedule.periods.filter(id=period.id).exists():
            messages.error(request, "La période de cette semaine n'est plus associée à son roulement hebdomadaire.")
            return redirect('shift_schedule_list')
            
    except Exception as e:
        messages.error(request, "Erreur de validation : impossible d'accéder aux données de cette semaine.")
        return redirect('shift_schedule_list')
    
    if request.method == 'POST':
        form = ShiftScheduleDailyPlanForm(request.POST)
        if form.is_valid():
            # Validate that the selected daily rotation plan has periods defined
            selected_daily_plan = form.cleaned_data['daily_rotation_plan']
            if not selected_daily_plan.periods.exists():
                form.add_error('daily_rotation_plan', 
                    f'Impossible d\'assigner le rythme quotidien "{selected_daily_plan.designation}" : '
                    'aucune période n\'est définie pour ce rythme. '
                    'Veuillez d\'abord ajouter une période à ce rythme quotidien.')
                
                # Return form with error for HTMX
                if request.headers.get('HX-Request'):
                    return render(request, 'core/shift_schedules/shift_schedule_daily_plan_form_htmx.html', {
                        'form': form,
                        'week': week,
                        'daily_plan': None,
                        'weekday': weekday,
                        'current_agent': get_agent_from_user(request.user),
                    })
                    
            with transaction.atomic():
                daily_plan = form.save(commit=False)
                daily_plan.week = week
                daily_plan.weekday = weekday
                
                try:
                    daily_plan.full_clean()  # This will call our clean() method
                    daily_plan.save()
                except ValidationError as e:
                    # Handle validation errors
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            form.add_error(field if field != '__all__' else None, error)
                    
                    # Return form with errors for HTMX
                    if request.headers.get('HX-Request'):
                        return render(request, 'core/shift_schedules/shift_schedule_daily_plan_form_htmx.html', {
                            'form': form,
                            'week': week,
                            'daily_plan': None,
                            'weekday': weekday,
                            'current_agent': get_agent_from_user(request.user),
                        })
                    return render(request, 'core/shift_schedules/shift_schedule_daily_plan_form_htmx.html', {
                        'form': form,
                        'week': week,
                        'daily_plan': None,
                        'weekday': weekday,
                        'current_agent': get_agent_from_user(request.user),
                    })
                
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
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'date')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/public_holidays/public_holiday_list_partial.html', {
            'holidays': holidays,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order,
            'holidays_by_year': holidays_by_year
        })
    
    return render(request, 'core/public_holidays/public_holiday_list.html', {
        'holidays': holidays,
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
        
        return render(request, 'core/public_holidays/public_holiday_list_partial.html', {
            'holidays': holidays,
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
def team_count(request):
    """HTMX endpoint for team count"""
    count = Team.objects.count()
    return HttpResponse(f'<p class="text-2xl font-semibold text-gray-900" id="team-count">{count}</p>')


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
    
    # Get current sort order for template
    current_sort = request.GET.get('sort', 'order')
    current_order = request.GET.get('order', 'asc')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/departments/department_list_partial.html', {
            'departments': departments,
            'search_query': search_query,
            'current_sort': current_sort,
            'current_order': current_order
        })
    
    return render(request, 'core/departments/department_list.html', {
        'departments': departments,
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
        
        return render(request, 'core/departments/department_list_partial.html', {
            'departments': departments,
            'search_query': search_query,
            'current_sort': request.GET.get('sort', 'order'),
            'current_order': request.GET.get('order', 'asc'),
            'success_message': f'Département "{name}" supprimé avec succès.'
        })
    
    messages.success(request, f'Département "{name}" supprimé avec succès.')
    return redirect('department_list')


@user_passes_test(is_superuser)
def department_export(request):
    """Export departments to JSON file - only accessible to superusers"""
    departments = Department.objects.all()
    
    # Prepare data for export
    export_data = []
    for department in departments:
        department_data = {
            'name': department.name,
            'order': department.order,
            'created_at': department.created_at.isoformat() if department.created_at else None,
            'updated_at': department.updated_at.isoformat() if department.updated_at else None,
        }
        export_data.append(department_data)
    
    # Generate filename with current date (timezone-aware)
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_departments.json"
    
    # Create response
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def department_import(request):
    """Import departments from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_department_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_department_changelist')
        
        try:
            # Read and parse JSON
            content = import_file.read().decode('utf-8')
            data = json.loads(content)
            
            if not isinstance(data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste de départements.')
                return redirect('admin:core_department_changelist')
            
            # Validate required fields for each department
            required_fields = ['name', 'order']
            errors = []
            
            for i, department_data in enumerate(data):
                for field in required_fields:
                    if field not in department_data or department_data[field] is None:
                        errors.append(f'Département {i+1}: champ "{field}" manquant ou vide')
                
                # Validate order is a positive integer
                if 'order' in department_data:
                    try:
                        order_value = int(department_data['order'])
                        if order_value < 1:
                            errors.append(f'Département {i+1}: l\'ordre doit être un nombre positif')
                    except (ValueError, TypeError):
                        errors.append(f'Département {i+1}: l\'ordre doit être un nombre entier')
            
            if errors:
                messages.error(request, f'Erreurs de validation ({len(errors)} erreurs trouvées):')
                for error in errors[:3]:  # Show first 3 errors
                    messages.error(request, f'  • {error}')
                if len(errors) > 3:
                    messages.error(request, f'  • ... et {len(errors) - 3} autres erreurs.')
                return redirect('admin:core_department_changelist')
            
            # Delete all existing departments
            Department.objects.all().delete()
            
            # Import new departments
            created_count = 0
            for department_data in data:
                Department.objects.create(
                    name=department_data['name'],
                    order=int(department_data['order'])
                )
                created_count += 1
            
            messages.success(request, f'Import réussi: {created_count} départements importés.')
            
        except json.JSONDecodeError:
            messages.error(request, 'Le fichier JSON n\'est pas valide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation: {str(e)}')
    
    return redirect('admin:core_department_changelist')


@user_passes_test(is_superuser)
def function_export(request):
    """Export functions to JSON file - only accessible to superusers"""
    functions = Function.objects.all()
    
    # Prepare data for export
    export_data = []
    for function in functions:
        function_data = {
            'designation': function.designation,
            'description': function.description,
            'status': function.status,
        }
        export_data.append(function_data)
    
    # Generate filename with current date (timezone-aware)
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_functions.json"
    
    # Create response
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def function_import(request):
    """Import functions from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_function_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_function_changelist')
        
        try:
            # Read and parse JSON
            content = import_file.read().decode('utf-8')
            data = json.loads(content)
            
            if not isinstance(data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste de fonctions.')
                return redirect('admin:core_function_changelist')
            
            # Validate required fields for each function
            required_fields = ['designation']
            errors = []
            
            for i, function_data in enumerate(data):
                for field in required_fields:
                    if field not in function_data or not function_data[field]:
                        errors.append(f'Fonction {i+1}: champ "{field}" manquant ou vide')
                
                # Validate status is boolean if provided
                if 'status' in function_data and function_data['status'] is not None:
                    if not isinstance(function_data['status'], bool):
                        errors.append(f'Fonction {i+1}: le statut doit être true ou false')
            
            if errors:
                messages.error(request, f'Erreurs de validation ({len(errors)} erreurs trouvées):')
                for error in errors[:3]:  # Show first 3 errors
                    messages.error(request, f'  • {error}')
                if len(errors) > 3:
                    messages.error(request, f'  • ... et {len(errors) - 3} autres erreurs.')
                return redirect('admin:core_function_changelist')
            
            # Delete all existing functions
            Function.objects.all().delete()
            
            # Import new functions
            created_count = 0
            for function_data in data:
                Function.objects.create(
                    designation=function_data['designation'],
                    description=function_data.get('description', ''),
                    status=function_data.get('status', True)
                )
                created_count += 1
            
            messages.success(request, f'Import réussi: {created_count} fonctions importées.')
            
        except json.JSONDecodeError:
            messages.error(request, 'Le fichier JSON n\'est pas valide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation: {str(e)}')
    
    return redirect('admin:core_function_changelist')


@user_passes_test(is_superuser)
def scheduletype_export(request):
    """Export schedule types to JSON file - only accessible to superusers"""
    schedule_types = ScheduleType.objects.all()
    
    # Prepare data for export
    export_data = []
    for schedule_type in schedule_types:
        schedule_type_data = {
            'designation': schedule_type.designation,
            'short_designation': schedule_type.short_designation,
            'color': schedule_type.color,
        }
        export_data.append(schedule_type_data)
    
    # Generate filename with current date (timezone-aware)
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_schedule_types.json"
    
    # Create response
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def scheduletype_import(request):
    """Import schedule types from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_scheduletype_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_scheduletype_changelist')
        
        try:
            # Read and parse JSON
            content = import_file.read().decode('utf-8')
            data = json.loads(content)
            
            if not isinstance(data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste de types d\'horaires.')
                return redirect('admin:core_scheduletype_changelist')
            
            # Validate required fields for each schedule type
            required_fields = ['designation', 'color']
            errors = []
            
            for i, schedule_type_data in enumerate(data):
                for field in required_fields:
                    if field not in schedule_type_data or not schedule_type_data[field]:
                        errors.append(f'Type d\'horaire {i+1}: champ "{field}" manquant ou vide')
                
                # Validate color format (hexadecimal)
                if 'color' in schedule_type_data and schedule_type_data['color']:
                    import re
                    if not re.match(r'^#[0-9A-Fa-f]{6}$', schedule_type_data['color']):
                        errors.append(f'Type d\'horaire {i+1}: la couleur doit être au format hexadécimal (ex: #FF0000)')
                
                # Validate short_designation format if provided
                if 'short_designation' in schedule_type_data and schedule_type_data['short_designation']:
                    if not re.match(r'^[A-Z]{2,3}$', schedule_type_data['short_designation'].upper()):
                        errors.append(f'Type d\'horaire {i+1}: l\'abréviation doit contenir 2 ou 3 lettres majuscules uniquement')
            
            if errors:
                messages.error(request, f'Erreurs de validation ({len(errors)} erreurs trouvées):')
                for error in errors[:3]:  # Show first 3 errors
                    messages.error(request, f'  • {error}')
                if len(errors) > 3:
                    messages.error(request, f'  • ... et {len(errors) - 3} autres erreurs.')
                return redirect('admin:core_scheduletype_changelist')
            
            # Delete all existing schedule types
            ScheduleType.objects.all().delete()
            
            # Import new schedule types
            created_count = 0
            for schedule_type_data in data:
                ScheduleType.objects.create(
                    designation=schedule_type_data['designation'],
                    short_designation=schedule_type_data.get('short_designation', '').upper() if schedule_type_data.get('short_designation') else None,
                    color=schedule_type_data['color']
                )
                created_count += 1
            
            messages.success(request, f'Import réussi: {created_count} types d\'horaires importés.')
            
        except json.JSONDecodeError:
            messages.error(request, 'Le fichier JSON n\'est pas valide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation: {str(e)}')
    
    return redirect('admin:core_scheduletype_changelist')


@user_passes_test(is_superuser)
def dailyrotationplan_export(request):
    """Export daily rotation plans to JSON file - only accessible to superusers"""
    daily_rotation_plans = DailyRotationPlan.objects.all()
    
    # Prepare data for export
    export_data = []
    for plan in daily_rotation_plans:
        plan_data = {
            'designation': plan.designation,
            'description': plan.description,
            'schedule_type_designation': plan.schedule_type.designation,
            'created_at': plan.created_at.isoformat() if plan.created_at else None,
            'updated_at': plan.updated_at.isoformat() if plan.updated_at else None,
        }
        export_data.append(plan_data)
    
    # Generate filename with current date (timezone-aware)
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_daily_rotation_plans.json"
    
    # Create response
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def dailyrotationplan_import(request):
    """Import daily rotation plans from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_dailyrotationplan_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_dailyrotationplan_changelist')
        
        try:
            # Read and parse JSON
            content = import_file.read().decode('utf-8')
            data = json.loads(content)
            
            if not isinstance(data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste de rythmes quotidiens.')
                return redirect('admin:core_dailyrotationplan_changelist')
            
            # Validate required fields for each daily rotation plan
            required_fields = ['designation', 'schedule_type_designation']
            errors = []
            
            for i, plan_data in enumerate(data):
                for field in required_fields:
                    if field not in plan_data or not plan_data[field]:
                        errors.append(f'Rythme quotidien {i+1}: champ "{field}" manquant ou vide')
                
                # Validate that schedule_type exists
                if 'schedule_type_designation' in plan_data and plan_data['schedule_type_designation']:
                    try:
                        ScheduleType.objects.get(designation=plan_data['schedule_type_designation'])
                    except ScheduleType.DoesNotExist:
                        errors.append(f'Rythme quotidien {i+1}: type d\'horaire "{plan_data["schedule_type_designation"]}" introuvable')
            
            if errors:
                messages.error(request, f'Erreurs de validation ({len(errors)} erreurs trouvées):')
                for error in errors[:3]:  # Show first 3 errors
                    messages.error(request, f'  • {error}')
                if len(errors) > 3:
                    messages.error(request, f'  • ... et {len(errors) - 3} autres erreurs.')
                return redirect('admin:core_dailyrotationplan_changelist')
            
            # Delete all existing daily rotation plans
            DailyRotationPlan.objects.all().delete()
            
            # Import new daily rotation plans
            created_count = 0
            for plan_data in data:
                schedule_type = ScheduleType.objects.get(designation=plan_data['schedule_type_designation'])
                DailyRotationPlan.objects.create(
                    designation=plan_data['designation'],
                    description=plan_data.get('description', ''),
                    schedule_type=schedule_type
                )
                created_count += 1
            
            messages.success(request, f'Import réussi: {created_count} rythmes quotidiens importés.')
            
        except json.JSONDecodeError:
            messages.error(request, 'Le fichier JSON n\'est pas valide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation: {str(e)}')
    
    return redirect('admin:core_dailyrotationplan_changelist')


@user_passes_test(is_superuser)
def shiftschedule_export(request):
    """Export shift schedules to JSON file - only accessible to superusers"""
    shift_schedules = ShiftSchedule.objects.all()
    
    # Prepare data for export
    export_data = []
    for schedule in shift_schedules:
        schedule_data = {
            'name': schedule.name,
            'type': schedule.type,
            'break_times': schedule.break_times,
            'created_at': schedule.created_at.isoformat() if schedule.created_at else None,
            'updated_at': schedule.updated_at.isoformat() if schedule.updated_at else None,
        }
        export_data.append(schedule_data)
    
    # Generate filename with current date (timezone-aware)
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_shift_schedules.json"
    
    # Create response
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def shiftschedule_import(request):
    """Import shift schedules from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_shiftschedule_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_shiftschedule_changelist')
        
        try:
            # Read and parse JSON
            content = import_file.read().decode('utf-8')
            data = json.loads(content)
            
            if not isinstance(data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste de plannings de poste.')
                return redirect('admin:core_shiftschedule_changelist')
            
            # Validate required fields for each shift schedule
            required_fields = ['name', 'type']
            valid_types = ['day', 'shift']
            errors = []
            
            for i, schedule_data in enumerate(data):
                for field in required_fields:
                    if field not in schedule_data or not schedule_data[field]:
                        errors.append(f'Planning de poste {i+1}: champ "{field}" manquant ou vide')
                
                # Validate type choice
                if 'type' in schedule_data and schedule_data['type']:
                    if schedule_data['type'] not in valid_types:
                        errors.append(f'Planning de poste {i+1}: type "{schedule_data["type"]}" invalide (doit être "day" ou "shift")')
                
                # Validate break_times is a positive integer if provided
                if 'break_times' in schedule_data and schedule_data['break_times'] is not None:
                    try:
                        break_times = int(schedule_data['break_times'])
                        if break_times < 0:
                            errors.append(f'Planning de poste {i+1}: le nombre de pauses doit être positif')
                    except (ValueError, TypeError):
                        errors.append(f'Planning de poste {i+1}: le nombre de pauses doit être un nombre entier')
            
            if errors:
                messages.error(request, f'Erreurs de validation ({len(errors)} erreurs trouvées):')
                for error in errors[:3]:  # Show first 3 errors
                    messages.error(request, f'  • {error}')
                if len(errors) > 3:
                    messages.error(request, f'  • ... et {len(errors) - 3} autres erreurs.')
                return redirect('admin:core_shiftschedule_changelist')
            
            # Delete all existing shift schedules
            ShiftSchedule.objects.all().delete()
            
            # Import new shift schedules
            created_count = 0
            for schedule_data in data:
                ShiftSchedule.objects.create(
                    name=schedule_data['name'],
                    type=schedule_data['type'],
                    break_times=schedule_data.get('break_times', 2)
                )
                created_count += 1
            
            messages.success(request, f'Import réussi: {created_count} plannings de poste importés.')
            
        except json.JSONDecodeError:
            messages.error(request, 'Le fichier JSON n\'est pas valide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation: {str(e)}')
    
    return redirect('admin:core_shiftschedule_changelist')


@user_passes_test(is_superuser)
def shiftscheduleperiod_export(request):
    """Export shift schedule periods to JSON file - only accessible to superusers"""
    shift_schedule_periods = ShiftSchedulePeriod.objects.all()
    
    # Prepare data for export
    export_data = []
    for period in shift_schedule_periods:
        period_data = {
            'shift_schedule_name': period.shift_schedule.name,
            'start_date': period.start_date.isoformat() if period.start_date else None,
            'end_date': period.end_date.isoformat() if period.end_date else None,
            'created_at': period.created_at.isoformat() if period.created_at else None,
            'updated_at': period.updated_at.isoformat() if period.updated_at else None,
        }
        export_data.append(period_data)
    
    # Generate filename with current date (timezone-aware)
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_shift_schedule_periods.json"
    
    # Create response
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def shiftscheduleperiod_import(request):
    """Import shift schedule periods from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_shiftscheduleperiod_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_shiftscheduleperiod_changelist')
        
        try:
            # Read and parse JSON
            content = import_file.read().decode('utf-8')
            data = json.loads(content)
            
            if not isinstance(data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste de périodes de planning de poste.')
                return redirect('admin:core_shiftscheduleperiod_changelist')
            
            # Validate required fields for each period
            required_fields = ['shift_schedule_name', 'start_date', 'end_date']
            errors = []
            
            for i, period_data in enumerate(data):
                for field in required_fields:
                    if field not in period_data or not period_data[field]:
                        errors.append(f'Période {i+1}: champ "{field}" manquant ou vide')
                
                # Validate that shift_schedule exists
                if 'shift_schedule_name' in period_data and period_data['shift_schedule_name']:
                    try:
                        ShiftSchedule.objects.get(name=period_data['shift_schedule_name'])
                    except ShiftSchedule.DoesNotExist:
                        errors.append(f'Période {i+1}: planning de poste "{period_data["shift_schedule_name"]}" introuvable')
                
                # Validate date formats
                for date_field in ['start_date', 'end_date']:
                    if date_field in period_data and period_data[date_field]:
                        try:
                            from datetime import datetime
                            datetime.fromisoformat(period_data[date_field])
                        except ValueError:
                            errors.append(f'Période {i+1}: format de date invalide pour "{date_field}" (attendu: YYYY-MM-DD)')
                
                # Validate that end_date >= start_date
                if ('start_date' in period_data and period_data['start_date'] and
                    'end_date' in period_data and period_data['end_date']):
                    try:
                        start_date = datetime.fromisoformat(period_data['start_date']).date()
                        end_date = datetime.fromisoformat(period_data['end_date']).date()
                        if end_date < start_date:
                            errors.append(f'Période {i+1}: la date de fin doit être postérieure ou égale à la date de début')
                    except ValueError:
                        pass  # Date format error already caught above
            
            if errors:
                messages.error(request, f'Erreurs de validation ({len(errors)} erreurs trouvées):')
                for error in errors[:3]:  # Show first 3 errors
                    messages.error(request, f'  • {error}')
                if len(errors) > 3:
                    messages.error(request, f'  • ... et {len(errors) - 3} autres erreurs.')
                return redirect('admin:core_shiftscheduleperiod_changelist')
            
            # Delete all existing shift schedule periods
            ShiftSchedulePeriod.objects.all().delete()
            
            # Import new shift schedule periods
            created_count = 0
            for period_data in data:
                shift_schedule = ShiftSchedule.objects.get(name=period_data['shift_schedule_name'])
                start_date = datetime.fromisoformat(period_data['start_date']).date()
                end_date = datetime.fromisoformat(period_data['end_date']).date()
                
                ShiftSchedulePeriod.objects.create(
                    shift_schedule=shift_schedule,
                    start_date=start_date,
                    end_date=end_date
                )
                created_count += 1
            
            messages.success(request, f'Import réussi: {created_count} périodes de planning de poste importées.')
            
        except json.JSONDecodeError:
            messages.error(request, 'Le fichier JSON n\'est pas valide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation: {str(e)}')
    
    return redirect('admin:core_shiftscheduleperiod_changelist')


@user_passes_test(is_superuser)
def rotationperiod_export(request):
    """Export rotation periods to JSON file - only accessible to superusers"""
    rotation_periods = RotationPeriod.objects.all()
    
    # Prepare data for export
    export_data = []
    for period in rotation_periods:
        period_data = {
            'daily_rotation_plan_designation': period.daily_rotation_plan.designation,
            'start_date': period.start_date.isoformat() if period.start_date else None,
            'end_date': period.end_date.isoformat() if period.end_date else None,
            'start_time': period.start_time.isoformat() if period.start_time else None,
            'end_time': period.end_time.isoformat() if period.end_time else None,
            'created_at': period.created_at.isoformat() if period.created_at else None,
            'updated_at': period.updated_at.isoformat() if period.updated_at else None,
        }
        export_data.append(period_data)
    
    # Generate filename with current date (timezone-aware)
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_rotation_periods.json"
    
    # Create response
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def rotationperiod_import(request):
    """Import rotation periods from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_rotationperiod_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_rotationperiod_changelist')
        
        try:
            # Read and parse JSON
            content = import_file.read().decode('utf-8')
            data = json.loads(content)
            
            if not isinstance(data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste de périodes de rotation.')
                return redirect('admin:core_rotationperiod_changelist')
            
            # Validate required fields for each period
            required_fields = ['daily_rotation_plan_designation', 'start_date', 'end_date', 'start_time', 'end_time']
            errors = []
            
            for i, period_data in enumerate(data):
                for field in required_fields:
                    if field not in period_data or not period_data[field]:
                        errors.append(f'Période {i+1}: champ "{field}" manquant ou vide')
                
                # Validate that daily_rotation_plan exists
                if 'daily_rotation_plan_designation' in period_data and period_data['daily_rotation_plan_designation']:
                    try:
                        DailyRotationPlan.objects.get(designation=period_data['daily_rotation_plan_designation'])
                    except DailyRotationPlan.DoesNotExist:
                        errors.append(f'Période {i+1}: rythme quotidien "{period_data["daily_rotation_plan_designation"]}" introuvable')
                
                # Validate date formats
                for date_field in ['start_date', 'end_date']:
                    if date_field in period_data and period_data[date_field]:
                        try:
                            from datetime import datetime
                            datetime.fromisoformat(period_data[date_field])
                        except ValueError:
                            errors.append(f'Période {i+1}: format de date invalide pour "{date_field}" (attendu: YYYY-MM-DD)')
                
                # Validate time formats
                for time_field in ['start_time', 'end_time']:
                    if time_field in period_data and period_data[time_field]:
                        try:
                            from datetime import datetime
                            datetime.fromisoformat(f"2000-01-01T{period_data[time_field]}")
                        except ValueError:
                            errors.append(f'Période {i+1}: format d\'heure invalide pour "{time_field}" (attendu: HH:MM:SS)')
                
                # Validate that end_date >= start_date
                if ('start_date' in period_data and period_data['start_date'] and
                    'end_date' in period_data and period_data['end_date']):
                    try:
                        start_date = datetime.fromisoformat(period_data['start_date']).date()
                        end_date = datetime.fromisoformat(period_data['end_date']).date()
                        if end_date < start_date:
                            errors.append(f'Période {i+1}: la date de fin doit être postérieure ou égale à la date de début')
                    except ValueError:
                        pass  # Date format error already caught above
                
                # Validate time consistency (night shifts are allowed)
                if ('start_time' in period_data and period_data['start_time'] and
                    'end_time' in period_data and period_data['end_time']):
                    try:
                        start_time = datetime.fromisoformat(f"2000-01-01T{period_data['start_time']}").time()
                        end_time = datetime.fromisoformat(f"2000-01-01T{period_data['end_time']}").time()
                        
                        if start_time >= end_time:
                            # Check if this could be a valid night shift
                            from datetime import time
                            is_potential_night_shift = (
                                start_time >= time(16, 0) and end_time <= time(12, 0)
                            )
                            if not is_potential_night_shift:
                                errors.append(f'Période {i+1}: heure de fin invalide. Les équipes de nuit doivent commencer après 16:00 et finir avant 12:00')
                    except ValueError:
                        pass  # Time format error already caught above
            
            if errors:
                messages.error(request, f'Erreurs de validation ({len(errors)} erreurs trouvées):')
                for error in errors[:3]:  # Show first 3 errors
                    messages.error(request, f'  • {error}')
                if len(errors) > 3:
                    messages.error(request, f'  • ... et {len(errors) - 3} autres erreurs.')
                return redirect('admin:core_rotationperiod_changelist')
            
            # Delete all existing rotation periods
            RotationPeriod.objects.all().delete()
            
            # Import new rotation periods
            created_count = 0
            for period_data in data:
                daily_rotation_plan = DailyRotationPlan.objects.get(designation=period_data['daily_rotation_plan_designation'])
                start_date = datetime.fromisoformat(period_data['start_date']).date()
                end_date = datetime.fromisoformat(period_data['end_date']).date()
                start_time = datetime.fromisoformat(f"2000-01-01T{period_data['start_time']}").time()
                end_time = datetime.fromisoformat(f"2000-01-01T{period_data['end_time']}").time()
                
                RotationPeriod.objects.create(
                    daily_rotation_plan=daily_rotation_plan,
                    start_date=start_date,
                    end_date=end_date,
                    start_time=start_time,
                    end_time=end_time
                )
                created_count += 1
            
            messages.success(request, f'Import réussi: {created_count} périodes de rotation importées.')
            
        except json.JSONDecodeError:
            messages.error(request, 'Le fichier JSON n\'est pas valide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation: {str(e)}')
    
    return redirect('admin:core_rotationperiod_changelist')


@user_passes_test(is_superuser)
def shiftscheduleweek_export(request):
    """Export shift schedule weeks to JSON - only accessible to superusers"""
    weeks = ShiftScheduleWeek.objects.all().order_by('period__shift_schedule__name', 'period__start_date', 'week_number')
    
    weeks_data = []
    for week in weeks:
        weeks_data.append({
            'shift_schedule_name': week.period.shift_schedule.name,
            'period_start_date': week.period.start_date.isoformat(),
            'period_end_date': week.period.end_date.isoformat(),
            'week_number': week.week_number
        })
    
    # Generate filename with current date
    from django.utils import timezone
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_shift_schedule_weeks.json"
    
    response = HttpResponse(
        json.dumps(weeks_data, indent=2, ensure_ascii=False),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def shiftscheduleweek_import(request):
    """Import shift schedule weeks from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_shiftscheduleweek_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_shiftscheduleweek_changelist')
        
        try:
            # Read and parse JSON
            content = import_file.read().decode('utf-8')
            data = json.loads(content)
            
            if not isinstance(data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste de semaines de planning.')
                return redirect('admin:core_shiftscheduleweek_changelist')
            
            # Validate required fields for each week
            required_fields = ['shift_schedule_name', 'period_start_date', 'period_end_date', 'week_number']
            errors = []
            
            for i, week_data in enumerate(data):
                for field in required_fields:
                    if field not in week_data or week_data[field] is None or week_data[field] == '':
                        errors.append(f'Semaine {i+1}: champ "{field}" manquant ou vide')
                
                # Validate that shift schedule exists
                if 'shift_schedule_name' in week_data and week_data['shift_schedule_name']:
                    try:
                        shift_schedule = ShiftSchedule.objects.get(name=week_data['shift_schedule_name'])
                        
                        # Validate that the period exists for this shift schedule
                        if ('period_start_date' in week_data and week_data['period_start_date'] and
                            'period_end_date' in week_data and week_data['period_end_date']):
                            try:
                                start_date = datetime.fromisoformat(week_data['period_start_date']).date()
                                end_date = datetime.fromisoformat(week_data['period_end_date']).date()
                                
                                period = ShiftSchedulePeriod.objects.filter(
                                    shift_schedule=shift_schedule,
                                    start_date=start_date,
                                    end_date=end_date
                                ).first()
                                
                                if not period:
                                    errors.append(f'Semaine {i+1}: période {start_date} - {end_date} introuvable pour le planning "{week_data["shift_schedule_name"]}"')
                            except ValueError:
                                pass  # Date format error will be caught below
                    except ShiftSchedule.DoesNotExist:
                        errors.append(f'Semaine {i+1}: planning de poste "{week_data["shift_schedule_name"]}" introuvable')
                
                # Validate date formats
                for date_field in ['period_start_date', 'period_end_date']:
                    if date_field in week_data and week_data[date_field]:
                        try:
                            from datetime import datetime
                            datetime.fromisoformat(week_data[date_field])
                        except ValueError:
                            errors.append(f'Semaine {i+1}: format de date invalide pour "{date_field}" (attendu: YYYY-MM-DD)')
                
                # Validate week_number is a positive integer
                if 'week_number' in week_data:
                    try:
                        week_number = int(week_data['week_number'])
                        if week_number <= 0:
                            errors.append(f'Semaine {i+1}: le numéro de semaine doit être un entier positif')
                    except (ValueError, TypeError):
                        errors.append(f'Semaine {i+1}: numéro de semaine invalide (doit être un nombre entier)')
                
                # Validate that period dates are consistent
                if ('period_start_date' in week_data and week_data['period_start_date'] and
                    'period_end_date' in week_data and week_data['period_end_date']):
                    try:
                        start_date = datetime.fromisoformat(week_data['period_start_date']).date()
                        end_date = datetime.fromisoformat(week_data['period_end_date']).date()
                        if end_date < start_date:
                            errors.append(f'Semaine {i+1}: la date de fin de période doit être postérieure ou égale à la date de début')
                    except ValueError:
                        pass  # Date format error already caught above
            
            if errors:
                messages.error(request, f'Erreurs de validation ({len(errors)} erreurs trouvées):')
                for error in errors[:3]:  # Show first 3 errors
                    messages.error(request, f'  • {error}')
                if len(errors) > 3:
                    messages.error(request, f'  • ... et {len(errors) - 3} autres erreurs.')
                return redirect('admin:core_shiftscheduleweek_changelist')
            
            # Delete all existing shift schedule weeks
            ShiftScheduleWeek.objects.all().delete()
            
            # Import new shift schedule weeks
            created_count = 0
            for week_data in data:
                shift_schedule = ShiftSchedule.objects.get(name=week_data['shift_schedule_name'])
                start_date = datetime.fromisoformat(week_data['period_start_date']).date()
                end_date = datetime.fromisoformat(week_data['period_end_date']).date()
                
                period = ShiftSchedulePeriod.objects.get(
                    shift_schedule=shift_schedule,
                    start_date=start_date,
                    end_date=end_date
                )
                
                ShiftScheduleWeek.objects.create(
                    period=period,
                    week_number=int(week_data['week_number'])
                )
                created_count += 1
            
            messages.success(request, f'Import réussi: {created_count} semaines de planning importées.')
            
        except json.JSONDecodeError:
            messages.error(request, 'Le fichier JSON n\'est pas valide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation: {str(e)}')
    
    return redirect('admin:core_shiftscheduleweek_changelist')


@user_passes_test(is_superuser)
def shiftscheduledailyplan_export(request):
    """Export shift schedule daily plans to JSON - only accessible to superusers"""
    daily_plans = ShiftScheduleDailyPlan.objects.all().order_by('week__period__shift_schedule__name', 'week__period__start_date', 'week__week_number', 'weekday')
    
    daily_plans_data = []
    for plan in daily_plans:
        daily_plans_data.append({
            'shift_schedule_name': plan.week.period.shift_schedule.name,
            'period_start_date': plan.week.period.start_date.isoformat(),
            'period_end_date': plan.week.period.end_date.isoformat(),
            'week_number': plan.week.week_number,
            'weekday': plan.weekday,
            'daily_rotation_plan_designation': plan.daily_rotation_plan.designation
        })
    
    # Generate filename with current date
    from django.utils import timezone
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_shift_schedule_daily_plans.json"
    
    response = HttpResponse(
        json.dumps(daily_plans_data, indent=2, ensure_ascii=False),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def shiftscheduledailyplan_import(request):
    """Import shift schedule daily plans from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_shiftscheduledailyplan_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_shiftscheduledailyplan_changelist')
        
        try:
            # Read and parse JSON
            content = import_file.read().decode('utf-8')
            data = json.loads(content)
            
            if not isinstance(data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste de plans quotidiens de planning.')
                return redirect('admin:core_shiftscheduledailyplan_changelist')
            
            # Validate required fields for each daily plan
            required_fields = ['shift_schedule_name', 'period_start_date', 'period_end_date', 'week_number', 'weekday', 'daily_rotation_plan_designation']
            errors = []
            
            for i, plan_data in enumerate(data):
                for field in required_fields:
                    if field not in plan_data or plan_data[field] is None or plan_data[field] == '':
                        errors.append(f'Plan {i+1}: champ "{field}" manquant ou vide')
                
                # Validate that shift schedule exists
                if 'shift_schedule_name' in plan_data and plan_data['shift_schedule_name']:
                    try:
                        shift_schedule = ShiftSchedule.objects.get(name=plan_data['shift_schedule_name'])
                        
                        # Validate that the period exists for this shift schedule
                        if ('period_start_date' in plan_data and plan_data['period_start_date'] and
                            'period_end_date' in plan_data and plan_data['period_end_date']):
                            try:
                                start_date = datetime.fromisoformat(plan_data['period_start_date']).date()
                                end_date = datetime.fromisoformat(plan_data['period_end_date']).date()
                                
                                period = ShiftSchedulePeriod.objects.filter(
                                    shift_schedule=shift_schedule,
                                    start_date=start_date,
                                    end_date=end_date
                                ).first()
                                
                                if not period:
                                    errors.append(f'Plan {i+1}: période {start_date} - {end_date} introuvable pour le planning "{plan_data["shift_schedule_name"]}"')
                                else:
                                    # Validate that the week exists for this period
                                    if 'week_number' in plan_data and plan_data['week_number']:
                                        try:
                                            week_number = int(plan_data['week_number'])
                                            week = ShiftScheduleWeek.objects.filter(
                                                period=period,
                                                week_number=week_number
                                            ).first()
                                            
                                            if not week:
                                                errors.append(f'Plan {i+1}: semaine {week_number} introuvable pour la période {start_date} - {end_date}')
                                        except ValueError:
                                            pass  # Week number format error will be caught below
                            except ValueError:
                                pass  # Date format error will be caught below
                    except ShiftSchedule.DoesNotExist:
                        errors.append(f'Plan {i+1}: planning de poste "{plan_data["shift_schedule_name"]}" introuvable')
                
                # Validate that daily rotation plan exists
                if 'daily_rotation_plan_designation' in plan_data and plan_data['daily_rotation_plan_designation']:
                    try:
                        DailyRotationPlan.objects.get(designation=plan_data['daily_rotation_plan_designation'])
                    except DailyRotationPlan.DoesNotExist:
                        errors.append(f'Plan {i+1}: rythme quotidien "{plan_data["daily_rotation_plan_designation"]}" introuvable')
                
                # Validate date formats
                for date_field in ['period_start_date', 'period_end_date']:
                    if date_field in plan_data and plan_data[date_field]:
                        try:
                            from datetime import datetime
                            datetime.fromisoformat(plan_data[date_field])
                        except ValueError:
                            errors.append(f'Plan {i+1}: format de date invalide pour "{date_field}" (attendu: YYYY-MM-DD)')
                
                # Validate week_number is a positive integer
                if 'week_number' in plan_data:
                    try:
                        week_number = int(plan_data['week_number'])
                        if week_number <= 0:
                            errors.append(f'Plan {i+1}: le numéro de semaine doit être un entier positif')
                    except (ValueError, TypeError):
                        errors.append(f'Plan {i+1}: numéro de semaine invalide (doit être un nombre entier)')
                
                # Validate weekday is a valid integer (1-7)
                if 'weekday' in plan_data:
                    try:
                        weekday = int(plan_data['weekday'])
                        if weekday < 1 or weekday > 7:
                            errors.append(f'Plan {i+1}: le jour de la semaine doit être entre 1 (Lundi) et 7 (Dimanche)')
                    except (ValueError, TypeError):
                        errors.append(f'Plan {i+1}: jour de la semaine invalide (doit être un nombre entier entre 1 et 7)')
                
                # Validate that period dates are consistent
                if ('period_start_date' in plan_data and plan_data['period_start_date'] and
                    'period_end_date' in plan_data and plan_data['period_end_date']):
                    try:
                        start_date = datetime.fromisoformat(plan_data['period_start_date']).date()
                        end_date = datetime.fromisoformat(plan_data['period_end_date']).date()
                        if end_date < start_date:
                            errors.append(f'Plan {i+1}: la date de fin de période doit être postérieure ou égale à la date de début')
                    except ValueError:
                        pass  # Date format error already caught above
            
            if errors:
                messages.error(request, f'Erreurs de validation ({len(errors)} erreurs trouvées):')
                for error in errors[:3]:  # Show first 3 errors
                    messages.error(request, f'  • {error}')
                if len(errors) > 3:
                    messages.error(request, f'  • ... et {len(errors) - 3} autres erreurs.')
                return redirect('admin:core_shiftscheduledailyplan_changelist')
            
            # Delete all existing shift schedule daily plans
            ShiftScheduleDailyPlan.objects.all().delete()
            
            # Import new shift schedule daily plans
            created_count = 0
            for plan_data in data:
                shift_schedule = ShiftSchedule.objects.get(name=plan_data['shift_schedule_name'])
                start_date = datetime.fromisoformat(plan_data['period_start_date']).date()
                end_date = datetime.fromisoformat(plan_data['period_end_date']).date()
                
                period = ShiftSchedulePeriod.objects.get(
                    shift_schedule=shift_schedule,
                    start_date=start_date,
                    end_date=end_date
                )
                
                week = ShiftScheduleWeek.objects.get(
                    period=period,
                    week_number=int(plan_data['week_number'])
                )
                
                daily_rotation_plan = DailyRotationPlan.objects.get(designation=plan_data['daily_rotation_plan_designation'])
                
                ShiftScheduleDailyPlan.objects.create(
                    week=week,
                    weekday=int(plan_data['weekday']),
                    daily_rotation_plan=daily_rotation_plan
                )
                created_count += 1
            
            messages.success(request, f'Import réussi: {created_count} plans quotidiens de planning importés.')
            
        except json.JSONDecodeError:
            messages.error(request, 'Le fichier JSON n\'est pas valide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation: {str(e)}')
    
    return redirect('admin:core_shiftscheduledailyplan_changelist')


@user_passes_test(is_superuser)
def global_export(request):
    """Export all models to a single ZIP file - only accessible to superusers"""
    import zipfile
    import io
    from django.utils import timezone
    
    # Generate timestamp for filename
    current_date = timezone.now().strftime('%Y-%m-%d_%H%M%S')
    
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        # Export Agents
        agents = Agent.objects.all().order_by('matricule')
        agents_data = []
        for agent in agents:
            agents_data.append({
                'matricule': agent.matricule,
                'last_name': agent.last_name,
                'first_name': agent.first_name,
                'grade': agent.grade,
                'hire_date': agent.hire_date.isoformat(),
                'departure_date': agent.departure_date.isoformat() if agent.departure_date else None,
                'permission_level': agent.permission_level
            })
        zip_file.writestr(f"{current_date}_agents.json", json.dumps(agents_data, indent=2, ensure_ascii=False))
        
        # Export Departments
        departments = Department.objects.all().order_by('order', 'name')
        departments_data = []
        for dept in departments:
            departments_data.append({
                'name': dept.name,
                'order': dept.order
            })
        zip_file.writestr(f"{current_date}_departments.json", json.dumps(departments_data, indent=2, ensure_ascii=False))
        
        # Export Functions
        functions = Function.objects.all().order_by('designation')
        functions_data = []
        for func in functions:
            functions_data.append({
                'designation': func.designation,
                'description': func.description,
                'status': func.status
            })
        zip_file.writestr(f"{current_date}_functions.json", json.dumps(functions_data, indent=2, ensure_ascii=False))
        
        # Export Schedule Types
        schedule_types = ScheduleType.objects.all().order_by('designation')
        schedule_types_data = []
        for st in schedule_types:
            schedule_types_data.append({
                'designation': st.designation,
                'short_designation': st.short_designation,
                'color': st.color
            })
        zip_file.writestr(f"{current_date}_schedule_types.json", json.dumps(schedule_types_data, indent=2, ensure_ascii=False))
        
        # Export Daily Rotation Plans
        daily_plans = DailyRotationPlan.objects.all().order_by('designation')
        daily_plans_data = []
        for plan in daily_plans:
            daily_plans_data.append({
                'designation': plan.designation,
                'description': plan.description,
                'schedule_type_designation': plan.schedule_type.designation
            })
        zip_file.writestr(f"{current_date}_daily_rotation_plans.json", json.dumps(daily_plans_data, indent=2, ensure_ascii=False))
        
        # Export Rotation Periods
        rotation_periods = RotationPeriod.objects.all().order_by('daily_rotation_plan__designation', 'start_date', 'start_time')
        rotation_periods_data = []
        for period in rotation_periods:
            rotation_periods_data.append({
                'daily_rotation_plan_designation': period.daily_rotation_plan.designation,
                'start_date': period.start_date.isoformat(),
                'end_date': period.end_date.isoformat(),
                'start_time': period.start_time.isoformat(),
                'end_time': period.end_time.isoformat()
            })
        zip_file.writestr(f"{current_date}_rotation_periods.json", json.dumps(rotation_periods_data, indent=2, ensure_ascii=False))
        
        # Export Shift Schedules
        shift_schedules = ShiftSchedule.objects.all().order_by('name')
        shift_schedules_data = []
        for schedule in shift_schedules:
            shift_schedules_data.append({
                'name': schedule.name,
                'type': schedule.type,
                'break_times': schedule.break_times
            })
        zip_file.writestr(f"{current_date}_shift_schedules.json", json.dumps(shift_schedules_data, indent=2, ensure_ascii=False))
        
        # Export Shift Schedule Periods
        shift_periods = ShiftSchedulePeriod.objects.all().order_by('shift_schedule__name', 'start_date')
        shift_periods_data = []
        for period in shift_periods:
            shift_periods_data.append({
                'shift_schedule_name': period.shift_schedule.name,
                'start_date': period.start_date.isoformat(),
                'end_date': period.end_date.isoformat()
            })
        zip_file.writestr(f"{current_date}_shift_schedule_periods.json", json.dumps(shift_periods_data, indent=2, ensure_ascii=False))
        
        # Export Shift Schedule Weeks
        shift_weeks = ShiftScheduleWeek.objects.all().order_by('period__shift_schedule__name', 'period__start_date', 'week_number')
        shift_weeks_data = []
        for week in shift_weeks:
            shift_weeks_data.append({
                'shift_schedule_name': week.period.shift_schedule.name,
                'period_start_date': week.period.start_date.isoformat(),
                'period_end_date': week.period.end_date.isoformat(),
                'week_number': week.week_number
            })
        zip_file.writestr(f"{current_date}_shift_schedule_weeks.json", json.dumps(shift_weeks_data, indent=2, ensure_ascii=False))
        
        # Export Shift Schedule Daily Plans
        daily_plans_shift = ShiftScheduleDailyPlan.objects.all().order_by('week__period__shift_schedule__name', 'week__period__start_date', 'week__week_number', 'weekday')
        daily_plans_shift_data = []
        for plan in daily_plans_shift:
            daily_plans_shift_data.append({
                'shift_schedule_name': plan.week.period.shift_schedule.name,
                'period_start_date': plan.week.period.start_date.isoformat(),
                'period_end_date': plan.week.period.end_date.isoformat(),
                'week_number': plan.week.week_number,
                'weekday': plan.weekday,
                'daily_rotation_plan_designation': plan.daily_rotation_plan.designation
            })
        zip_file.writestr(f"{current_date}_shift_schedule_daily_plans.json", json.dumps(daily_plans_shift_data, indent=2, ensure_ascii=False))
    
    zip_buffer.seek(0)
    
    response = HttpResponse(
        zip_buffer.getvalue(),
        content_type='application/zip'
    )
    response['Content-Disposition'] = f'attachment; filename="{current_date}_export_global_planning.zip"'
    
    return response


# =============================================================================
# Team Management Views
# =============================================================================

@login_required
@admin_required
def team_list(request):
    """List all teams with search and department filtering"""
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    
    from django.db.models import Prefetch
    
    teams = Team.objects.select_related('department').prefetch_related(
        'positions__function',
        Prefetch('positions__agent_assignments', 
                queryset=TeamPositionAgentAssignment.objects.select_related('agent').order_by('-start_date')),
        Prefetch('positions__rotation_assignments', 
                queryset=TeamPositionRotationAssignment.objects.select_related('rotation_plan').order_by('-start_date'))
    ).order_by('designation')
    
    # Apply search filter
    if search_query:
        teams = teams.filter(
            Q(designation__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )
    
    # Apply department filter
    if department_filter:
        teams = teams.filter(department_id=department_filter)
    
    departments = Department.objects.all().order_by('order', 'name')
    current_agent = get_agent_from_user(request.user)
    
    from datetime import date
    
    context = {
        'teams': teams,
        'search_query': search_query,
        'department_filter': department_filter,
        'departments': departments,
        'current_agent': current_agent,
        'today': date.today(),
    }
    
    return render(request, 'core/teams/team_list.html', context)


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def team_create(request):
    """Create a new team"""
    # Check if we have departments
    if not Department.objects.exists():
        messages.error(request, 'Aucun département n\'est disponible. Vous devez créer un département avant de créer une équipe.')
        return redirect('team_list')
    
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                team = form.save()
                messages.success(request, f'L\'équipe "{team.designation}" a été créée avec succès.')
                
                if request.headers.get('HX-Request'):
                    return HttpResponse("""
                        <script>
                            document.getElementById('team-modal').style.display = 'none';
                            location.reload();
                        </script>
                    """)
                return redirect('team_list')
    else:
        form = TeamForm()
    
    context = {'form': form}
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/teams/team_form_htmx.html', context)
    return render(request, 'core/teams/team_form.html', context)


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def team_edit(request, team_id):
    """Edit an existing team"""
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            with transaction.atomic():
                team = form.save()
                messages.success(request, f'L\'équipe "{team.designation}" a été modifiée avec succès.')
                
                if request.headers.get('HX-Request'):
                    return HttpResponse("""
                        <script>
                            document.getElementById('team-modal').style.display = 'none';
                            location.reload();
                        </script>
                    """)
                return redirect('team_list')
    else:
        form = TeamForm(instance=team)
    
    context = {'form': form, 'team': team}
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/teams/team_form_htmx.html', context)
    return render(request, 'core/teams/team_form.html', context)


@login_required
@admin_required
@require_http_methods(["POST"])
def team_delete(request, team_id):
    """Delete a team"""
    try:
        team = get_object_or_404(Team, id=team_id)
        team_name = team.designation
        
        with transaction.atomic():
            team.delete()
        
        messages.success(request, f'L\'équipe "{team_name}" a été supprimée avec succès.')
        
        if request.headers.get('HX-Request'):
            return HttpResponse("""
                <script>
                    location.reload();
                </script>
            """)
        
        return redirect('team_list')
    except Exception as e:
        messages.error(request, f'Erreur lors de la suppression : {str(e)}')
        return redirect('team_list')


# =============================================================================
# Team Position Management Views
# =============================================================================

@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def team_position_create(request, team_id):
    """Create a new position for a team"""
    try:
        team = get_object_or_404(Team, id=team_id)
        
        # Check if we have functions
        if not Function.objects.filter(status=True).exists():
            messages.error(request, 'Aucune fonction active n\'est disponible. Vous devez créer une fonction avant d\'ajouter un poste à l\'équipe.')
            return redirect('team_list')
        
        if request.method == 'POST':
            form = TeamPositionForm(request.POST, team=team)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        position = form.save()
                        # Ensure the position has a function before accessing it
                        if position.function:
                            function_name = position.function.designation
                        else:
                            function_name = 'Fonction non définie'
                        messages.success(request, f'Le poste "{function_name}" a été ajouté à l\'équipe "{team.designation}" avec succès.')
                        return redirect('team_list')
                except Exception as e:
                    messages.error(request, f'Erreur lors de la création du poste: {str(e)}')
            else:
                # Debug: show form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Erreur {field}: {error}')
        else:
            form = TeamPositionForm(team=team)
        
        context = {'form': form, 'team': team}
        
        if request.headers.get('HX-Request'):
            return render(request, 'core/teams/team_position_form_htmx.html', context)
        return render(request, 'core/teams/team_position_form.html', context)
    
    except Exception as e:
        import traceback
        messages.error(request, f'Erreur dans team_position_create: {str(e)}')
        messages.error(request, f'Traceback: {traceback.format_exc()}')
        return redirect('team_list')


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def team_position_edit(request, position_id):
    """Edit an existing team position"""
    from django.db.models import Prefetch
    
    from datetime import date
    today = date.today()
    
    position = get_object_or_404(
        TeamPosition.objects.prefetch_related(
            Prefetch('agent_assignments', 
                    queryset=TeamPositionAgentAssignment.objects.select_related('agent').extra(
                        select={
                            'is_current': f'start_date <= "{today}" AND end_date >= "{today}"'
                        }
                    ).order_by('-is_current', '-start_date')),
            Prefetch('rotation_assignments', 
                    queryset=TeamPositionRotationAssignment.objects.select_related('rotation_plan').extra(
                        select={
                            'is_current': f'start_date <= "{today}" AND end_date >= "{today}"'
                        }
                    ).order_by('-is_current', '-start_date'))
        ),
        id=position_id
    )
    
    if request.method == 'POST':
        form = TeamPositionForm(request.POST, instance=position, team=position.team)
        if form.is_valid():
            with transaction.atomic():
                position = form.save()
                messages.success(request, f'Le poste "{position.function.designation}" a été modifié avec succès.')
                return redirect('team_list')
    else:
        form = TeamPositionForm(instance=position, team=position.team)
    
    context = {
        'form': form, 
        'position': position, 
        'team': position.team,
        'today': today
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/teams/team_position_form_htmx.html', context)
    return render(request, 'core/teams/team_position_form.html', context)


@login_required
@admin_required
@require_http_methods(["POST"])
def team_position_delete(request, position_id):
    """Delete a team position"""
    position = get_object_or_404(TeamPosition, id=position_id)
    function_name = position.function.designation
    team_name = position.team.designation
    
    with transaction.atomic():
        position.delete()
    
    messages.success(request, f'Le poste "{function_name}" a été retiré de l\'équipe "{team_name}" avec succès.')
    
    if request.headers.get('HX-Request'):
        return HttpResponse("""
            <script>
                location.reload();
            </script>
        """)
    
    return redirect('team_list')


# =============================================================================
# Team API Endpoints
# =============================================================================

@login_required
@viewer_required
def api_team_positions(request, team_id):
    """API endpoint to get positions for a team"""
    team = get_object_or_404(Team, id=team_id)
    positions = TeamPosition.objects.filter(team=team).select_related('function')
    
    positions_data = []
    for position in positions:
        current_agent = position.current_agent
        current_rotation = position.current_rotation_plan
        
        position_data = {
            'id': position.id,
            'function': {
                'id': position.function.id,
                'designation': position.function.designation,
                'description': position.function.description,
                'status': position.function.status,
            },
            'current_agent': {
                'id': current_agent.id,
                'matricule': current_agent.matricule,
                'first_name': current_agent.first_name,
                'last_name': current_agent.last_name,
                'grade': current_agent.grade,
            } if current_agent else None,
            'current_rotation_plan': {
                'id': current_rotation.id,
                'name': current_rotation.name,
                'type': current_rotation.type,
                'break_times': current_rotation.break_times,
            } if current_rotation else None,
            'considers_holidays': position.considers_holidays,
        }
        positions_data.append(position_data)
    
    return JsonResponse({'positions': positions_data})


# Team Export/Import Functions

@user_passes_test(is_superuser)
def team_export(request):
    """Export teams to JSON file - only accessible to superusers"""
    teams = Team.objects.all()
    
    # Prepare data for export
    export_data = []
    for team in teams:
        team_data = {
            'designation': team.designation,
            'description': team.description,
            'color': team.color,
            'department': {
                'name': team.department.name,
                'order': team.department.order,
            },
            'created_at': team.created_at.isoformat() if team.created_at else None,
            'updated_at': team.updated_at.isoformat() if team.updated_at else None,
        }
        export_data.append(team_data)
    
    # Generate filename with current date (timezone-aware)
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_teams.json"
    
    # Create response
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def team_import(request):
    """Import teams from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_team_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_team_changelist')
        
        try:
            # Parse JSON content
            file_content = import_file.read().decode('utf-8')
            teams_data = json.loads(file_content)
            
            if not isinstance(teams_data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste d\'équipes.')
                return redirect('admin:core_team_changelist')
            
            # Count existing records
            existing_count = Team.objects.count()
            
            # Delete existing teams
            Team.objects.all().delete()
            
            # Import new teams
            imported_count = 0
            for team_data in teams_data:
                try:
                    # Get or create department
                    department_data = team_data.get('department', {})
                    department, created = Department.objects.get_or_create(
                        name=department_data.get('name'),
                        defaults={'order': department_data.get('order', 10)}
                    )
                    
                    # Create team
                    Team.objects.create(
                        designation=team_data.get('designation'),
                        description=team_data.get('description', ''),
                        color=team_data.get('color'),
                        department=department
                    )
                    imported_count += 1
                    
                except Exception as e:
                    messages.warning(request, f'Erreur lors de l\'importation de l\'équipe "{team_data.get("designation", "Inconnue")}" : {str(e)}')
                    continue
            
            messages.success(request, f'Importation terminée : {imported_count} équipe(s) importée(s), {existing_count} équipe(s) supprimée(s).')
            
        except json.JSONDecodeError:
            messages.error(request, 'Erreur lors de la lecture du fichier JSON. Vérifiez le format du fichier.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation : {str(e)}')
    
    return redirect('admin:core_team_changelist')


# TeamPosition Export/Import Functions

@user_passes_test(is_superuser)
def teamposition_export(request):
    """Export team positions to JSON file - only accessible to superusers"""
    positions = TeamPosition.objects.all()
    
    # Prepare data for export
    export_data = []
    for position in positions:
        current_agent = position.current_agent
        current_rotation = position.current_rotation_plan
        
        position_data = {
            'team': {
                'designation': position.team.designation,
                'department_name': position.team.department.name,
            },
            'function': {
                'designation': position.function.designation,
                'description': position.function.description,
            },
            'current_agent': {
                'matricule': current_agent.matricule,
                'first_name': current_agent.first_name,
                'last_name': current_agent.last_name,
                'grade': current_agent.grade,
            } if current_agent else None,
            'current_rotation_plan': {
                'name': current_rotation.name,
                'type': current_rotation.type,
                'break_times': current_rotation.break_times,
            } if current_rotation else None,
            'considers_holidays': position.considers_holidays,
            'order': position.order,
            'created_at': position.created_at.isoformat() if position.created_at else None,
            'updated_at': position.updated_at.isoformat() if position.updated_at else None,
        }
        export_data.append(position_data)
    
    # Generate filename with current date (timezone-aware)
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_team_positions.json"
    
    # Create response
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def teamposition_import(request):
    """Import team positions from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_teamposition_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_teamposition_changelist')
        
        try:
            # Parse JSON content
            file_content = import_file.read().decode('utf-8')
            positions_data = json.loads(file_content)
            
            if not isinstance(positions_data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste de postes d\'équipe.')
                return redirect('admin:core_teamposition_changelist')
            
            # Count existing records
            existing_count = TeamPosition.objects.count()
            
            # Delete existing positions
            TeamPosition.objects.all().delete()
            
            # Import new positions
            imported_count = 0
            for position_data in positions_data:
                try:
                    # Get team
                    team_data = position_data.get('team', {})
                    team = Team.objects.filter(
                        designation=team_data.get('designation'),
                        department__name=team_data.get('department_name')
                    ).first()
                    
                    if not team:
                        messages.warning(request, f'Équipe "{team_data.get("designation")}" non trouvée, position ignorée.')
                        continue
                    
                    # Get function
                    function_data = position_data.get('function', {})
                    function = Function.objects.filter(
                        designation=function_data.get('designation')
                    ).first()
                    
                    if not function:
                        messages.warning(request, f'Fonction "{function_data.get("designation")}" non trouvée, position ignorée.')
                        continue
                    
                    # Create position (affectations se gèrent séparément)
                    TeamPosition.objects.create(
                        team=team,
                        function=function,
                        considers_holidays=position_data.get('considers_holidays', True),
                        order=position_data.get('order', 1),
                    )
                    imported_count += 1
                    
                except Exception as e:
                    messages.warning(request, f'Erreur lors de l\'importation du poste : {str(e)}')
                    continue
            
            messages.success(request, f'Importation terminée : {imported_count} poste(s) importé(s), {existing_count} poste(s) supprimé(s).')
            
        except json.JSONDecodeError:
            messages.error(request, 'Erreur lors de la lecture du fichier JSON. Vérifiez le format du fichier.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation : {str(e)}')
    
    return redirect('admin:core_teamposition_changelist')


# PublicHoliday Export/Import Functions

@user_passes_test(is_superuser)
def publicholiday_export(request):
    """Export public holidays to JSON file - only accessible to superusers"""
    holidays = PublicHoliday.objects.all()
    
    # Prepare data for export
    export_data = []
    for holiday in holidays:
        holiday_data = {
            'designation': holiday.designation,
            'date': holiday.date.isoformat() if holiday.date else None,
            'created_at': holiday.created_at.isoformat() if holiday.created_at else None,
            'updated_at': holiday.updated_at.isoformat() if holiday.updated_at else None,
        }
        export_data.append(holiday_data)
    
    # Generate filename with current date (timezone-aware)
    current_date = timezone.now().strftime('%Y-%m-%d')
    filename = f"{current_date}_public_holidays.json"
    
    # Create response
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@user_passes_test(is_superuser)
@transaction.atomic
def publicholiday_import(request):
    """Import public holidays from JSON file - overwrites existing database - only accessible to superusers"""
    if request.method == 'POST':
        import_file = request.FILES.get('import_file')
        
        if not import_file:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:core_publicholiday_changelist')
        
        # Validate file type
        if not import_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('admin:core_publicholiday_changelist')
        
        try:
            # Parse JSON content
            file_content = import_file.read().decode('utf-8')
            holidays_data = json.loads(file_content)
            
            if not isinstance(holidays_data, list):
                messages.error(request, 'Le fichier JSON doit contenir une liste de jours fériés.')
                return redirect('admin:core_publicholiday_changelist')
            
            # Count existing records
            existing_count = PublicHoliday.objects.count()
            
            # Delete existing holidays
            PublicHoliday.objects.all().delete()
            
            # Import new holidays
            imported_count = 0
            for holiday_data in holidays_data:
                try:
                    # Parse date
                    date = None
                    if holiday_data.get('date'):
                        date = datetime.fromisoformat(holiday_data['date']).date()
                    
                    # Create holiday
                    PublicHoliday.objects.create(
                        designation=holiday_data.get('designation'),
                        date=date
                    )
                    imported_count += 1
                    
                except Exception as e:
                    messages.warning(request, f'Erreur lors de l\'importation du jour férié "{holiday_data.get("designation", "Inconnu")}" : {str(e)}')
                    continue
            
            messages.success(request, f'Importation terminée : {imported_count} jour(s) férié(s) importé(s), {existing_count} jour(s) férié(s) supprimé(s).')
            
        except json.JSONDecodeError:
            messages.error(request, 'Erreur lors de la lecture du fichier JSON. Vérifiez le format du fichier.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'importation : {str(e)}')
    
    return redirect('admin:core_publicholiday_changelist')


# Team Position Assignment Views
@admin_required
@require_http_methods(["POST"])
def update_agent_assignment(request, assignment_id):
    """Update agent assignment dates via AJAX"""
    assignment = get_object_or_404(TeamPositionAgentAssignment, id=assignment_id)
    
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse({'success': False, 'error': 'Dates manquantes'}, status=400)
    
    try:
        from datetime import datetime
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date_obj >= end_date_obj:
            return JsonResponse({'success': False, 'error': 'La date de fin doit être postérieure à la date de début'}, status=400)
        
        # Check for overlapping assignments
        overlapping = TeamPositionAgentAssignment.objects.filter(
            team_position=assignment.team_position,
            start_date__lte=end_date_obj,
            end_date__gte=start_date_obj
        ).exclude(id=assignment.id)
        
        if overlapping.exists():
            return JsonResponse({'success': False, 'error': 'Cette période chevauche avec une autre affectation'}, status=400)
        
        assignment.start_date = start_date_obj
        assignment.end_date = end_date_obj
        assignment.save()
        
        return JsonResponse({
            'success': True, 
            'start_date': start_date_obj.strftime('%d/%m/%Y'),
            'end_date': end_date_obj.strftime('%d/%m/%Y')
        })
        
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Format de date invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def update_rotation_assignment(request, assignment_id):
    """Update rotation assignment dates via AJAX"""
    assignment = get_object_or_404(TeamPositionRotationAssignment, id=assignment_id)
    
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse({'success': False, 'error': 'Dates manquantes'}, status=400)
    
    try:
        from datetime import datetime
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date_obj >= end_date_obj:
            return JsonResponse({'success': False, 'error': 'La date de fin doit être postérieure à la date de début'}, status=400)
        
        # Check for overlapping assignments
        overlapping = TeamPositionRotationAssignment.objects.filter(
            team_position=assignment.team_position,
            start_date__lte=end_date_obj,
            end_date__gte=start_date_obj
        ).exclude(id=assignment.id)
        
        if overlapping.exists():
            return JsonResponse({'success': False, 'error': 'Cette période chevauche avec une autre affectation'}, status=400)
        
        assignment.start_date = start_date_obj
        assignment.end_date = end_date_obj
        assignment.save()
        
        return JsonResponse({
            'success': True, 
            'start_date': start_date_obj.strftime('%d/%m/%Y'),
            'end_date': end_date_obj.strftime('%d/%m/%Y')
        })
        
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Format de date invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def delete_agent_assignment(request, assignment_id):
    """Delete agent assignment via AJAX"""
    assignment = get_object_or_404(TeamPositionAgentAssignment, id=assignment_id)
    
    try:
        assignment.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def delete_rotation_assignment(request, assignment_id):
    """Delete rotation assignment via AJAX"""
    assignment = get_object_or_404(TeamPositionRotationAssignment, id=assignment_id)
    
    try:
        assignment.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def create_agent_assignment(request, position_id):
    """Create new agent assignment via AJAX"""
    position = get_object_or_404(TeamPosition, id=position_id)
    
    agent_id = request.POST.get('agent_id')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    if not agent_id or not start_date or not end_date:
        return JsonResponse({'success': False, 'error': 'Tous les champs sont requis'}, status=400)
    
    try:
        from datetime import datetime
        agent = get_object_or_404(Agent, id=agent_id)
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date_obj >= end_date_obj:
            return JsonResponse({'success': False, 'error': 'La date de fin doit être postérieure à la date de début'}, status=400)
        
        # Check for overlapping assignments for this position
        overlapping = TeamPositionAgentAssignment.objects.filter(
            team_position=position,
            start_date__lte=end_date_obj,
            end_date__gte=start_date_obj
        )
        
        if overlapping.exists():
            return JsonResponse({'success': False, 'error': 'Cette période chevauche avec une autre affectation d\'agent'}, status=400)
        
        # Create the new assignment
        assignment = TeamPositionAgentAssignment.objects.create(
            team_position=position,
            agent=agent,
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        
        return JsonResponse({'success': True, 'assignment_id': assignment.id})
        
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Format de date invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def create_rotation_assignment(request, position_id):
    """Create new rotation assignment via AJAX"""
    position = get_object_or_404(TeamPosition, id=position_id)
    
    rotation_id = request.POST.get('rotation_id')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    if not rotation_id or not start_date or not end_date:
        return JsonResponse({'success': False, 'error': 'Tous les champs sont requis'}, status=400)
    
    try:
        from datetime import datetime
        rotation_plan = get_object_or_404(ShiftSchedule, id=rotation_id)
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date_obj >= end_date_obj:
            return JsonResponse({'success': False, 'error': 'La date de fin doit être postérieure à la date de début'}, status=400)
        
        # Check for overlapping assignments for this position
        overlapping = TeamPositionRotationAssignment.objects.filter(
            team_position=position,
            start_date__lte=end_date_obj,
            end_date__gte=start_date_obj
        )
        
        if overlapping.exists():
            return JsonResponse({'success': False, 'error': 'Cette période chevauche avec une autre affectation de roulement'}, status=400)
        
        # Create the new assignment
        assignment = TeamPositionRotationAssignment.objects.create(
            team_position=position,
            rotation_plan=rotation_plan,
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        
        return JsonResponse({'success': True, 'assignment_id': assignment.id})
        
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Format de date invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
