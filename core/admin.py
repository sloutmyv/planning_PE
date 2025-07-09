from django.contrib import admin
from .models import (Agent, Function, ScheduleType, DailyRotationPlan, RotationPeriod,
                     ShiftSchedule, ShiftSchedulePeriod, ShiftScheduleWeek, ShiftScheduleDailyPlan)


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
