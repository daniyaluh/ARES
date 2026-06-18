"""
Email verification code service.
Handles generation, storage, and delivery of email verification codes.
"""
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.conf import settings
from .auth_utils import generate_email_code, hash_code
import secrets


def generate_and_send_email_code(user, purpose='2fa'):
    """
    Generate a fresh email verification code and send it (or display it in development).
    
    Args:
        user: The user object
        purpose: Purpose of the code ('2fa', 'purchase', etc.)
    
    Returns:
        tuple: (code: str, success: bool, message: str)
    """
    # Generate a fresh code
    code = generate_email_code(length=6)
    
    # Store code in cache with expiration (5 minutes)
    cache_key = f'email_code_{user.id}_{purpose}'
    cache.set(cache_key, hash_code(code), timeout=300)  # 5 minutes
    
    # In development, we'll display the code
    # In production, this would send an actual email
    email_sent = False
    
    # Check if we're in development mode
    is_development = settings.DEBUG or getattr(settings, 'EMAIL_BACKEND', '').endswith('console.EmailBackend')
    
    if is_development:
        # Development mode - don't send email, just return the code to display
        # The code will be shown on the login/2FA page
        message = f"Development mode: Code will be displayed on screen (This code will be sent via email in production)"
        email_sent = True  # We consider it "sent" because we're providing it
    else:
        # Production mode - send actual email
        try:
            from django.core.mail import send_mail
            send_mail(
                subject='ARES Marketplace - Email Verification Code',
                message=f'Your email verification code is: {code}\n\nThis code will expire in 5 minutes.\n\nIf you did not request this code, please ignore this email.',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ares.com'),
                recipient_list=[user.email],
                fail_silently=False,
            )
            message = f"Verification code sent to {user.email}"
            email_sent = True
        except Exception as e:
            message = f"Failed to send email: {str(e)}"
            email_sent = False
    
    return code, email_sent, message


def verify_email_code_from_cache(user, provided_code, purpose='2fa'):
    """
    Verify an email code from cache.
    
    Args:
        user: The user object
        provided_code: The code provided by the user
        purpose: Purpose of the code ('2fa', 'purchase', etc.)
    
    Returns:
        bool: True if code is valid, False otherwise
    """
    cache_key = f'email_code_{user.id}_{purpose}'
    stored_hash = cache.get(cache_key)
    
    if not stored_hash:
        return False
    
    # Verify the code
    provided_hash = hash_code(provided_code)
    if secrets.compare_digest(stored_hash, provided_hash):
        # Code is valid - delete it so it can't be reused
        cache.delete(cache_key)
        return True
    
    return False


def get_email_code_from_cache(user, purpose='2fa'):
    """
    Get the current email code from cache (for display in development).
    This should only be used in development mode for testing.
    
    Args:
        user: The user object
        purpose: Purpose of the code ('2fa', 'purchase', etc.)
    
    Returns:
        str or None: The code if available, None otherwise
    """
    if not settings.DEBUG:
        return None  # Never expose codes in production
    
    # We can't retrieve the code from the hash, but we can check if a code exists
    cache_key = f'email_code_{user.id}_{purpose}'
    stored_hash = cache.get(cache_key)
    
    if stored_hash:
        # In development, we need to store the plain code somewhere temporarily
        # Let's use a separate cache entry
        code_cache_key = f'email_code_plain_{user.id}_{purpose}'
        return cache.get(code_cache_key)
    
    return None



