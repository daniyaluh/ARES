"""
Management command to create the age-restricted clearance level.
"""
from django.core.management.base import BaseCommand
from verification.models import ClearanceLevel


class Command(BaseCommand):
    help = 'Create age-restricted clearance level for adult-content robots'

    def handle(self, *args, **options):
        clearance, created = ClearanceLevel.objects.get_or_create(
            code='age_restricted',
            defaults={
                'name': 'Age Restricted (18+)',
                'description': 'Clearance for accessing age-restricted content including adult companion robots and humanoid partners. Requires age verification (18+).',
                'can_access_restricted': True,
                'can_access_military': False,
                'can_access_export_controlled': False,
                'minimum_clearance_required': 'public',
                'validity_months': 0,  # Age verification doesn't expire
                'requires_renewal': False,
                'requires_background_check': False,
                'priority': 2,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created age-restricted clearance level'))
        else:
            self.stdout.write(self.style.WARNING('Age-restricted clearance level already exists'))
        
        self.stdout.write(f'Clearance Level: {clearance.name}')
        self.stdout.write(f'Code: {clearance.code}')
        self.stdout.write(f'Priority: {clearance.priority}')

