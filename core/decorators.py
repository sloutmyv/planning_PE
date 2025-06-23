from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect
from functools import wraps
from .models import Agent


def get_agent_from_user(user):
    """Get Agent instance from User"""
    try:
        return Agent.objects.get(user=user)
    except Agent.DoesNotExist:
        return None


def permission_required(permission_level):
    """
    Decorator to check user permission level
    permission_level can be: 'viewer', 'editor', 'admin', 'super_admin'
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            agent = get_agent_from_user(request.user)
            
            if not agent:
                # User is not an agent, only allow super admin access via Django admin
                if request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                raise Http404
            
            # Check if user needs to change password
            if not agent.password_changed and request.path != '/change-password/':
                return redirect('change_password')
            
            # Check permission level
            permission_checks = {
                'viewer': agent.is_viewer,
                'editor': agent.is_editor,
                'admin': agent.is_admin,
                'super_admin': agent.is_super_admin,
            }
            
            if permission_level in permission_checks:
                if permission_checks[permission_level]():
                    return view_func(request, *args, **kwargs)
            
            raise Http404
        
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Shortcut decorator for admin permission"""
    return permission_required('admin')(view_func)


def editor_required(view_func):
    """Shortcut decorator for editor permission"""
    return permission_required('editor')(view_func)


def viewer_required(view_func):
    """Shortcut decorator for viewer permission"""
    return permission_required('viewer')(view_func)


def super_admin_required(view_func):
    """Shortcut decorator for super admin permission"""
    return permission_required('super_admin')(view_func)