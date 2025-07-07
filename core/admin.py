from django.contrib import admin
from .models import Agent, Function, ScheduleType, DailyRotationPlan, RotationPeriod


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


class RotationPeriodInline(admin.TabularInline):
    model = RotationPeriod
    extra = 1
    fields = ('start_date', 'end_date', 'start_time', 'end_time')
    ordering = ('start_date', 'start_time')


@admin.register(DailyRotationPlan)
class DailyRotationPlanAdmin(admin.ModelAdmin):
    list_display = ('designation', 'schedule_type', 'created_at', 'updated_at')
    list_filter = ('schedule_type', 'created_at')
    search_fields = ('designation', 'description')
    ordering = ('designation',)
    inlines = [RotationPeriodInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('designation', 'description', 'schedule_type')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RotationPeriod)
class RotationPeriodAdmin(admin.ModelAdmin):
    list_display = ('daily_rotation_plan', 'start_date', 'end_date', 'start_time', 'end_time', 'get_duration_display')
    list_filter = ('daily_rotation_plan', 'start_date')
    search_fields = ('daily_rotation_plan__designation',)
    ordering = ('daily_rotation_plan', 'start_date', 'start_time')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Plan de rotation', {
            'fields': ('daily_rotation_plan',)
        }),
        ('Période de validité', {
            'fields': ('start_date', 'end_date')
        }),
        ('Horaires quotidiens', {
            'fields': ('start_time', 'end_time')
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_duration_display(self, obj):
        """Display shift duration in admin list"""
        hours = obj.get_duration_hours()
        return f"{hours:.1f}h"
    get_duration_display.short_description = 'Durée'
