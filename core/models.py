from django.db import models
from django.core.validators import RegexValidator


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
    
    def __str__(self):
        return f"{self.matricule} - {self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"
