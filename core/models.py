from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User


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
