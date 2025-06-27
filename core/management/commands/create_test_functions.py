from django.core.management.base import BaseCommand
from core.models import Function
import json
import os


class Command(BaseCommand):
    help = 'Create test functions from JSON database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing functions before creating new ones',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing functions if data has changed',
        )

    def handle(self, *args, **options):
        # Get the path to the JSON file in the same directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, 'functions_data.json')
        
        # Check if JSON file exists
        if not os.path.exists(json_file_path):
            self.stdout.write(
                self.style.ERROR(f'JSON file not found: {json_file_path}')
            )
            return

        # Load functions data from JSON
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                functions_data = json.load(file)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading JSON file: {str(e)}')
            )
            return

        if options['clear']:
            Function.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Cleared all existing functions')
            )

        # Create/update functions from JSON data
        functions_created = 0
        functions_updated = 0
        functions_skipped = 0
        
        for function_data in functions_data:
            # Check if function already exists
            existing_function = Function.objects.filter(designation=function_data['designation']).first()
            
            if existing_function and not options['update']:
                functions_skipped += 1
                self.stdout.write(
                    self.style.WARNING(f'Skipped existing function: {function_data["designation"]}')
                )
                continue
            
            # Create or update the function
            try:
                if existing_function:
                    # Update existing function
                    updated = False
                    changes = []
                    
                    if existing_function.description != function_data.get('description', ''):
                        existing_function.description = function_data.get('description', '')
                        changes.append('description')
                        updated = True
                    
                    if existing_function.status != function_data.get('status', True):
                        existing_function.status = function_data.get('status', True)
                        changes.append('status')
                        updated = True
                    
                    if updated:
                        existing_function.save()
                        functions_updated += 1
                        status_text = "Actif" if existing_function.status else "Inactif"
                        self.stdout.write(
                            f"Updated: {existing_function.designation} ({status_text}) "
                            f"[{', '.join(changes)}]"
                        )
                    else:
                        functions_skipped += 1
                        self.stdout.write(
                            self.style.WARNING(f'No changes for: {existing_function.designation}')
                        )
                else:
                    # Create new function
                    function = Function.objects.create(
                        designation=function_data['designation'],
                        description=function_data.get('description', ''),
                        status=function_data.get('status', True)
                    )
                    functions_created += 1
                    
                    status_text = "Actif" if function.status else "Inactif"
                    self.stdout.write(
                        f"Created: {function.designation} ({status_text})"
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing function {function_data["designation"]}: {str(e)}')
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(f'\nOperation completed:')
        )
        if functions_created > 0:
            self.stdout.write(f'Created: {functions_created} functions')
        if functions_updated > 0:
            self.stdout.write(f'Updated: {functions_updated} functions')
        if functions_skipped > 0:
            self.stdout.write(f'Skipped: {functions_skipped} functions')
        
        # Show statistics
        total_functions = Function.objects.count()
        active_functions = Function.objects.filter(status=True).count()
        inactive_functions = Function.objects.filter(status=False).count()
        
        self.stdout.write(f'\nStatistics:')
        self.stdout.write(f'Total functions in database: {total_functions}')
        self.stdout.write(f'Active functions: {active_functions}')
        self.stdout.write(f'Inactive functions: {inactive_functions}')
        
        if total_functions > 0:
            active_percentage = (active_functions / total_functions) * 100
            self.stdout.write(f'Active rate: {active_percentage:.1f}%')