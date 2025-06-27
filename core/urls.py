from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Homepage
    path('', views.index, name='index'),
    
    # HTMX endpoints for dashboard stats
    path('agent-count/', views.agent_count, name='agent_count'),
    path('function-count/', views.function_count, name='function_count'),
    path('schedule-type-count/', views.schedule_type_count, name='schedule_type_count'),
    
    # Agent URLs
    path('agents/', views.agent_list, name='agent_list'),
    path('agents/create/', views.agent_create, name='agent_create'),
    path('agents/<int:pk>/', views.agent_detail, name='agent_detail'),
    path('agents/<int:pk>/edit/', views.agent_edit, name='agent_edit'),
    path('agents/<int:pk>/delete/', views.agent_delete, name='agent_delete'),
    
    # Function URLs
    path('functions/', views.function_list, name='function_list'),
    path('functions/create/', views.function_create, name='function_create'),
    path('functions/<int:pk>/', views.function_detail, name='function_detail'),
    path('functions/<int:pk>/edit/', views.function_edit, name='function_edit'),
    path('functions/<int:pk>/delete/', views.function_delete, name='function_delete'),
    
    # ScheduleType URLs
    path('schedule-types/', views.schedule_type_list, name='schedule_type_list'),
    path('schedule-types/create/', views.schedule_type_create, name='schedule_type_create'),
    path('schedule-types/<int:pk>/', views.schedule_type_detail, name='schedule_type_detail'),
    path('schedule-types/<int:pk>/edit/', views.schedule_type_edit, name='schedule_type_edit'),
    path('schedule-types/<int:pk>/delete/', views.schedule_type_delete, name='schedule_type_delete'),
    
    # Permission Management URLs (integrated into agent management)
    path('agents/<int:pk>/change-permission/save/', views.change_agent_permission, name='change_agent_permission'),
]