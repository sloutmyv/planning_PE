from django.urls import path
from . import views

urlpatterns = [
    # Homepage
    path('', views.index, name='index'),
    
    # HTMX endpoints for dashboard stats
    path('agent-count/', views.agent_count, name='agent_count'),
    path('function-count/', views.function_count, name='function_count'),
    
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
]