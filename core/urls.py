from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Homepage
    path('', views.index, name='index'),
    
    # User Manual
    path('user-manual/', views.user_manual, name='user_manual'),
    
    # HTMX endpoints for dashboard stats
    path('agent-count/', views.agent_count, name='agent_count'),
    path('function-count/', views.function_count, name='function_count'),
    path('schedule-type-count/', views.schedule_type_count, name='schedule_type_count'),
    path('daily-rotation-plan-count/', views.daily_rotation_plan_count, name='daily_rotation_plan_count'),
    path('rotation-period-count/', views.rotation_period_count, name='rotation_period_count'),
    path('public-holiday-count/', views.public_holiday_count, name='public_holiday_count'),
    path('department-count/', views.department_count, name='department_count'),
    path('team-count/', views.team_count, name='team_count'),
    
    # Agent URLs
    path('agents/', views.agent_list, name='agent_list'),
    path('agents/create/', views.agent_create, name='agent_create'),
    path('agents/<int:pk>/', views.agent_detail, name='agent_detail'),
    path('agents/<int:pk>/edit/', views.agent_edit, name='agent_edit'),
    path('agents/<int:pk>/delete/', views.agent_delete, name='agent_delete'),
    # Export/Import URLs are now handled by Django admin interface only
    
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
    
    # API endpoints for plans
    path('api/daily-rotation-plans/', views.api_daily_rotation_plans, name='api_daily_rotation_plans'),
    path('api/shift-schedule-weeks/<int:week_id>/assign-daily-plan/<int:weekday>/', views.api_assign_daily_plan, name='api_assign_daily_plan'),
    
    # API endpoints for periods
    path('api/plans/<int:plan_id>/periods/', views.api_plan_periods, name='api_plan_periods'),
    path('api/shift-schedules/<int:schedule_id>/periods/', views.api_shift_schedule_periods, name='api_shift_schedule_periods'),
    
    # API endpoints for weeks
    path('api/shift-schedule-periods/<int:period_id>/weeks/', views.api_shift_schedule_period_weeks, name='api_shift_schedule_period_weeks'),
    
    # Shift Schedule URLs
    path('shift-schedules/', views.shift_schedule_list, name='shift_schedule_list'),
    path('shift-schedules/create/', views.shift_schedule_create, name='shift_schedule_create'),
    path('shift-schedules/<int:schedule_id>/edit/', views.shift_schedule_edit, name='shift_schedule_edit'),
    path('shift-schedules/<int:schedule_id>/delete/', views.shift_schedule_delete, name='shift_schedule_delete'),
    
    # Shift Schedule Period URLs
    path('shift-schedules/<int:schedule_id>/periods/create/', views.shift_schedule_period_create, name='shift_schedule_period_create'),
    path('shift-schedule-periods/<int:period_id>/edit/', views.shift_schedule_period_edit, name='shift_schedule_period_edit'),
    path('shift-schedule-periods/<int:period_id>/delete/', views.shift_schedule_period_delete, name='shift_schedule_period_delete'),
    path('shift-schedule-periods/<int:period_id>/duplicate/', views.shift_schedule_period_duplicate, name='shift_schedule_period_duplicate'),
    
    # Shift Schedule Week URLs
    path('shift-schedule-periods/<int:period_id>/weeks/create/', views.shift_schedule_week_create, name='shift_schedule_week_create'),
    path('shift-schedule-weeks/<int:week_id>/edit/', views.shift_schedule_week_edit, name='shift_schedule_week_edit'),
    path('shift-schedule-weeks/<int:week_id>/delete/', views.shift_schedule_week_delete, name='shift_schedule_week_delete'),
    path('shift-schedule-weeks/<int:week_id>/duplicate/', views.shift_schedule_week_duplicate, name='shift_schedule_week_duplicate'),
    
    # Shift Schedule Daily Plan URLs
    path('shift-schedule-weeks/<int:week_id>/daily-plans/create/<int:weekday>/', views.shift_schedule_daily_plan_create, name='shift_schedule_daily_plan_create'),
    path('shift-schedule-daily-plans/<int:daily_plan_id>/edit/', views.shift_schedule_daily_plan_edit, name='shift_schedule_daily_plan_edit'),
    path('shift-schedule-daily-plans/<int:daily_plan_id>/delete/', views.shift_schedule_daily_plan_delete, name='shift_schedule_daily_plan_delete'),
    
    # Public Holiday URLs
    path('public-holidays/', views.public_holiday_list, name='public_holiday_list'),
    path('public-holidays/create/', views.public_holiday_create, name='public_holiday_create'),
    path('public-holidays/<int:pk>/', views.public_holiday_detail, name='public_holiday_detail'),
    path('public-holidays/<int:pk>/edit/', views.public_holiday_edit, name='public_holiday_edit'),
    path('public-holidays/<int:pk>/duplicate/', views.public_holiday_duplicate, name='public_holiday_duplicate'),
    path('public-holidays/<int:pk>/delete/', views.public_holiday_delete, name='public_holiday_delete'),
    
    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    
    # Team URLs
    path('teams/', views.team_list, name='team_list'),
    path('teams/create/', views.team_create, name='team_create'),
    path('teams/<int:team_id>/edit/', views.team_edit, name='team_edit'),
    path('teams/<int:team_id>/delete/', views.team_delete, name='team_delete'),
    
    # Team Position URLs
    path('teams/<int:team_id>/positions/create/', views.team_position_create, name='team_position_create'),
    path('team-positions/<int:position_id>/edit/', views.team_position_edit, name='team_position_edit'),
    path('team-positions/<int:position_id>/delete/', views.team_position_delete, name='team_position_delete'),
    
    # Team Position Assignment URLs
    path('agent-assignments/<int:assignment_id>/update/', views.update_agent_assignment, name='update_agent_assignment'),
    path('rotation-assignments/<int:assignment_id>/update/', views.update_rotation_assignment, name='update_rotation_assignment'),
    path('agent-assignments/<int:assignment_id>/delete/', views.delete_agent_assignment, name='delete_agent_assignment'),
    path('rotation-assignments/<int:assignment_id>/delete/', views.delete_rotation_assignment, name='delete_rotation_assignment'),
    path('team-positions/<int:position_id>/agent-assignments/create/', views.create_agent_assignment, name='create_agent_assignment'),
    path('team-positions/<int:position_id>/rotation-assignments/create/', views.create_rotation_assignment, name='create_rotation_assignment'),
    
    # API endpoints for teams
    path('api/teams/<int:team_id>/positions/', views.api_team_positions, name='api_team_positions'),
    
    # Global Export URL
    path('global-export/', views.global_export, name='global_export'),
]