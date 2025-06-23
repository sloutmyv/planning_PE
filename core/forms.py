from django import forms
from .models import Agent, Function


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
            'grade': 'Grade',
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