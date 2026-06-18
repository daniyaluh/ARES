"""
Management command to update clearance level priorities.
"""
from django.core.management.base import BaseCommand
from verification.models import ClearanceLevel


class Command(BaseCommand):
    help = 'Update clearance level priorities: public=10, age_restricted=25, military=40, research=50'

    def handle(self, *args, **options):
        self.stdout.write('Updating clearance level priorities...')
        
        # Update public to priority 10
        try:
            public = ClearanceLevel.objects.get(code='public')
            public.priority = 10
            public.save()
            self.stdout.write(self.style.SUCCESS(f'Updated {public.name}: Priority {public.priority}'))
        except ClearanceLevel.DoesNotExist:
            self.stdout.write(self.style.WARNING('Public clearance level not found'))
        
        # Update age_restricted to priority 25
        try:
            age_restricted = ClearanceLevel.objects.get(code='age_restricted')
            age_restricted.priority = 25
            age_restricted.save()
            self.stdout.write(self.style.SUCCESS(f'Updated {age_restricted.name}: Priority {age_restricted.priority}'))
        except ClearanceLevel.DoesNotExist:
            self.stdout.write(self.style.WARNING('Age-restricted clearance level not found'))
        
        # Update military to priority 40
        try:
            military = ClearanceLevel.objects.get(code='military')
            military.priority = 40
            military.save()
            self.stdout.write(self.style.SUCCESS(f'Updated {military.name}: Priority {military.priority}'))
        except ClearanceLevel.DoesNotExist:
            self.stdout.write(self.style.WARNING('Military clearance level not found'))
        
        # Create research clearance level with priority 50
        research, created = ClearanceLevel.objects.get_or_create(
            code='research',
            defaults={
                'name': 'Research & Advanced Robotics',
                'description': 'Highest clearance level for accessing cutting-edge research robotics, experimental prototypes, and most advanced autonomous systems. Requires extensive background checks and research institution affiliation.',
                'can_access_restricted': True,
                'can_access_military': True,
                'can_access_export_controlled': True,
                'minimum_clearance_required': 'top_secret',
                'validity_months': 24,
                'requires_renewal': True,
                'requires_background_check': True,
                'priority': 50,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created {research.name}: Priority {research.priority}'))
        else:
            research.priority = 50
            research.save()
            self.stdout.write(self.style.SUCCESS(f'Updated {research.name}: Priority {research.priority}'))
        
        # Display all clearance levels
        self.stdout.write('\nFinal clearance level priorities:')
        levels = ClearanceLevel.objects.all().order_by('-priority')
        for level in levels:
            self.stdout.write(f'  {level.code}: {level.name} - Priority: {level.priority}')







