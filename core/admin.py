from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (Agent, Function, ScheduleType, DailyRotationPlan, RotationPeriod,
                     ShiftSchedule, ShiftSchedulePeriod, ShiftScheduleWeek, ShiftScheduleDailyPlan, 
                     Department, Team, TeamPosition, PublicHoliday, TeamPositionAgentAssignment, TeamPositionRotationAssignment)
from .views import (agent_export, agent_import, department_export, department_import, function_export, function_import, 
                    scheduletype_export, scheduletype_import, dailyrotationplan_export, dailyrotationplan_import, 
                    shiftschedule_export, shiftschedule_import, shiftscheduleperiod_export, shiftscheduleperiod_import, 
                    rotationperiod_export, rotationperiod_import, shiftscheduleweek_export, shiftscheduleweek_import, 
                    shiftscheduledailyplan_export, shiftscheduledailyplan_import, team_export, team_import, 
                    teamposition_export, teamposition_import, publicholiday_export, publicholiday_import)
import json


def is_superuser(user):
    """Check if user is a superuser"""
    return user.is_authenticated and user.is_superuser


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'first_name', 'last_name', 'grade', 'hire_date', 'departure_date')
    list_filter = ('grade', 'hire_date', 'departure_date')
    search_fields = ('matricule', 'first_name', 'last_name')
    ordering = ('matricule',)
    date_hierarchy = 'hire_date'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_agents), name='core_agent_export'),
            path('import/', self.admin_site.admin_view(self.import_agents), name='core_agent_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_agents(self, request):
        """Export agents to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les agents.')
            return redirect('admin:core_agent_changelist')
        return agent_export(request)
    
    def import_agents(self, request):
        """Import agents from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les agents.')
            return redirect('admin:core_agent_changelist')
            
        if request.method == 'POST':
            return agent_import(request)
        
        # Show the import form
        return render(request, 'admin/core/agent/import_form.html', {
            'title': 'Importer des agents',
            'opts': self.model._meta,
            'has_change_permission': True,
            'agent_count': Agent.objects.count(),
        })


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ('designation', 'status')
    list_filter = ('status',)
    search_fields = ('designation', 'description')
    ordering = ('designation',)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_functions), name='core_function_export'),
            path('import/', self.admin_site.admin_view(self.import_functions), name='core_function_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_functions(self, request):
        """Export functions to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les fonctions.')
            return redirect('admin:core_function_changelist')
        return function_export(request)
    
    def import_functions(self, request):
        """Import functions from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les fonctions.')
            return redirect('admin:core_function_changelist')
            
        if request.method == 'POST':
            return function_import(request)
        
        # Show the import form
        return render(request, 'admin/core/function/import_form.html', {
            'title': 'Importer des fonctions',
            'opts': self.model._meta,
            'has_change_permission': True,
            'function_count': Function.objects.count(),
        })


@admin.register(ScheduleType)
class ScheduleTypeAdmin(admin.ModelAdmin):
    list_display = ('designation', 'short_designation', 'color', 'color_preview')
    search_fields = ('designation', 'short_designation')
    ordering = ('designation',)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_scheduletypes), name='core_scheduletype_export'),
            path('import/', self.admin_site.admin_view(self.import_scheduletypes), name='core_scheduletype_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_scheduletypes(self, request):
        """Export schedule types to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les types d\'horaires.')
            return redirect('admin:core_scheduletype_changelist')
        return scheduletype_export(request)
    
    def import_scheduletypes(self, request):
        """Import schedule types from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les types d\'horaires.')
            return redirect('admin:core_scheduletype_changelist')
            
        if request.method == 'POST':
            return scheduletype_import(request)
        
        # Show the import form
        return render(request, 'admin/core/scheduletype/import_form.html', {
            'title': 'Importer des types d\'horaires',
            'opts': self.model._meta,
            'has_change_permission': True,
            'scheduletype_count': ScheduleType.objects.count(),
        })
    
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
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_dailyrotationplans), name='core_dailyrotationplan_export'),
            path('import/', self.admin_site.admin_view(self.import_dailyrotationplans), name='core_dailyrotationplan_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_dailyrotationplans(self, request):
        """Export daily rotation plans to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les rythmes quotidiens.')
            return redirect('admin:core_dailyrotationplan_changelist')
        return dailyrotationplan_export(request)
    
    def import_dailyrotationplans(self, request):
        """Import daily rotation plans from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les rythmes quotidiens.')
            return redirect('admin:core_dailyrotationplan_changelist')
            
        if request.method == 'POST':
            return dailyrotationplan_import(request)
        
        # Show the import form
        return render(request, 'admin/core/dailyrotationplan/import_form.html', {
            'title': 'Importer des rythmes quotidiens',
            'opts': self.model._meta,
            'has_change_permission': True,
            'dailyrotationplan_count': DailyRotationPlan.objects.count(),
        })
    
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
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_rotationperiods), name='core_rotationperiod_export'),
            path('import/', self.admin_site.admin_view(self.import_rotationperiods), name='core_rotationperiod_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_rotationperiods(self, request):
        """Export rotation periods to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les périodes de rotation.')
            return redirect('admin:core_rotationperiod_changelist')
        return rotationperiod_export(request)
    
    def import_rotationperiods(self, request):
        """Import rotation periods from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les périodes de rotation.')
            return redirect('admin:core_rotationperiod_changelist')
            
        if request.method == 'POST':
            return rotationperiod_import(request)
        
        # Show the import form
        return render(request, 'admin/core/rotationperiod/import_form.html', {
            'title': 'Importer des périodes de rotation',
            'opts': self.model._meta,
            'has_change_permission': True,
            'rotationperiod_count': RotationPeriod.objects.count(),
        })
    
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


# Shift Schedule Admin Classes

class ShiftSchedulePeriodInline(admin.TabularInline):
    model = ShiftSchedulePeriod
    extra = 1
    fields = ('start_date', 'end_date')
    ordering = ('start_date',)


@admin.register(ShiftSchedule)
class ShiftScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'break_times', 'created_at', 'updated_at')
    list_filter = ('type', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [ShiftSchedulePeriodInline]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_shiftschedules), name='core_shiftschedule_export'),
            path('import/', self.admin_site.admin_view(self.import_shiftschedules), name='core_shiftschedule_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_shiftschedules(self, request):
        """Export shift schedules to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les plannings de poste.')
            return redirect('admin:core_shiftschedule_changelist')
        return shiftschedule_export(request)
    
    def import_shiftschedules(self, request):
        """Import shift schedules from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les plannings de poste.')
            return redirect('admin:core_shiftschedule_changelist')
            
        if request.method == 'POST':
            return shiftschedule_import(request)
        
        # Show the import form
        return render(request, 'admin/core/shiftschedule/import_form.html', {
            'title': 'Importer des plannings de poste',
            'opts': self.model._meta,
            'has_change_permission': True,
            'shiftschedule_count': ShiftSchedule.objects.count(),
        })
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'type', 'break_times')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


class ShiftScheduleWeekInline(admin.TabularInline):
    model = ShiftScheduleWeek
    extra = 1
    fields = ('week_number',)
    ordering = ('week_number',)


@admin.register(ShiftSchedulePeriod)
class ShiftSchedulePeriodAdmin(admin.ModelAdmin):
    list_display = ('shift_schedule', 'start_date', 'end_date', 'get_duration_days')
    list_filter = ('shift_schedule', 'start_date')
    search_fields = ('shift_schedule__name',)
    ordering = ('shift_schedule', 'start_date')
    date_hierarchy = 'start_date'
    inlines = [ShiftScheduleWeekInline]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_shiftscheduleperiods), name='core_shiftscheduleperiod_export'),
            path('import/', self.admin_site.admin_view(self.import_shiftscheduleperiods), name='core_shiftscheduleperiod_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_shiftscheduleperiods(self, request):
        """Export shift schedule periods to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les périodes de planning de poste.')
            return redirect('admin:core_shiftscheduleperiod_changelist')
        return shiftscheduleperiod_export(request)
    
    def import_shiftscheduleperiods(self, request):
        """Import shift schedule periods from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les périodes de planning de poste.')
            return redirect('admin:core_shiftscheduleperiod_changelist')
            
        if request.method == 'POST':
            return shiftscheduleperiod_import(request)
        
        # Show the import form
        return render(request, 'admin/core/shiftscheduleperiod/import_form.html', {
            'title': 'Importer des périodes de planning de poste',
            'opts': self.model._meta,
            'has_change_permission': True,
            'shiftscheduleperiod_count': ShiftSchedulePeriod.objects.count(),
        })
    
    fieldsets = (
        ('Planning de poste', {
            'fields': ('shift_schedule',)
        }),
        ('Période', {
            'fields': ('start_date', 'end_date')
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_duration_days(self, obj):
        """Display period duration in days"""
        if obj.start_date and obj.end_date:
            duration = (obj.end_date - obj.start_date).days + 1
            return f"{duration} jour{'s' if duration > 1 else ''}"
        return "N/A"
    get_duration_days.short_description = 'Durée'


class ShiftScheduleDailyPlanInline(admin.TabularInline):
    model = ShiftScheduleDailyPlan
    extra = 7  # One for each day of the week
    fields = ('weekday', 'daily_rotation_plan')
    ordering = ('weekday',)


@admin.register(ShiftScheduleWeek)
class ShiftScheduleWeekAdmin(admin.ModelAdmin):
    list_display = ('period', 'week_number', 'get_period_dates')
    list_filter = ('period__shift_schedule', 'week_number')
    search_fields = ('period__shift_schedule__name',)
    ordering = ('period', 'week_number')
    inlines = [ShiftScheduleDailyPlanInline]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_shiftscheduleweeks), name='core_shiftscheduleweek_export'),
            path('import/', self.admin_site.admin_view(self.import_shiftscheduleweeks), name='core_shiftscheduleweek_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_shiftscheduleweeks(self, request):
        """Export shift schedule weeks to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les semaines de planning.')
            return redirect('admin:core_shiftscheduleweek_changelist')
        return shiftscheduleweek_export(request)
    
    def import_shiftscheduleweeks(self, request):
        """Import shift schedule weeks from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les semaines de planning.')
            return redirect('admin:core_shiftscheduleweek_changelist')
            
        if request.method == 'POST':
            return shiftscheduleweek_import(request)
        
        # Show the import form
        return render(request, 'admin/core/shiftscheduleweek/import_form.html', {
            'title': 'Importer des semaines de planning',
            'opts': self.model._meta,
            'has_change_permission': True,
            'shiftscheduleweek_count': ShiftScheduleWeek.objects.count(),
        })
    
    fieldsets = (
        ('Semaine', {
            'fields': ('period', 'week_number')
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_period_dates(self, obj):
        """Display parent period dates"""
        return f"{obj.period.start_date} - {obj.period.end_date}"
    get_period_dates.short_description = 'Période'


@admin.register(ShiftScheduleDailyPlan)
class ShiftScheduleDailyPlanAdmin(admin.ModelAdmin):
    list_display = ('week', 'get_weekday_display', 'daily_rotation_plan', 'get_schedule_type')
    list_filter = ('weekday', 'daily_rotation_plan__schedule_type', 'week__period__shift_schedule')
    search_fields = ('week__period__shift_schedule__name', 'daily_rotation_plan__designation')
    ordering = ('week', 'weekday')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_shiftscheduledailyplans), name='core_shiftscheduledailyplan_export'),
            path('import/', self.admin_site.admin_view(self.import_shiftscheduledailyplans), name='core_shiftscheduledailyplan_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_shiftscheduledailyplans(self, request):
        """Export shift schedule daily plans to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les plans quotidiens de planning.')
            return redirect('admin:core_shiftscheduledailyplan_changelist')
        return shiftscheduledailyplan_export(request)
    
    def import_shiftscheduledailyplans(self, request):
        """Import shift schedule daily plans from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les plans quotidiens de planning.')
            return redirect('admin:core_shiftscheduledailyplan_changelist')
            
        if request.method == 'POST':
            return shiftscheduledailyplan_import(request)
        
        # Show the import form
        return render(request, 'admin/core/shiftscheduledailyplan/import_form.html', {
            'title': 'Importer des plans quotidiens de planning',
            'opts': self.model._meta,
            'has_change_permission': True,
            'shiftscheduledailyplan_count': ShiftScheduleDailyPlan.objects.count(),
        })
    
    fieldsets = (
        ('Assignation', {
            'fields': ('week', 'weekday', 'daily_rotation_plan')
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_weekday_display(self, obj):
        """Display French weekday name"""
        return obj.get_weekday_display_french()
    get_weekday_display.short_description = 'Jour'
    
    def get_schedule_type(self, obj):
        """Display schedule type of the daily rotation plan"""
        return obj.daily_rotation_plan.schedule_type.designation
    get_schedule_type.short_description = 'Type d\'horaire'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('order', 'name')
    date_hierarchy = 'created_at'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_departments), name='core_department_export'),
            path('import/', self.admin_site.admin_view(self.import_departments), name='core_department_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_departments(self, request):
        """Export departments to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les départements.')
            return redirect('admin:core_department_changelist')
        return department_export(request)
    
    def import_departments(self, request):
        """Import departments from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les départements.')
            return redirect('admin:core_department_changelist')
            
        if request.method == 'POST':
            return department_import(request)
        
        # Show the import form
        return render(request, 'admin/core/department/import_form.html', {
            'title': 'Importer des départements',
            'opts': self.model._meta,
            'has_change_permission': True,
            'department_count': Department.objects.count(),
        })


class TeamPositionInline(admin.TabularInline):
    model = TeamPosition
    extra = 1
    fields = ('function', 'order', 'considers_holidays')
    ordering = ('order', 'function__designation')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('designation', 'department', 'color_preview', 'created_at', 'updated_at')
    list_filter = ('department', 'created_at')
    search_fields = ('designation', 'description', 'department__name')
    ordering = ('department__order', 'designation')
    date_hierarchy = 'created_at'
    inlines = [TeamPositionInline]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_teams), name='core_team_export'),
            path('import/', self.admin_site.admin_view(self.import_teams), name='core_team_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_teams(self, request):
        """Export teams to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les équipes.')
            return redirect('admin:core_team_changelist')
        return team_export(request)
    
    def import_teams(self, request):
        """Import teams from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les équipes.')
            return redirect('admin:core_team_changelist')
            
        if request.method == 'POST':
            return team_import(request)
        
        # Show the import form
        return render(request, 'admin/core/team/import_form.html', {
            'title': 'Importer des équipes',
            'opts': self.model._meta,
            'has_change_permission': True,
            'team_count': Team.objects.count(),
        })
    
    def color_preview(self, obj):
        """Display color preview in admin list"""
        return f'<div style="width: 20px; height: 20px; background-color: {obj.color}; border: 1px solid #ccc; display: inline-block;"></div>'
    color_preview.allow_tags = True
    color_preview.short_description = 'Couleur'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('designation', 'description', 'department', 'color')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TeamPosition)
class TeamPositionAdmin(admin.ModelAdmin):
    list_display = ('team', 'function', 'get_current_agent', 'get_current_rotation', 'order', 'considers_holidays')
    list_filter = ('team__department', 'team', 'function', 'considers_holidays', 'created_at')
    search_fields = ('team__designation', 'function__designation')
    ordering = ('team__department__order', 'team__designation', 'order')
    date_hierarchy = 'created_at'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_teampositions), name='core_teamposition_export'),
            path('import/', self.admin_site.admin_view(self.import_teampositions), name='core_teamposition_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_teampositions(self, request):
        """Export team positions to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les postes d\'équipe.')
            return redirect('admin:core_teamposition_changelist')
        return teamposition_export(request)
    
    def import_teampositions(self, request):
        """Import team positions from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les postes d\'équipe.')
            return redirect('admin:core_teamposition_changelist')
            
        if request.method == 'POST':
            return teamposition_import(request)
        
        # Show the import form
        return render(request, 'admin/core/teamposition/import_form.html', {
            'title': 'Importer des postes d\'équipe',
            'opts': self.model._meta,
            'has_change_permission': True,
            'teamposition_count': TeamPosition.objects.count(),
        })
    
    def get_current_agent(self, obj):
        """Display current agent assignment"""
        agent = obj.current_agent
        return agent.matricule if agent else "Aucun agent"
    get_current_agent.short_description = 'Agent actuel'
    
    def get_current_rotation(self, obj):
        """Display current rotation assignment"""
        rotation = obj.current_rotation_plan
        return rotation.name if rotation else "Aucun roulement"
    get_current_rotation.short_description = 'Roulement actuel'
    
    fieldsets = (
        ('Équipe et Fonction', {
            'fields': ('team', 'function', 'order')
        }),
        ('Paramètres', {
            'fields': ('considers_holidays',)
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TeamPositionAgentAssignment)
class TeamPositionAgentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('team_position', 'agent', 'start_date', 'end_date', 'is_active')
    list_filter = ('team_position__team__department', 'team_position__team', 'start_date', 'end_date', 'created_at')
    search_fields = ('team_position__team__designation', 'team_position__function__designation', 'agent__matricule', 'agent__first_name', 'agent__last_name')
    ordering = ('team_position__team__designation', 'team_position__function__designation', '-start_date')
    date_hierarchy = 'start_date'
    
    def is_active(self, obj):
        """Display if assignment is currently active"""
        return obj.is_active()
    is_active.boolean = True
    is_active.short_description = 'Actif'
    
    fieldsets = (
        ('Affectation', {
            'fields': ('team_position', 'agent')
        }),
        ('Période de validité', {
            'fields': ('start_date', 'end_date')
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TeamPositionRotationAssignment)
class TeamPositionRotationAssignmentAdmin(admin.ModelAdmin):
    list_display = ('team_position', 'rotation_plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('team_position__team__department', 'team_position__team', 'start_date', 'end_date', 'created_at')
    search_fields = ('team_position__team__designation', 'team_position__function__designation', 'rotation_plan__name')
    ordering = ('team_position__team__designation', 'team_position__function__designation', '-start_date')
    date_hierarchy = 'start_date'
    
    def is_active(self, obj):
        """Display if assignment is currently active"""
        return obj.is_active()
    is_active.boolean = True
    is_active.short_description = 'Actif'
    
    fieldsets = (
        ('Affectation', {
            'fields': ('team_position', 'rotation_plan')
        }),
        ('Période de validité', {
            'fields': ('start_date', 'end_date')
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    list_display = ('designation', 'date', 'created_at', 'updated_at')
    list_filter = ('date', 'created_at')
    search_fields = ('designation',)
    ordering = ('date',)
    date_hierarchy = 'date'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_publicholidays), name='core_publicholiday_export'),
            path('import/', self.admin_site.admin_view(self.import_publicholidays), name='core_publicholiday_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Only show export/import buttons to superusers
        if request.user.is_superuser:
            extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
    
    def export_publicholidays(self, request):
        """Export public holidays to JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent exporter les jours fériés.')
            return redirect('admin:core_publicholiday_changelist')
        return publicholiday_export(request)
    
    def import_publicholidays(self, request):
        """Import public holidays from JSON - only accessible to superusers"""
        if not request.user.is_superuser:
            messages.error(request, 'Accès refusé. Seuls les superutilisateurs peuvent importer les jours fériés.')
            return redirect('admin:core_publicholiday_changelist')
            
        if request.method == 'POST':
            return publicholiday_import(request)
        
        # Show the import form
        return render(request, 'admin/core/publicholiday/import_form.html', {
            'title': 'Importer des jours fériés',
            'opts': self.model._meta,
            'has_change_permission': True,
            'publicholiday_count': PublicHoliday.objects.count(),
        })
    
    fieldsets = (
        ('Informations du jour férié', {
            'fields': ('designation', 'date')
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
