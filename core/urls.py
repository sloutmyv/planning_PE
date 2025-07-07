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
    path('daily-rotation-plan-count/', views.daily_rotation_plan_count, name='daily_rotation_plan_count'),
    path('rotation-period-count/', views.rotation_period_count, name='rotation_period_count'),
    
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
    
    # DailyRotationPlan URLs
    path('daily-rotation-plans/', views.daily_rotation_plan_list, name='daily_rotation_plan_list'),
    path('daily-rotation-plans/create/', views.daily_rotation_plan_create, name='daily_rotation_plan_create'),
    path('daily-rotation-plans/<int:pk>/', views.daily_rotation_plan_detail, name='daily_rotation_plan_detail'),
    path('daily-rotation-plans/<int:pk>/edit/', views.daily_rotation_plan_edit, name='daily_rotation_plan_edit'),
    path('daily-rotation-plans/<int:pk>/delete/', views.daily_rotation_plan_delete, name='daily_rotation_plan_delete'),
    
    # RotationPeriod URLs
    path('rotation-periods/', views.rotation_period_list, name='rotation_period_list'),
    path('rotation-periods/create/', views.rotation_period_create, name='rotation_period_create'),
    path('rotation-periods/<int:pk>/edit/', views.rotation_period_edit, name='rotation_period_edit'),
    path('rotation-periods/<int:pk>/delete/', views.rotation_period_delete, name='rotation_period_delete'),
    
    # API endpoints for periods
    path('api/plans/<int:plan_id>/periods/', views.api_plan_periods, name='api_plan_periods'),
]