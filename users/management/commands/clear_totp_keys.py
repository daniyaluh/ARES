"""
Django management command to clear all TOTP (authenticator app) security keys.
This allows users to re-setup their authenticator app from scratch.
"""
from django.core.management.base import BaseCommand
from django.db import models
from users.models import UserSecurityKey, CustomUser
from django.utils import timezone


class Command(BaseCommand):
    help = 'Clear all TOTP (authenticator app) security keys from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Clear TOTP keys for a specific user (email or username)',
            default=None,
        )
        parser.add_argument(
            '--disable-2fa',
            action='store_true',
            help='Force disable 2FA for all affected users (even if they have other security keys)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        user_filter = options['user']
        disable_2fa = options['disable_2fa']
        force = options['force']

        # Filter TOTP keys
        totp_keys = UserSecurityKey.objects.filter(key_type='totp')
        
        if user_filter:
            # Filter by user
            try:
                user = CustomUser.objects.get(
                    models.Q(email=user_filter) | models.Q(username=user_filter)
                )
                totp_keys = totp_keys.filter(user=user)
                self.stdout.write(
                    self.style.WARNING(
                        f'Found {totp_keys.count()} TOTP key(s) for user: {user.email} ({user.username})'
                    )
                )
            except CustomUser.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User not found: {user_filter}')
                )
                return
            except CustomUser.MultipleObjectsReturned:
                self.stdout.write(
                    self.style.ERROR(f'Multiple users found for: {user_filter}')
                )
                return
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Found {totp_keys.count()} TOTP key(s) in total'
                )
            )

        if totp_keys.count() == 0:
            self.stdout.write(
                self.style.SUCCESS('No TOTP keys found. Nothing to clear.')
            )
            return

        # Show details
        self.stdout.write('\nTOTP Keys to be deleted:')
        for key in totp_keys:
            self.stdout.write(
                f'  - User: {key.user.email} ({key.user.username})'
                f' | Name: {key.name}'
                f' | Active: {key.is_active}'
                f' | Primary: {key.is_primary}'
                f' | Created: {key.created_at}'
            )

        # Confirmation
        if not force:
            confirm = input('\nAre you sure you want to delete these TOTP keys? (yes/no): ')
            if confirm.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Get affected users before deletion
        affected_users = set(totp_keys.values_list('user', flat=True).distinct())
        
        # Delete TOTP keys
        deleted_count = totp_keys.count()
        totp_keys.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully deleted {deleted_count} TOTP key(s)'
            )
        )

        # Disable 2FA for users who only had TOTP keys (or always if --disable-2fa flag is set)
        disabled_count = 0
        for user_id in affected_users:
            user = CustomUser.objects.get(id=user_id)
            
            # Check if user has any other active security keys
            other_keys = UserSecurityKey.objects.filter(
                user=user,
                is_active=True
            )
            
            # If --disable-2fa flag is set, always disable 2FA regardless of other keys
            # Otherwise, only disable if they have no other active keys
            if disable_2fa or not other_keys.exists():
                if user.two_factor_enabled:
                    user.two_factor_enabled = False
                    user.save(update_fields=['two_factor_enabled'])
                    disabled_count += 1
                    reason = 'disabled via --disable-2fa flag' if disable_2fa else 'no other security keys'
                    self.stdout.write(
                        self.style.WARNING(
                            f'  - Disabled 2FA for user: {user.email} ({reason})'
                        )
                    )
        
        if disabled_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Disabled 2FA for {disabled_count} user(s)'
                )
            )
        elif not disable_2fa:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ All affected users still have other security keys - 2FA remains enabled'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                '\n✓ TOTP keys cleared successfully. You can now re-setup your authenticator app and enable 2FA again.'
            )
        )

