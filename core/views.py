from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Agent, Function
from .forms import AgentForm, FunctionForm


def index(request):
    """Homepage with schedule placeholder"""
    return render(request, 'core/index.html')


def is_staff_user(user):
    """Check if user is staff member"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user)
def agent_count(request):
    """HTMX endpoint for agent count"""
    count = Agent.objects.count()
    return HttpResponse(f'<p class="text-2xl font-semibold text-gray-900" id="agent-count">{count}</p>')


@login_required
@user_passes_test(is_staff_user)
def function_count(request):
    """HTMX endpoint for function count"""
    count = Function.objects.count()
    return HttpResponse(f'<p class="text-2xl font-semibold text-gray-900" id="function-count">{count}</p>')


# Agent Views
@login_required
@user_passes_test(is_staff_user)
def agent_list(request):
    """List all agents with search and pagination"""
    search_query = request.GET.get('search', '')
    agents = Agent.objects.all()
    
    if search_query:
        agents = agents.filter(
            matricule__icontains=search_query
        ) | agents.filter(
            first_name__icontains=search_query
        ) | agents.filter(
            last_name__icontains=search_query
        )
    
    paginator = Paginator(agents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/agents/agent_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query
        })
    
    return render(request, 'core/agents/agent_list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })


@login_required
@user_passes_test(is_staff_user)
def agent_create(request):
    """Create new agent"""
    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            agent = form.save()
            messages.success(request, f'Agent {agent.matricule} créé avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Agent {agent.matricule} créé avec succès.</div>'
                    '<script>setTimeout(() => { document.dispatchEvent(new CustomEvent("closeCreateForm")); location.reload(); }, 1000)</script>'
                )
            return redirect('agent_list')
    else:
        form = AgentForm()
    
    return render(request, 'core/agents/agent_form.html', {
        'form': form,
        'title': 'Créer un Agent',
        'is_htmx': request.headers.get('HX-Request')
    })


@login_required
@user_passes_test(is_staff_user)
def agent_detail(request, pk):
    """Agent detail view"""
    agent = get_object_or_404(Agent, pk=pk)
    return render(request, 'core/agents/agent_detail.html', {'agent': agent})


@login_required
@user_passes_test(is_staff_user)
def agent_edit(request, pk):
    """Edit existing agent"""
    agent = get_object_or_404(Agent, pk=pk)
    
    if request.method == 'POST':
        form = AgentForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, f'Agent {agent.matricule} modifié avec succès.')
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Agent {agent.matricule} modifié avec succès.</div>'
                    '<script>setTimeout(() => window.location.reload(), 1000)</script>'
                )
            return redirect('agent_list')
    else:
        form = AgentForm(instance=agent)
    
    return render(request, 'core/agents/agent_form.html', {
        'form': form,
        'agent': agent,
        'title': f'Modifier {agent.matricule}',
        'is_htmx': request.headers.get('HX-Request')
    })


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["DELETE"])
def agent_delete(request, pk):
    """Delete agent"""
    agent = get_object_or_404(Agent, pk=pk)
    matricule = agent.matricule
    agent.delete()
    
    if request.headers.get('HX-Request'):
        return HttpResponse(
            f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Agent {matricule} supprimé avec succès.</div>'
            '<script>setTimeout(() => window.location.reload(), 1000)</script>'
        )
    
    messages.success(request, f'Agent {matricule} supprimé avec succès.')
    return redirect('agent_list')


# Function Views
@login_required
@user_passes_test(is_staff_user)
def function_list(request):
    """List all functions with search and pagination"""
    search_query = request.GET.get('search', '')
    functions = Function.objects.all()
    
    if search_query:
        functions = functions.filter(
            designation__icontains=search_query
        ) | functions.filter(
            description__icontains=search_query
        )
    
    paginator = Paginator(functions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/functions/function_list_partial.html', {
            'page_obj': page_obj,
            'search_query': search_query
        })
    
    return render(request, 'core/functions/function_list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })


@login_required
@user_passes_test(is_staff_user)
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
                    '<script>setTimeout(() => { document.dispatchEvent(new CustomEvent("closeFunctionCreateForm")); location.reload(); }, 1000)</script>'
                )
            return redirect('function_list')
    else:
        form = FunctionForm()
    
    return render(request, 'core/functions/function_form.html', {
        'form': form,
        'title': 'Créer une Fonction',
        'is_htmx': request.headers.get('HX-Request')
    })


@login_required
@user_passes_test(is_staff_user)
def function_detail(request, pk):
    """Function detail view"""
    function = get_object_or_404(Function, pk=pk)
    return render(request, 'core/functions/function_detail.html', {'function': function})


@login_required
@user_passes_test(is_staff_user)
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
                    '<script>setTimeout(() => window.location.reload(), 1000)</script>'
                )
            return redirect('function_list')
    else:
        form = FunctionForm(instance=function)
    
    return render(request, 'core/functions/function_form.html', {
        'form': form,
        'function': function,
        'title': f'Modifier "{function.designation}"',
        'is_htmx': request.headers.get('HX-Request')
    })


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["DELETE"])
def function_delete(request, pk):
    """Delete function"""
    function = get_object_or_404(Function, pk=pk)
    designation = function.designation
    function.delete()
    
    if request.headers.get('HX-Request'):
        return HttpResponse(
            f'<div class="p-4 mb-4 text-green-800 bg-green-100 rounded-lg">Fonction "{designation}" supprimée avec succès.</div>'
            '<script>setTimeout(() => window.location.reload(), 1000)</script>'
        )
    
    messages.success(request, f'Fonction "{designation}" supprimée avec succès.')
    return redirect('function_list')
