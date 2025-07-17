from django.db import models, transaction
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, time


class Agent(models.Model):
    GRADE_CHOICES = [
        ('Agent', 'Agent'),
        ('Maitrise', 'Maitrise'),
        ('Cadre', 'Cadre'),
    ]
    
    PERMISSION_CHOICES = [
        ('V', 'Viewer'),
        ('E', 'Editor'),
        ('A', 'Administrator'),
        ('S', 'Super Administrator'),
    ]
    
    matricule = models.CharField(
        max_length=5,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]\d{4}$',
                message='Le matricule doit contenir une lettre suivie de 4 chiffres (ex: A1234)'
            )
        ]
    )
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES)
    hire_date = models.DateField(verbose_name="Date d'embauche", default=timezone.now)
    departure_date = models.DateField(verbose_name="Date de départ", null=True, blank=True)
    permission_level = models.CharField(max_length=1, choices=PERMISSION_CHOICES, default='V', verbose_name="Niveau de permission")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    password_changed = models.BooleanField(default=False, verbose_name="Mot de passe modifié")
    
    def clean(self):
        super().clean()
        if self.departure_date and self.hire_date and self.departure_date <= self.hire_date:
            raise ValidationError({
                'departure_date': 'La date de départ doit être postérieure à la date d\'embauche.'
            })
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        """Override save to create user account when agent is created"""
        created = self.pk is None
        super().save(*args, **kwargs)
        
        if created and not self.user:
            # Create user account for new agent
            from django.contrib.auth.models import User
            user = User.objects.create_user(
                username=self.matricule,
                first_name=self.first_name,
                last_name=self.last_name,
                password='azerty'
            )
            # Set staff status for Super Administrators
            if self.permission_level == 'S':
                user.is_staff = True
                user.is_superuser = True
                user.save()
            
            self.user = user
            self.save(update_fields=['user'])
        elif not created and self.user:
            # Update existing user's information when agent is updated
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name
            
            # Update staff status based on permission level
            if self.permission_level == 'S':
                self.user.is_staff = True
                self.user.is_superuser = True
            else:
                self.user.is_staff = False
                self.user.is_superuser = False
            
            self.user.save()
    
    def is_super_admin(self):
        return self.permission_level == 'S'
    
    def is_admin(self):
        return self.permission_level in ['A', 'S']
    
    def is_editor(self):
        return self.permission_level in ['E', 'A', 'S']
    
    def is_viewer(self):
        return self.permission_level in ['V', 'E', 'A', 'S']
    
    def can_manage_permissions(self):
        return self.permission_level in ['A', 'S']
    
    def get_permission_display_name(self):
        permission_names = {
            'V': 'Lecteur',
            'E': 'Éditeur',
            'A': 'Administrateur',
            'S': 'Super Administrateur'
        }
        return permission_names.get(self.permission_level, 'Inconnu')
    
    def get_permission_short_name(self):
        permission_short = {
            'V': 'R',
            'E': 'E',
            'A': 'A',
            'S': 'SA'
        }
        return permission_short.get(self.permission_level, '?')
    
    def __str__(self):
        return f"{self.matricule} - {self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"


class Function(models.Model):
    designation = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, verbose_name="Actif")
    
    def __str__(self):
        return self.designation
    
    class Meta:
        verbose_name = "Fonction"
        verbose_name_plural = "Fonctions"


class ScheduleType(models.Model):
    designation = models.CharField(max_length=100, unique=True)
    short_designation = models.CharField(
        max_length=3, 
        blank=True,
        null=True,
        unique=True,
        help_text="Abréviation en 2-3 lettres majuscules (ex: MAT, APM, NUIT)"
    )
    color = models.CharField(max_length=7, help_text="Code couleur hexadécimal (ex: #FF0000)")
    
    def clean(self):
        super().clean()
        # Validate hexadecimal color format
        import re
        if not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            raise ValidationError({
                'color': 'La couleur doit être au format hexadécimal (ex: #FF0000)'
            })
        
        # Validate short designation format (only if provided)
        if self.short_designation and not re.match(r'^[A-Z]{2,3}$', self.short_designation):
            raise ValidationError({
                'short_designation': 'L\'abréviation doit contenir 2 ou 3 lettres majuscules uniquement'
            })
    
    def save(self, *args, **kwargs):
        # Ensure short_designation is always uppercase
        if self.short_designation:
            self.short_designation = self.short_designation.upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.designation
    
    class Meta:
        verbose_name = "Type de Planning"
        verbose_name_plural = "Types de Planning"


class DailyRotationPlan(models.Model):
    designation = models.CharField(
        max_length=200,
        help_text="Nom du plan (ex: 'Équipe A - Salle de contrôle')"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description détaillée du plan de rotation"
    )
    schedule_type = models.ForeignKey(
        ScheduleType,
        on_delete=models.PROTECT,
        help_text="Type d'horaire qui s'applique à toutes les périodes de ce plan"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.designation
    
    class Meta:
        verbose_name = "Rythme Quotidien"
        verbose_name_plural = "Rythmes Quotidiens"
        ordering = ['designation']


class RotationPeriod(models.Model):
    daily_rotation_plan = models.ForeignKey(
        DailyRotationPlan,
        on_delete=models.CASCADE,
        related_name='periods',
        help_text="Plan de rotation auquel appartient cette période"
    )
    start_date = models.DateField(
        help_text="Date de début de validité de la période"
    )
    end_date = models.DateField(
        help_text="Date de fin de validité de la période"
    )
    start_time = models.TimeField(
        help_text="Heure de début quotidienne (ex: 08:00)"
    )
    end_time = models.TimeField(
        help_text="Heure de fin quotidienne (ex: 16:00)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        super().clean()
        
        # Validate that end_date >= start_date
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': 'La date de fin doit être postérieure ou égale à la date de début.'
            })
        
        # Validate time consistency (except for night shifts)
        if self.start_time and self.end_time:
            # Allow night shifts where end_time < start_time (e.g., 22:00-06:00)
            # Only validate if it's not a night shift
            if self.start_time >= self.end_time:
                # Check if this could be a valid night shift
                if not (self.start_time >= time(18, 0) and self.end_time <= time(12, 0)):
                    raise ValidationError({
                        'end_time': 'L\'heure de fin doit être postérieure à l\'heure de début, sauf pour les équipes de nuit (18h00-12h00).'
                    })
        
        # Check for overlapping periods within the same plan
        if self.daily_rotation_plan_id:
            overlapping_periods = RotationPeriod.objects.filter(
                daily_rotation_plan=self.daily_rotation_plan
            ).exclude(pk=self.pk if self.pk else None)
            
            for period in overlapping_periods:
                # Check if date ranges overlap
                if (self.start_date <= period.end_date and 
                    self.end_date >= period.start_date):
                    raise ValidationError({
                        'start_date': f'Cette période chevauche avec une période existante ({period.start_date} - {period.end_date}).',
                        'end_date': f'Cette période chevauche avec une période existante ({period.start_date} - {period.end_date}).'
                    })
    
    def is_night_shift(self):
        """Check if this is a night shift (end_time < start_time)"""
        return self.start_time > self.end_time
    
    def get_duration_hours(self):
        """Calculate the duration of the shift in hours"""
        if self.is_night_shift():
            # Night shift calculation
            end_next_day = datetime.combine(datetime.today(), self.end_time)
            start_today = datetime.combine(datetime.today(), self.start_time)
            duration = (end_next_day + timezone.timedelta(days=1)) - start_today
        else:
            # Regular shift calculation
            end_today = datetime.combine(datetime.today(), self.end_time)
            start_today = datetime.combine(datetime.today(), self.start_time)
            duration = end_today - start_today
        
        return duration.total_seconds() / 3600
    
    def is_active(self):
        """Check if this period is currently active (end date is today or in the future)"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.end_date >= today
    
    def __str__(self):
        return f"{self.daily_rotation_plan.designation} - {self.start_date} à {self.end_date}"
    
    class Meta:
        verbose_name = "Période de Rotation"
        verbose_name_plural = "Périodes de Rotation"
        ordering = ['start_date', 'start_time']


class ShiftSchedule(models.Model):
    TYPE_CHOICES = [
        ('day', 'Journée'),
        ('shift', 'Quart'),
    ]
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Nom du planning de poste (ex: 'Planning Été 2024')"
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='day'
    )
    break_times = models.PositiveIntegerField(
        default=2,
        help_text="Nombre de pauses par défaut (généralement 2)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Planning de Poste"
        verbose_name_plural = "Plannings de Poste"
        ordering = ['name']


class ShiftSchedulePeriod(models.Model):
    shift_schedule = models.ForeignKey(
        ShiftSchedule,
        on_delete=models.CASCADE,
        related_name='periods',
        help_text="Planning de poste auquel appartient cette période"
    )
    start_date = models.DateField(
        help_text="Date de début de la période"
    )
    end_date = models.DateField(
        help_text="Date de fin de la période"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        super().clean()
        
        # Validate that end_date >= start_date
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': 'La date de fin doit être postérieure ou égale à la date de début.'
            })
        
        # Check for overlapping periods within the same shift schedule
        if self.shift_schedule_id:
            overlapping_periods = ShiftSchedulePeriod.objects.filter(
                shift_schedule=self.shift_schedule
            ).exclude(pk=self.pk if self.pk else None)
            
            for period in overlapping_periods:
                # Check if date ranges overlap
                if (self.start_date <= period.end_date and 
                    self.end_date >= period.start_date):
                    raise ValidationError({
                        'start_date': f'Cette période chevauche avec une période existante ({period.start_date} - {period.end_date}).',
                        'end_date': f'Cette période chevauche avec une période existante ({period.start_date} - {period.end_date}).'
                    })
    
    def __str__(self):
        return f"{self.shift_schedule.name} - {self.start_date} à {self.end_date}"
    
    class Meta:
        verbose_name = "Période de Planning de Poste"
        verbose_name_plural = "Périodes de Planning de Poste"
        ordering = ['start_date']


class ShiftScheduleWeek(models.Model):
    period = models.ForeignKey(
        ShiftSchedulePeriod,
        on_delete=models.CASCADE,
        related_name='weeks',
        help_text="Période à laquelle appartient cette semaine"
    )
    week_number = models.PositiveIntegerField(
        help_text="Numéro de la semaine dans la période (1, 2, 3, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.period.shift_schedule.name} - Semaine {self.week_number}"
    
    class Meta:
        verbose_name = "Semaine de Planning"
        verbose_name_plural = "Semaines de Planning"
        unique_together = ['period', 'week_number']
        ordering = ['period', 'week_number']


class ShiftScheduleDailyPlan(models.Model):
    WEEKDAY_CHOICES = [
        (1, 'Lundi'),
        (2, 'Mardi'),
        (3, 'Mercredi'),
        (4, 'Jeudi'),
        (5, 'Vendredi'),
        (6, 'Samedi'),
        (7, 'Dimanche'),
    ]
    
    week = models.ForeignKey(
        ShiftScheduleWeek,
        on_delete=models.CASCADE,
        related_name='daily_plans',
        help_text="Semaine à laquelle appartient ce plan quotidien"
    )
    weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        help_text="Jour de la semaine (1=Lundi, 7=Dimanche)"
    )
    daily_rotation_plan = models.ForeignKey(
        DailyRotationPlan,
        on_delete=models.PROTECT,
        help_text="Rythme quotidien assigné à ce jour"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_weekday_display_french(self):
        """Return French weekday name"""
        weekday_names = {
            1: 'Lundi',
            2: 'Mardi',
            3: 'Mercredi',
            4: 'Jeudi',
            5: 'Vendredi',
            6: 'Samedi',
            7: 'Dimanche'
        }
        return weekday_names.get(self.weekday, 'Inconnu')
    
    def __str__(self):
        return f"{self.week} - {self.get_weekday_display_french()}: {self.daily_rotation_plan.designation}"
    
    class Meta:
        verbose_name = "Plan Quotidien de Planning"
        verbose_name_plural = "Plans Quotidiens de Planning"
        ordering = ['week', 'weekday']


class PublicHoliday(models.Model):
    designation = models.CharField(
        max_length=200,
        help_text="Nom du jour férié (ex: 'Fête du Travail', 'Noël')"
    )
    date = models.DateField(
        unique=True,
        help_text="Date du jour férié",
        error_messages={
            'unique': 'Un jour férié existe déjà pour cette date.'
        }
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        super().clean()
        
        # Check for duplicate holidays on the same date
        if self.date:
            existing_holidays = PublicHoliday.objects.filter(date=self.date)
            if self.pk:
                existing_holidays = existing_holidays.exclude(pk=self.pk)
            
            if existing_holidays.exists():
                raise ValidationError({
                    'date': f'Un jour férié existe déjà pour cette date ({existing_holidays.first().designation}).'
                })
    
    def __str__(self):
        return f"{self.designation} - {self.date.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = "Jour Férié"
        verbose_name_plural = "Jours Fériés"
        ordering = ['date']
