from django.contrib import admin
from .models import Agent, Function, ScheduleType


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'first_name', 'last_name', 'grade', 'hire_date', 'departure_date')
    list_filter = ('grade', 'hire_date', 'departure_date')
    search_fields = ('matricule', 'first_name', 'last_name')
    ordering = ('matricule',)
    date_hierarchy = 'hire_date'


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ('designation', 'status')
    list_filter = ('status',)
    search_fields = ('designation', 'description')
    ordering = ('designation',)


@admin.register(ScheduleType)
class ScheduleTypeAdmin(admin.ModelAdmin):
    list_display = ('designation', 'short_designation', 'color', 'color_preview')
    search_fields = ('designation', 'short_designation')
    ordering = ('designation',)
    
    def color_preview(self, obj):
        """Display color preview in admin list"""
        return f'<div style="width: 20px; height: 20px; background-color: {obj.color}; border: 1px solid #ccc; display: inline-block;"></div>'
    color_preview.allow_tags = True
    color_preview.short_description = 'Aperçu'
