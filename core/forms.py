from django import forms
from .models import (Agent, Function, ScheduleType, DailyRotationPlan, RotationPeriod,
                     ShiftSchedule, ShiftSchedulePeriod, ShiftScheduleWeek, ShiftScheduleDailyPlan, PublicHoliday, Department, Team, TeamPosition)


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
                'type': 'time',
                'data-allow-night-shift': 'true'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'time',
                'data-allow-night-shift': 'true'
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
        from datetime import time
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        daily_rotation_plan = cleaned_data.get('daily_rotation_plan')
        
        # Basic date validation
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('La date de fin doit être postérieure ou égale à la date de début.')
        
        # Time validation with automatic night shift detection
        if start_time and end_time:
            if start_time >= end_time:
                # Check if this could be a valid night shift
                # Night shifts are allowed if start_time >= 16:00 AND end_time <= 12:00
                is_potential_night_shift = (
                    start_time >= time(16, 0) and end_time <= time(12, 0)
                )
                
                if not is_potential_night_shift:
                    raise forms.ValidationError({
                        'end_time': 'L\'heure de fin doit être postérieure à l\'heure de début, sauf pour les équipes de nuit. Les équipes de nuit sont automatiquement détectées (ex: 16:00-08:00, 22:00-06:00).'
                    })
        
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter daily rotation plans to only show those with periods defined
        self.fields['daily_rotation_plan'].queryset = DailyRotationPlan.objects.filter(
            periods__isnull=False
        ).distinct()
        
        # Add help text to explain the filtering
        self.fields['daily_rotation_plan'].help_text = (
            "Seuls les rythmes quotidiens ayant au moins une période définie sont disponibles."
        )
    
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


class DepartmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set suggested next order value for new departments
        if not self.instance.pk:
            next_order = Department.get_next_order()
            self.fields['order'].widget.attrs['placeholder'] = f'Par défaut : {next_order}'
            # Make order field not required so it can be auto-filled
            self.fields['order'].required = False
    
    class Meta:
        model = Department
        fields = ['name', 'order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ex: Ressources Humaines, Informatique'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'min': '1',
                'step': '1'
            }),
        }
        labels = {
            'name': 'Nom du département',
            'order': 'Ordre d\'affichage',
        }
    
    def clean_order(self):
        order = self.cleaned_data.get('order')
        
        # If order is not provided, use the next available order
        if order is None or order == '':
            order = Department.get_next_order()
        
        # Check for duplicate order values
        existing_departments = Department.objects.filter(order=order)
        if self.instance.pk:
            existing_departments = existing_departments.exclude(pk=self.instance.pk)
        
        if existing_departments.exists():
            raise forms.ValidationError(
                f'Un département avec l\'ordre {order} existe déjà.'
            )
        
        return order


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['designation', 'description', 'color', 'department']
        widgets = {
            'designation': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ex: Équipe Alpha, Salle de contrôle A'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Description détaillée de l\'équipe (optionnel)',
                'rows': 3
            }),
            'color': forms.TextInput(attrs={
                'class': 'block w-20 h-10 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'color',
                'placeholder': '#FF0000'
            }),
            'department': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
        }
        labels = {
            'designation': 'Nom de l\'équipe',
            'description': 'Description',
            'color': 'Couleur',
            'department': 'Département',
        }


class TeamPositionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        
        # Set team if provided and hide it
        if team:
            self.fields['team'].initial = team
            self.fields['team'].widget = forms.HiddenInput()
        
        # Filter available functions to only show active ones
        self.fields['function'].queryset = Function.objects.filter(status=True)
        
        # Filter daily rotation plans to only show those with periods defined
        self.fields['rotation_plan'].queryset = DailyRotationPlan.objects.filter(
            periods__isnull=False
        ).distinct()
        
        # Make agent and rotation_plan optional
        self.fields['agent'].required = False
        self.fields['rotation_plan'].required = False
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False
        
        # Add empty options for optional fields
        self.fields['agent'].empty_label = "Aucun agent assigné"
        self.fields['rotation_plan'].empty_label = "Aucun plan de roulement"
        
        # Add help texts
        self.fields['function'].help_text = "Seules les fonctions actives sont disponibles."
        self.fields['rotation_plan'].help_text = "Seuls les plans de roulement ayant au moins une période définie sont disponibles."
        self.fields['agent'].help_text = "Optionnel - peut être assigné plus tard."
    
    class Meta:
        model = TeamPosition
        fields = ['team', 'function', 'agent', 'rotation_plan', 'start_date', 'end_date', 'considers_holidays']
        widgets = {
            'team': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'function': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'agent': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'rotation_plan': forms.Select(attrs={
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
            'considers_holidays': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
        }
        labels = {
            'team': 'Équipe',
            'function': 'Poste/Fonction',
            'agent': 'Agent assigné',
            'rotation_plan': 'Plan de roulement',
            'start_date': 'Date de début',
            'end_date': 'Date de fin',
            'considers_holidays': 'Prend en compte les jours fériés',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        team = cleaned_data.get('team')
        function = cleaned_data.get('function')
        
        # Basic date validation
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('La date de fin doit être postérieure ou égale à la date de début.')
        
        # Check for duplicate function within the team
        if team and function:
            existing_positions = TeamPosition.objects.filter(
                team=team,
                function=function
            )
            
            # Exclude current instance if editing
            if self.instance.pk:
                existing_positions = existing_positions.exclude(pk=self.instance.pk)
            
            if existing_positions.exists():
                raise forms.ValidationError({
                    'function': f'Le poste "{function.designation}" est déjà assigné à cette équipe.'
                })
        
        return cleaned_data