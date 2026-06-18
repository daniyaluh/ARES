"""
Management command to set up test users.
Creates exactly one admin, one staff, one regular user, and one seller.
Clears all verification statuses.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Profile, NotificationPreference
from verification.models import VerificationRequest

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up test users: 1 admin, 1 staff, 1 user, 1 seller. Clear all verification statuses.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting test user setup...'))
        
        # Clear all verification requests and statuses
        self.stdout.write('Clearing all verification statuses...')
        VerificationRequest.objects.all().delete()
        User.objects.all().update(is_verified=False)
        self.stdout.write(self.style.SUCCESS('All verification statuses cleared.'))
        
        # Delete all existing users
        self.stdout.write('Removing existing users...')
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All existing users removed.'))
        
        # Create Admin
        self.stdout.write('Creating admin user...')
        admin = User.objects.create_user(
            email='admin@ares.com',
            username='admin',
            password='admin1234',
            first_name='System',
            last_name='Administrator',
            role='admin',
            is_staff=True,
            is_superuser=True,
            is_verified=False
        )
        Profile.objects.create(user=admin)
        NotificationPreference.objects.create(user=admin)
        self.stdout.write(self.style.SUCCESS(f'Created admin: {admin.username} ({admin.email})'))
        
        # Create Staff
        self.stdout.write('Creating staff user...')
        staff = User.objects.create_user(
            email='staff@ares.com',
            username='staff',
            password='staff1234',
            first_name='Support',
            last_name='Staff',
            role='support',
            is_staff=True,
            is_superuser=False,
            is_verified=False
        )
        Profile.objects.create(user=staff)
        NotificationPreference.objects.create(user=staff)
        self.stdout.write(self.style.SUCCESS(f'Created staff: {staff.username} ({staff.email})'))
        
        # Create Regular User
        self.stdout.write('Creating regular user...')
        user = User.objects.create_user(
            email='user@ares.com',
            username='testuser',
            password='user1234',
            first_name='Test',
            last_name='User',
            role='buyer',
            is_staff=False,
            is_superuser=False,
            is_verified=False
        )
        Profile.objects.create(user=user)
        NotificationPreference.objects.create(user=user)
        self.stdout.write(self.style.SUCCESS(f'Created user: {user.username} ({user.email})'))
        
        # Create Seller
        self.stdout.write('Creating seller user...')
        seller = User.objects.create_user(
            email='seller@ares.com',
            username='seller',
            password='seller1234',
            first_name='Robot',
            last_name='Seller',
            role='seller',
            is_staff=False,
            is_superuser=False,
            is_verified=False,
            is_seller_approved=True
        )
        Profile.objects.create(user=seller)
        NotificationPreference.objects.create(user=seller)
        self.stdout.write(self.style.SUCCESS(f'Created seller: {seller.username} ({seller.email})'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Test Users Setup Complete ==='))
        self.stdout.write(self.style.SUCCESS('Admin: admin@ares.com / admin1234'))
        self.stdout.write(self.style.SUCCESS('Staff: staff@ares.com / staff1234'))
        self.stdout.write(self.style.SUCCESS('User: user@ares.com / user1234'))
        self.stdout.write(self.style.SUCCESS('Seller: seller@ares.com / seller1234'))
        self.stdout.write(self.style.WARNING('All users are unverified. You can test verification from scratch.'))









