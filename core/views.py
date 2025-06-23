from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Agent, Function
from .forms import AgentForm, FunctionForm
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
