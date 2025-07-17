from django import forms
from .models import (Agent, Function, ScheduleType, DailyRotationPlan, RotationPeriod,
                     ShiftSchedule, ShiftSchedulePeriod, ShiftScheduleWeek, ShiftScheduleDailyPlan, PublicHoliday)


class AgentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show permission field to users who can manage permissions
        if user:
            try:
                from .decorators import get_agent_from_user
                current_agent = get_agent_from_user(user)
                if not (current_agent and current_agent.can_manage_permissions()):
                    # Remove permission field if user can't manage permissions
                    if 'permission_level' in self.fields:
                        del self.fields['permission_level']
                else:
                    # Limit permission choices for regular admins
                    if current_agent and not current_agent.is_super_admin():
                        # Regular admins cannot create super admins
                        self.fields['permission_level'].choices = [
                            choice for choice in Agent.PERMISSION_CHOICES if choice[0] != 'S'
                        ]
            except:
                # If there's any error, remove permission field to be safe
                if 'permission_level' in self.fields:
                    del self.fields['permission_level']
    
    class Meta:
        model = Agent
        fields = ['matricule', 'first_name', 'last_name', 'grade', 'permission_level', 'hire_date', 'departure_date']
        widgets = {
            'matricule': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ex: A1234'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Nom de famille'
            }),
            'grade': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'permission_level': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
            'departure_date': forms.DateInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
        }
        labels = {
            'matricule': 'Matricule',
            'first_name': 'Prénom',
            'last_name': 'Nom de famille',
            'grade': 'Collège',
            'permission_level': 'Niveau de permission',
            'hire_date': 'Date d\'embauche',
            'departure_date': 'Date de départ',
        }


class FunctionForm(forms.ModelForm):
    class Meta:
        model = Function
        fields = ['designation', 'description', 'status']
        widgets = {
            'designation': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Nom de la fonction'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Description de la fonction (optionnel)',
                'rows': 3
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
        }
        labels = {
            'designation': 'Désignation',
            'description': 'Description',
            'status': 'Actif',
        }


class ScheduleTypeForm(forms.ModelForm):
    class Meta:
        model = ScheduleType
        fields = ['designation', 'short_designation', 'color']
        widgets = {
            'designation': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Nom du type de planning'
            }),
            'short_designation': forms.TextInput(attrs={
                'class': 'block w-20 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 uppercase',
                'placeholder': 'MAT',
                'maxlength': '3',
                'style': 'text-transform: uppercase;',
                'required': False
            }),
            'color': forms.TextInput(attrs={
                'class': 'block w-20 h-10 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'color',
                'placeholder': '#FF0000'
            }),
        }
        labels = {
            'designation': 'Désignation',
            'short_designation': 'Abréviation',
            'color': 'Couleur',
        }


class DailyRotationPlanForm(forms.ModelForm):
    class Meta:
        model = DailyRotationPlan
        fields = ['designation', 'description', 'schedule_type']
        widgets = {
            'designation': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ex: Équipe A - Salle de contrôle'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Description détaillée du plan de rotation (optionnel)',
                'rows': 3
            }),
            'schedule_type': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
        }
        labels = {
            'designation': 'Nom du plan',
            'description': 'Description',
            'schedule_type': 'Type d\'horaire',
        }


class RotationPeriodForm(forms.ModelForm):
    class Meta:
        model = RotationPeriod
        fields = ['daily_rotation_plan', 'start_date', 'end_date', 'start_time', 'end_time']
        widgets = {
            'daily_rotation_plan': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'time'
            }),
        }
        labels = {
            'daily_rotation_plan': 'Rythme quotidien',
            'start_date': 'Date de début',
            'end_date': 'Date de fin',
            'start_time': 'Heure de début',
            'end_time': 'Heure de fin',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        daily_rotation_plan = cleaned_data.get('daily_rotation_plan')
        
        # Basic date validation
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('La date de fin doit être postérieure ou égale à la date de début.')
        
        # Check for overlapping periods within the same daily rotation plan
        if start_date and end_date and daily_rotation_plan:
            overlapping_periods = RotationPeriod.objects.filter(
                daily_rotation_plan=daily_rotation_plan,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            # Exclude current instance if editing
            if self.instance.pk:
                overlapping_periods = overlapping_periods.exclude(pk=self.instance.pk)
            
            if overlapping_periods.exists():
                overlapping_period = overlapping_periods.first()
                raise forms.ValidationError(
                    f'Cette période chevauche avec une période existante '
                    f'({overlapping_period.start_date.strftime("%d/%m/%Y")} - '
                    f'{overlapping_period.end_date.strftime("%d/%m/%Y")}) '
                    f'pour le même rythme quotidien.'
                )
        
        return cleaned_data


# Shift Schedule Forms

class ShiftScheduleForm(forms.ModelForm):
    class Meta:
        model = ShiftSchedule
        fields = ['name', 'type', 'break_times']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ex: Planning Été 2024'
            }),
            'type': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'break_times': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'min': '0',
                'max': '10',
                'step': '1'
            }),
        }
        labels = {
            'name': 'Nom du planning',
            'type': 'Type',
            'break_times': 'Durée de la pause (h)',
        }


class ShiftSchedulePeriodForm(forms.ModelForm):
    class Meta:
        model = ShiftSchedulePeriod
        fields = ['shift_schedule', 'start_date', 'end_date']
        widgets = {
            'shift_schedule': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
        }
        labels = {
            'shift_schedule': 'Planning de poste',
            'start_date': 'Date de début',
            'end_date': 'Date de fin',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        shift_schedule = cleaned_data.get('shift_schedule')
        
        # Basic date validation
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('La date de fin doit être postérieure ou égale à la date de début.')
        
        # Check for overlapping periods within the same shift schedule
        if start_date and end_date and shift_schedule:
            overlapping_periods = ShiftSchedulePeriod.objects.filter(
                shift_schedule=shift_schedule,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            # Exclude current instance if editing
            if self.instance.pk:
                overlapping_periods = overlapping_periods.exclude(pk=self.instance.pk)
            
            if overlapping_periods.exists():
                overlapping_period = overlapping_periods.first()
                raise forms.ValidationError(
                    f'Cette période chevauche avec une période existante '
                    f'({overlapping_period.start_date.strftime("%d/%m/%Y")} - '
                    f'{overlapping_period.end_date.strftime("%d/%m/%Y")}) '
                    f'pour le même planning de poste.'
                )
        
        return cleaned_data


class ShiftScheduleWeekForm(forms.ModelForm):
    class Meta:
        model = ShiftScheduleWeek
        fields = ['period', 'week_number']
        widgets = {
            'period': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'week_number': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'min': '1',
                'step': '1'
            }),
        }
        labels = {
            'period': 'Période',
            'week_number': 'Numéro de semaine',
        }


class ShiftScheduleDailyPlanForm(forms.ModelForm):
    class Meta:
        model = ShiftScheduleDailyPlan
        fields = ['week', 'weekday', 'daily_rotation_plan']
        widgets = {
            'week': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'weekday': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'daily_rotation_plan': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
        }
        labels = {
            'week': 'Semaine',
            'weekday': 'Jour de la semaine',
            'daily_rotation_plan': 'Rythme quotidien',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        week = cleaned_data.get('week')
        weekday = cleaned_data.get('weekday')
        daily_rotation_plan = cleaned_data.get('daily_rotation_plan')
        
        if week and weekday and daily_rotation_plan:
            # Check if this exact combination already exists
            existing = ShiftScheduleDailyPlan.objects.filter(
                week=week,
                weekday=weekday,
                daily_rotation_plan=daily_rotation_plan
            )
            
            # Exclude current instance if editing
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                weekday_name = dict(ShiftScheduleDailyPlan.WEEKDAY_CHOICES).get(weekday, str(weekday))
                raise forms.ValidationError(
                    f'Le rythme "{daily_rotation_plan.designation}" est déjà assigné au {weekday_name} de cette semaine.'
                )
        
        return cleaned_data


# Bulk forms for multiple daily plans per week
class WeeklyPlanFormSet(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.week = kwargs.pop('week', None)
        super().__init__(*args, **kwargs)
        
    def add_fields(self, form, index):
        super().add_fields(form, index)
        if self.week:
            form.fields['week'].initial = self.week
            form.fields['week'].widget = forms.HiddenInput()


WeeklyPlanFormSet = forms.formset_factory(
    ShiftScheduleDailyPlanForm,
    formset=WeeklyPlanFormSet,
    extra=7,  # 7 days of the week
    max_num=7,
    min_num=0,
    validate_max=True,
    validate_min=False
)


class PublicHolidayForm(forms.ModelForm):
    class Meta:
        model = PublicHoliday
        fields = ['designation', 'date']
        widgets = {
            'designation': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ex: Fête du Travail, Noël'
            }),
            'date': forms.DateInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
        }
        labels = {
            'designation': 'Nom du jour férié',
            'date': 'Date',
        }
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date:
            # Check for duplicate dates, excluding the current instance if editing
            existing_holidays = PublicHoliday.objects.filter(date=date)
            if self.instance.pk:
                existing_holidays = existing_holidays.exclude(pk=self.instance.pk)
            
            if existing_holidays.exists():
                existing_holiday = existing_holidays.first()
                raise forms.ValidationError(
                    f'Un jour férié existe déjà pour cette date : "{existing_holiday.designation}" ({date.strftime("%d/%m/%Y")})'
                )
        return date