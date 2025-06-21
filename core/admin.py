from django.contrib import admin
from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'first_name', 'last_name', 'grade', 'hire_date', 'departure_date')
    list_filter = ('grade', 'hire_date', 'departure_date')
    search_fields = ('matricule', 'first_name', 'last_name')
    ordering = ('matricule',)
    date_hierarchy = 'hire_date'
