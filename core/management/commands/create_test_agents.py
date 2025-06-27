from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Agent
import json
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Create test agents from JSON database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing agents before creating new ones',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing agents if data has changed',
        )

    def handle(self, *args, **options):
        # Get the path to the JSON file in the same directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, 'agents_data.json')
        
        # Check if JSON file exists
        if not os.path.exists(json_file_path):
            self.stdout.write(
                self.style.ERROR(f'JSON file not found: {json_file_path}')
            )
            return

        # Load agents data from JSON
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                agents_data = json.load(file)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading JSON file: {str(e)}')
            )
            return

        if options['clear']:
            Agent.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Cleared all existing agents')
            )

        # Create/update agents from JSON data
        agents_created = 0
        agents_updated = 0
        agents_skipped = 0
        
        for agent_data in agents_data:
            # Check if matricule already exists
            existing_agent = Agent.objects.filter(matricule=agent_data['matricule']).first()
            
            if existing_agent and not options['update']:
                agents_skipped += 1
                self.stdout.write(
                    self.style.WARNING(f'Skipped existing agent: {agent_data["matricule"]}')
                )
                continue
            
            # Parse dates
            try:
                hire_date = datetime.strptime(agent_data['hire_date'], '%Y-%m-%d').date()
                departure_date = None
                if agent_data['departure_date']:
                    departure_date = datetime.strptime(agent_data['departure_date'], '%Y-%m-%d').date()
            except ValueError as e:
                self.stdout.write(
                    self.style.ERROR(f'Error parsing date for {agent_data["matricule"]}: {str(e)}')
                )
                continue
            
            # Create or update the agent
            try:
                if existing_agent:
                    # Update existing agent
                    updated = False
                    changes = []
                    
                    if existing_agent.first_name != agent_data['first_name']:
                        existing_agent.first_name = agent_data['first_name']
                        changes.append('first_name')
                        updated = True
                    
                    if existing_agent.last_name != agent_data['last_name']:
                        existing_agent.last_name = agent_data['last_name']
                        changes.append('last_name')
                        updated = True
                    
                    if existing_agent.grade != agent_data['grade']:
                        existing_agent.grade = agent_data['grade']
                        changes.append('grade')
                        updated = True
                    
                    if existing_agent.hire_date != hire_date:
                        existing_agent.hire_date = hire_date
                        changes.append('hire_date')
                        updated = True
                    
                    if existing_agent.departure_date != departure_date:
                        existing_agent.departure_date = departure_date
                        changes.append('departure_date')
                        updated = True
                    
                    new_permission = agent_data.get('permission_level', 'V')
                    if existing_agent.permission_level != new_permission:
                        existing_agent.permission_level = new_permission
                        changes.append('permission_level')
                        updated = True
                    
                    if updated:
                        existing_agent.save()
                        agents_updated += 1
                        status = "parti" if departure_date else "actif"
                        permission_display = existing_agent.get_permission_display_name()
                        self.stdout.write(
                            f"Updated: {existing_agent.matricule} - {existing_agent.first_name} {existing_agent.last_name} "
                            f"({existing_agent.grade}) - {status} - {permission_display} "
                            f"[{', '.join(changes)}]"
                        )
                    else:
                        agents_skipped += 1
                        self.stdout.write(
                            self.style.WARNING(f'No changes for: {existing_agent.matricule}')
                        )
                else:
                    # Create new agent
                    agent = Agent.objects.create(
                        matricule=agent_data['matricule'],
                        first_name=agent_data['first_name'],
                        last_name=agent_data['last_name'],
                        grade=agent_data['grade'],
                        hire_date=hire_date,
                        departure_date=departure_date,
                        permission_level=agent_data.get('permission_level', 'V')
                    )
                    agents_created += 1
                    
                    status = "parti" if departure_date else "actif"
                    permission_display = agent.get_permission_display_name()
                    self.stdout.write(
                        f"Created: {agent.matricule} - {agent.first_name} {agent.last_name} "
                        f"({agent.grade}) - {status} - {permission_display}"
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing agent {agent_data["matricule"]}: {str(e)}')
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(f'\nOperation completed:')
        )
        if agents_created > 0:
            self.stdout.write(f'Created: {agents_created} agents')
        if agents_updated > 0:
            self.stdout.write(f'Updated: {agents_updated} agents')
        if agents_skipped > 0:
            self.stdout.write(f'Skipped: {agents_skipped} agents')
        
        # Show statistics
        total_agents = Agent.objects.count()
        active_agents = Agent.objects.filter(departure_date__isnull=True).count()
        departed_agents = Agent.objects.filter(departure_date__isnull=False).count()
        
        self.stdout.write(f'\nStatistics:')
        self.stdout.write(f'Total agents in database: {total_agents}')
        self.stdout.write(f'Active agents: {active_agents}')
        self.stdout.write(f'Departed agents: {departed_agents}')
        
        if total_agents > 0:
            departure_percentage = (departed_agents / total_agents) * 100
            self.stdout.write(f'Departure rate: {departure_percentage:.1f}%')
            
        # Grade distribution
        grades = ['Agent', 'Maitrise', 'Cadre']
        self.stdout.write(f'\nGrade distribution:')
        for grade in grades:
            count = Agent.objects.filter(grade=grade).count()
            percentage = (count / total_agents) * 100 if total_agents > 0 else 0
            self.stdout.write(f'{grade}: {count} ({percentage:.1f}%)')
            
        # Permission distribution
        permissions = ['V', 'E', 'A', 'S']
        permission_names = {'V': 'Viewer', 'E': 'Editor', 'A': 'Administrator', 'S': 'Super Administrator'}
        self.stdout.write(f'\nPermission distribution:')
        for perm in permissions:
            count = Agent.objects.filter(permission_level=perm).count()
            percentage = (count / total_agents) * 100 if total_agents > 0 else 0
            self.stdout.write(f'{permission_names[perm]} ({perm}): {count} ({percentage:.1f}%)')