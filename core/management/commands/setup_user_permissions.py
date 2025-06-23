from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Agent


class Command(BaseCommand):
    help = 'Setup user accounts for existing agents and create test permission agents'

    def handle(self, *args, **options):
        # First, create user accounts for existing agents that don't have one
        existing_agents = Agent.objects.filter(user__isnull=True)
        
        for agent in existing_agents:
            try:
                # Check if username already exists
                if User.objects.filter(username=agent.matricule).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User {agent.matricule} already exists, skipping')
                    )
                    continue
                
                user = User.objects.create_user(
                    username=agent.matricule,
                    first_name=agent.first_name,
                    last_name=agent.last_name,
                    password='azerty'
                )
                
                # Set staff status for Super Administrators
                if agent.permission_level == 'S':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                
                agent.user = user
                agent.save(update_fields=['user'])
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created user account for agent {agent.matricule}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating user for {agent.matricule}: {e}')
                )
        
        # Create test agents with different permission levels
        test_agents_data = [
            {
                'matricule': 'S0001',
                'first_name': 'Super',
                'last_name': 'Admin',
                'grade': 'Cadre',
                'permission_level': 'S'
            },
            {
                'matricule': 'A0001',
                'first_name': 'Admin',
                'last_name': 'Général',
                'grade': 'Cadre',
                'permission_level': 'A'
            },
            {
                'matricule': 'E0001',
                'first_name': 'Éditeur',
                'last_name': 'Test',
                'grade': 'Maitrise',
                'permission_level': 'E'
            },
            {
                'matricule': 'V0001',
                'first_name': 'Lecteur',
                'last_name': 'Simple',
                'grade': 'Agent',
                'permission_level': 'V'
            }
        ]
        
        for agent_data in test_agents_data:
            agent, created = Agent.objects.get_or_create(
                matricule=agent_data['matricule'],
                defaults=agent_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created test agent: {agent.matricule} ({agent.get_permission_display_name()})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Test agent {agent.matricule} already exists')
                )
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== SUMMARY ==='))
        for level_code, level_name in Agent.PERMISSION_CHOICES:
            count = Agent.objects.filter(permission_level=level_code).count()
            self.stdout.write(f'{level_name}: {count} agents')
        
        total_with_users = Agent.objects.filter(user__isnull=False).count()
        total_agents = Agent.objects.count()
        self.stdout.write(f'\nAgents with user accounts: {total_with_users}/{total_agents}')
        
        # Print test credentials
        self.stdout.write(self.style.SUCCESS('\n=== TEST CREDENTIALS ==='))
        for agent_data in test_agents_data:
            agent = Agent.objects.get(matricule=agent_data['matricule'])
            self.stdout.write(f'{agent.matricule} ({agent.get_permission_display_name()}): username={agent.matricule}, password=azerty')