from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Agent, Function


class Command(BaseCommand):
    help = 'Reset the entire database while preserving only superuser accounts'

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
                    'This command will delete ALL data from the database.\n'
                    'Only superuser accounts will be preserved.\n'
                    'This includes: agents, functions, and all regular user accounts.\n'
                    'To proceed, run: python manage.py reset_database --confirm'
                )
            )
            return

        # Store ALL superuser information before deletion (including those linked to agents)
        superusers = User.objects.filter(is_superuser=True)
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

        # Count items before deletion
        agent_count = Agent.objects.count()
        function_count = Function.objects.count()
        regular_user_count = User.objects.filter(is_superuser=False).count()

        # Delete all agents (this will cascade delete their associated users due to OneToOneField)
        Agent.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {agent_count} agents')
        )

        # Delete all functions
        Function.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {function_count} functions')
        )

        # Delete ALL users (including superusers) - we'll recreate superusers after
        all_users_count = User.objects.count()
        User.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {all_users_count} user accounts (including superusers)')
        )

        # Recreate superuser accounts (all users have been deleted)
        superusers_restored = 0
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
            superusers_restored += 1
            self.stdout.write(
                self.style.SUCCESS(f'Restored superuser: {user.username}')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDatabase reset completed successfully!\n'
                f'- Deleted {agent_count} agents\n'
                f'- Deleted {function_count} functions\n'
                f'- Deleted {all_users_count} user accounts\n'
                f'- Restored {superusers_restored} superuser account(s)\n'
            )
        )