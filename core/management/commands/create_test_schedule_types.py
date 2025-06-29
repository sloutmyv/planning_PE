from django.core.management.base import BaseCommand
from core.models import ScheduleType
import json
import os


class Command(BaseCommand):
    help = 'Create test schedule types from JSON database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing schedule types before creating new ones',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing schedule types if data has changed',
        )

    def handle(self, *args, **options):
        # Get the path to the JSON file in the same directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, 'schedule_types_data.json')
        
        # Check if JSON file exists
        if not os.path.exists(json_file_path):
            self.stdout.write(
                self.style.ERROR(f'JSON file not found: {json_file_path}')
            )
            return

        # Load schedule types data from JSON
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                schedule_types_data = json.load(file)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading JSON file: {str(e)}')
            )
            return

        if options['clear']:
            ScheduleType.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Cleared all existing schedule types')
            )

        # Create/update schedule types from JSON data
        schedule_types_created = 0
        schedule_types_updated = 0
        schedule_types_skipped = 0
        
        for schedule_type_data in schedule_types_data:
            # Check if schedule type already exists
            existing_schedule_type = ScheduleType.objects.filter(designation=schedule_type_data['designation']).first()
            
            if existing_schedule_type and not options['update']:
                schedule_types_skipped += 1
                self.stdout.write(
                    self.style.WARNING(f'Skipped existing schedule type: {schedule_type_data["designation"]}')
                )
                continue
            
            # Create or update the schedule type
            try:
                if existing_schedule_type:
                    # Update existing schedule type
                    updated = False
                    changes = []
                    
                    # Handle short_designation (can be empty string or None)
                    new_short_designation = schedule_type_data.get('short_designation', '') or None
                    if existing_schedule_type.short_designation != new_short_designation:
                        existing_schedule_type.short_designation = new_short_designation
                        changes.append('short_designation')
                        updated = True
                    
                    if existing_schedule_type.color != schedule_type_data.get('color', '#000000'):
                        existing_schedule_type.color = schedule_type_data.get('color', '#000000')
                        changes.append('color')
                        updated = True
                    
                    if updated:
                        existing_schedule_type.save()
                        schedule_types_updated += 1
                        short_text = existing_schedule_type.short_designation or "Non définie"
                        self.stdout.write(
                            f"Updated: {existing_schedule_type.designation} ({short_text}) "
                            f"[{', '.join(changes)}]"
                        )
                    else:
                        schedule_types_skipped += 1
                        self.stdout.write(
                            self.style.WARNING(f'No changes for: {existing_schedule_type.designation}')
                        )
                else:
                    # Create new schedule type
                    # Handle short_designation (convert empty string to None)
                    short_designation = schedule_type_data.get('short_designation', '') or None
                    
                    schedule_type = ScheduleType.objects.create(
                        designation=schedule_type_data['designation'],
                        short_designation=short_designation,
                        color=schedule_type_data.get('color', '#000000')
                    )
                    schedule_types_created += 1
                    
                    short_text = schedule_type.short_designation or "Non définie"
                    self.stdout.write(
                        f"Created: {schedule_type.designation} ({short_text}) - {schedule_type.color}"
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing schedule type {schedule_type_data["designation"]}: {str(e)}')
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(f'\nOperation completed:')
        )
        if schedule_types_created > 0:
            self.stdout.write(f'Created: {schedule_types_created} schedule types')
        if schedule_types_updated > 0:
            self.stdout.write(f'Updated: {schedule_types_updated} schedule types')
        if schedule_types_skipped > 0:
            self.stdout.write(f'Skipped: {schedule_types_skipped} schedule types')
        
        # Show statistics
        total_schedule_types = ScheduleType.objects.count()
        with_short_designation = ScheduleType.objects.exclude(short_designation__isnull=True).exclude(short_designation='').count()
        without_short_designation = total_schedule_types - with_short_designation
        
        self.stdout.write(f'\nStatistics:')
        self.stdout.write(f'Total schedule types in database: {total_schedule_types}')
        self.stdout.write(f'With short designation: {with_short_designation}')
        self.stdout.write(f'Without short designation: {without_short_designation}')
        
        if total_schedule_types > 0:
            with_short_percentage = (with_short_designation / total_schedule_types) * 100
            self.stdout.write(f'With short designation rate: {with_short_percentage:.1f}%')