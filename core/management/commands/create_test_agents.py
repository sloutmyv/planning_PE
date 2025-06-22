from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Agent
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Create 50 test agents with random data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing agents before creating new ones',
        )

    def handle(self, *args, **options):
        # French first names
        first_names = [
            'Jean', 'Pierre', 'Michel', 'André', 'Philippe', 'Alain', 'Bernard', 'Robert',
            'Jacques', 'Daniel', 'Claude', 'François', 'Gérard', 'Antoine', 'Louis',
            'Marie', 'Françoise', 'Monique', 'Catherine', 'Nathalie', 'Isabelle', 'Sylvie',
            'Martine', 'Nicole', 'Christine', 'Brigitte', 'Sophie', 'Valérie', 'Patricia',
            'Chantal', 'Julie', 'Caroline', 'Sandrine', 'Véronique', 'Stéphanie',
            'Émilie', 'Aurélie', 'Céline', 'Marine', 'Camille', 'Laura', 'Manon'
        ]

        # French last names
        last_names = [
            'Martin', 'Bernard', 'Thomas', 'Petit', 'Robert', 'Richard', 'Durand',
            'Dubois', 'Moreau', 'Laurent', 'Simon', 'Michel', 'Lefebvre', 'Leroy',
            'Roux', 'David', 'Bertrand', 'Morel', 'Fournier', 'Girard', 'Bonnet',
            'Dupont', 'Lambert', 'Fontaine', 'Rousseau', 'Vincent', 'Muller',
            'Lefevre', 'Faure', 'Andre', 'Mercier', 'Blanc', 'Guerin', 'Boyer',
            'Garnier', 'Chevalier', 'Francois', 'Legrand', 'Gauthier', 'Garcia',
            'Perrin', 'Robin', 'Clement', 'Morin', 'Nicolas', 'Henry', 'Roussel'
        ]

        # Available grades
        grades = ['Execution', 'Maitrise', 'Cadre']

        if options['clear']:
            Agent.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Cleared all existing agents')
            )

        # Generate 50 agents
        agents_created = 0
        
        for i in range(50):
            # Generate unique matricule
            matricule = f"AG{str(i+1).zfill(4)}"
            
            # Check if matricule already exists
            if Agent.objects.filter(matricule=matricule).exists():
                continue
                
            # Random names
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            # Random grade
            grade = random.choice(grades)
            
            # Random hire date between 2010 and 2024
            start_date = date(2010, 1, 1)
            end_date = date(2024, 12, 31)
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            hire_date = start_date + timedelta(days=random_days)
            
            # 10% chance of having left (departure date)
            departure_date = None
            if random.random() < 0.10:  # 10% chance
                # Departure date should be after hire date but before today
                min_departure = hire_date + timedelta(days=30)  # At least 30 days after hire
                max_departure = min(date.today(), hire_date + timedelta(days=365*10))  # Max 10 years or today
                
                if min_departure < max_departure:
                    time_between_departure = max_departure - min_departure
                    if time_between_departure.days > 0:
                        days_between_departure = time_between_departure.days
                        random_days_departure = random.randrange(days_between_departure)
                        departure_date = min_departure + timedelta(days=random_days_departure)
            
            # Create the agent
            try:
                agent = Agent.objects.create(
                    matricule=matricule,
                    first_name=first_name,
                    last_name=last_name,
                    grade=grade,
                    hire_date=hire_date,
                    departure_date=departure_date
                )
                agents_created += 1
                
                status = "parti" if departure_date else "actif"
                self.stdout.write(f"Created: {agent.matricule} - {agent.first_name} {agent.last_name} ({agent.grade}) - {status}")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating agent {matricule}: {str(e)}')
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {agents_created} agents')
        )
        
        # Show statistics
        total_agents = Agent.objects.count()
        active_agents = Agent.objects.filter(departure_date__isnull=True).count()
        departed_agents = Agent.objects.filter(departure_date__isnull=False).count()
        
        self.stdout.write(f'\nStatistics:')
        self.stdout.write(f'Total agents: {total_agents}')
        self.stdout.write(f'Active agents: {active_agents}')
        self.stdout.write(f'Departed agents: {departed_agents}')
        
        if total_agents > 0:
            departure_percentage = (departed_agents / total_agents) * 100
            self.stdout.write(f'Departure rate: {departure_percentage:.1f}%')
            
        # Grade distribution
        self.stdout.write(f'\nGrade distribution:')
        for grade in grades:
            count = Agent.objects.filter(grade=grade).count()
            percentage = (count / total_agents) * 100 if total_agents > 0 else 0
            self.stdout.write(f'{grade}: {count} ({percentage:.1f}%)')