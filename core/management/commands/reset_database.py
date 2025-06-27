from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Agent, Function


class Command(BaseCommand):
    help = 'Reset the database to zero while preserving the superuser account'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the database reset operation',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This command will delete all agents and functions from the database.\n'
                    'The superuser account will be preserved.\n'
                    'To proceed, run: python manage.py reset_database --confirm'
                )
            )
            return

        # Store superuser information before deletion
        superusers = User.objects.filter(is_superuser=True).exclude(agent__isnull=False)
        superuser_data = []
        
        for su in superusers:
            superuser_data.append({
                'username': su.username,
                'email': su.email,
                'first_name': su.first_name,
                'last_name': su.last_name,
                'password': su.password,  # Already hashed
                'is_staff': su.is_staff,
                'is_active': su.is_active,
                'date_joined': su.date_joined,
                'last_login': su.last_login,
            })

        # Delete all agents (this will cascade delete their associated users)
        agent_count = Agent.objects.count()
        Agent.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {agent_count} agents and their associated user accounts')
        )

        # Delete all functions
        function_count = Function.objects.count()
        Function.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {function_count} functions')
        )

        # Check if superusers still exist (they shouldn't have been deleted if not linked to agents)
        existing_superusers = User.objects.filter(is_superuser=True)
        if existing_superusers.exists():
            self.stdout.write(
                self.style.SUCCESS(f'Preserved {existing_superusers.count()} existing superuser account(s)')
            )
        else:
            # Recreate superuser accounts only if they were deleted
            for su_data in superuser_data:
                user = User.objects.create(
                    username=su_data['username'],
                    email=su_data['email'],
                    first_name=su_data['first_name'],
                    last_name=su_data['last_name'],
                    password=su_data['password'],
                    is_staff=su_data['is_staff'],
                    is_superuser=True,
                    is_active=su_data['is_active'],
                    date_joined=su_data['date_joined'],
                    last_login=su_data['last_login'],
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Restored superuser: {user.username}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDatabase reset completed successfully!\n'
                f'- All agents and their user accounts have been deleted\n'
                f'- All functions have been deleted\n'
                f'- {len(superuser_data)} superuser account(s) have been preserved\n'
            )
        )