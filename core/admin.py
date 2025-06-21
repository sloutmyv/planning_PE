from django.contrib import admin
from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'first_name', 'last_name', 'grade')
    list_filter = ('grade',)
    search_fields = ('matricule', 'first_name', 'last_name')
    ordering = ('matricule',)
