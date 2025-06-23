from .models import Agent


def agent_context(request):
    """Add agent information to template context"""
    context = {
        'current_agent': None,
    }
    
    if request.user.is_authenticated:
        try:
            context['current_agent'] = Agent.objects.get(user=request.user)
        except Agent.DoesNotExist:
            context['current_agent'] = None
    
    return context