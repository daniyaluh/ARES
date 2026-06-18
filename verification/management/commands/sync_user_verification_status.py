"""
Management command to sync user verification status with their clearance levels.
Sets is_verified=True for users who have approved clearance levels.
"""
from django.core.management.base import BaseCommand
from verification.models import VerificationRequest
from django.utils import timezone


class Command(BaseCommand):
    help = 'Sync user verification status: set is_verified=True for users with approved clearance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Find users with approved verification requests
        approved_requests = VerificationRequest.objects.filter(
            status='approved',
            current_clearance__isnull=False
        ).select_related('user', 'current_clearance').exclude(
            reviewed_at__isnull=True
        ).order_by('-reviewed_at', '-current_clearance__priority')
        
        updated_count = 0
        already_verified_count = 0
        
        # Process each approved request
        processed_users = set()
        for request in approved_requests:
            # Skip if we've already processed this user (we want the highest clearance)
            if request.user.id in processed_users:
                continue
            
            # Check if clearance is expired
            if request.expires_at and request.expires_at < timezone.now():
                continue  # Skip expired clearances
            
            processed_users.add(request.user.id)
            
            if not request.user.is_verified:
                if not dry_run:
                    request.user.is_verified = True
                    request.user.save(update_fields=['is_verified'])
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{request.user.email}: Set is_verified=True '
                        f'(Clearance: {request.current_clearance.name})'
                    )
                )
            else:
                already_verified_count += 1
        
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Would update {updated_count} users'))
            self.stdout.write(self.style.WARNING(f'{already_verified_count} users already verified'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} users'))
            self.stdout.write(self.style.WARNING(f'{already_verified_count} users were already verified'))







