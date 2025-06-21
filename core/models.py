from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Agent(models.Model):
    GRADE_CHOICES = [
        ('Agent', 'Agent'),
        ('Maitrise', 'Maitrise'),
        ('Cadre', 'Cadre'),
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
    
    def clean(self):
        super().clean()
        if self.departure_date and self.hire_date and self.departure_date <= self.hire_date:
            raise ValidationError({
                'departure_date': 'La date de départ doit être postérieure à la date d\'embauche.'
            })
    
    def __str__(self):
        return f"{self.matricule} - {self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"
