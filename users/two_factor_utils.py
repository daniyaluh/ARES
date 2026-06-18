"""
Two-Factor Authentication utilities.
"""
import pyotp
from django.utils import timezone
from django.contrib.auth import get_user_model
from .auth_utils import verify_code, hash_code

User = get_user_model()


def verify_totp_code(user, code):
    """
    Verify a TOTP code for a user.
    
    Args:
        user: The user object
        code: The 6-digit TOTP code
    
    Returns:
        tuple: (success: bool, security_key: UserSecurityKey or None)
    """
    from .models import UserSecurityKey
    
    # Get active TOTP keys for the user
    totp_keys = UserSecurityKey.objects.filter(
        user=user,
        key_type='totp',
        is_active=True
    )
    
    for key in totp_keys:
        if key.secret_key:
            totp = pyotp.TOTP(key.secret_key)
            if totp.verify(code, valid_window=1):  # Allow 30 seconds before/after
                # Update last used timestamp
                key.last_used_at = timezone.now()
                key.save(update_fields=['last_used_at'])
                return True, key
    
    return False, None


def verify_backup_code(user, code):
    """
    Verify a backup code for a user.
    
    Args:
        user: The user object
        code: The backup code (formatted as XXXX-XXXX)
    
    Returns:
        tuple: (success: bool, security_key: UserSecurityKey or None)
    """
    from .models import UserSecurityKey
    
    # Get active backup code keys for the user
    backup_keys = UserSecurityKey.objects.filter(
        user=user,
        key_type='backup',
        is_active=True
    )
    
    for key in backup_keys:
        if key.secret_key:
            # Hashed codes are stored comma-separated
            hashed_codes = key.secret_key.split(',')
            code_hash = hash_code(code)
            
            if code_hash in hashed_codes:
                # Remove the used code from the list
                hashed_codes.remove(code_hash)
                
                if hashed_codes:
                    # Update the key with remaining codes
                    key.secret_key = ','.join(hashed_codes)
                    key.last_used_at = timezone.now()
                    key.save(update_fields=['secret_key', 'last_used_at'])
                else:
                    # All codes used, deactivate the key
                    key.is_active = False
                    key.last_used_at = timezone.now()
                    key.save(update_fields=['is_active', 'last_used_at'])
                
                return True, key
    
    return False, None


def verify_sms_code(user, code):
    """
    Verify an SMS code for a user.
    Note: In production, codes should expire after a short time.
    
    Args:
        user: The user object
        code: The SMS code
    
    Returns:
        tuple: (success: bool, security_key: UserSecurityKey or None)
    """
    from .models import UserSecurityKey
    
    # Get active SMS keys for the user
    sms_keys = UserSecurityKey.objects.filter(
        user=user,
        key_type='sms',
        is_active=True
    )
    
    for key in sms_keys:
        if key.secret_key and verify_code(key.secret_key, code):
            key.last_used_at = timezone.now()
            key.save(update_fields=['last_used_at'])
            return True, key
    
    return False, None


def verify_email_code(user, code, purpose='2fa'):
    """
    Verify an email code for a user.
    Uses the email verification service which generates fresh codes on demand.
    
    Args:
        user: The user object
        code: The email code
        purpose: Purpose of the code ('2fa', 'purchase', etc.)
    
    Returns:
        tuple: (success: bool, security_key: UserSecurityKey or None)
    """
    from .models import UserSecurityKey
    from .email_verification_service import verify_email_code_from_cache
    
    # Get active email keys for the user
    email_keys = UserSecurityKey.objects.filter(
        user=user,
        key_type='email',
        is_active=True
    )
    
    if not email_keys.exists():
        return False, None
    
    # Verify using the cache-based system (fresh codes generated on demand)
    if verify_email_code_from_cache(user, code, purpose=purpose):
        # Code is valid - update the security key
        key = email_keys.first()  # Update the first active email key
        key.last_used_at = timezone.now()
        key.save(update_fields=['last_used_at'])
        return True, key
    
    return False, None


def verify_2fa_code(user, code, preferred_type=None, purpose='2fa'):
    """
    Verify a 2FA code using any available method.
    Tries methods in order: TOTP, Backup Code, SMS, Email
    
    Args:
        user: The user object
        code: The verification code
        preferred_type: Preferred verification type ('totp', 'backup', 'sms', 'email')
        purpose: Purpose of verification ('2fa', 'purchase', etc.) - default '2fa'
    
    Returns:
        tuple: (success: bool, security_key: UserSecurityKey or None, method_used: str or None)
    """
    from .models import UserSecurityKey
    
    # Check if user has 2FA enabled
    if not user.two_factor_enabled:
        return False, None, None
    
    # Get active security keys, ordered by preference
    active_keys = UserSecurityKey.objects.filter(
        user=user,
        is_active=True
    ).order_by('-is_primary', '-created_at')
    
    if not active_keys.exists():
        return False, None, None
    
    # Try preferred type first if specified
    if preferred_type:
        preferred_keys = active_keys.filter(key_type=preferred_type)
        if preferred_keys.exists():
            for key in preferred_keys:
                success, verified_key = _verify_code_by_type(key, code, purpose=purpose)
                if success:
                    return True, verified_key, preferred_type
    
    # Try all methods in order of preference
    verification_order = ['totp', 'backup', 'sms', 'email']
    
    for method in verification_order:
        method_keys = active_keys.filter(key_type=method)
        for key in method_keys:
            success, verified_key = _verify_code_by_type(key, code, purpose=purpose)
            if success:
                return True, verified_key, method
    
    return False, None, None


def _verify_code_by_type(security_key, code, purpose='2fa'):
    """
    Helper function to verify code based on security key type.
    
    Args:
        security_key: UserSecurityKey instance
        code: The verification code
        purpose: Purpose of verification ('2fa', 'purchase', etc.) - default '2fa'
    
    Returns:
        tuple: (success: bool, security_key: UserSecurityKey or None)
    """
    if security_key.key_type == 'totp' and security_key.secret_key:
        totp = pyotp.TOTP(security_key.secret_key)
        if totp.verify(code, valid_window=1):
            # timezone is already imported at the top of the file
            security_key.last_used_at = timezone.now()
            security_key.save(update_fields=['last_used_at'])
            return True, security_key
    
    elif security_key.key_type == 'backup' and security_key.secret_key:
        from .auth_utils import hash_code
        hashed_codes = security_key.secret_key.split(',')
        code_hash = hash_code(code)
        if code_hash in hashed_codes:
            hashed_codes.remove(code_hash)
            if hashed_codes:
                security_key.secret_key = ','.join(hashed_codes)
            else:
                security_key.is_active = False
            # timezone is already imported at the top of the file
            security_key.last_used_at = timezone.now()
            security_key.save()
            return True, security_key
    
    elif security_key.key_type == 'email':
        # Email codes are verified through the email verification service
        # which generates fresh codes on demand and stores them in cache
        from .email_verification_service import verify_email_code_from_cache
        
        # Try to verify from cache (for fresh codes)
        if verify_email_code_from_cache(security_key.user, code, purpose=purpose):
            # timezone is already imported at the top of the file
            security_key.last_used_at = timezone.now()
            security_key.save(update_fields=['last_used_at'])
            return True, security_key
        
        # Fallback: check if it's the old stored hash (for backward compatibility)
        # This shouldn't normally happen since we generate fresh codes, but just in case
        if security_key.secret_key and security_key.secret_key != 'email_key_placeholder':
            from .auth_utils import verify_code
            # verify_code takes (stored_hash, provided_code) as parameters
            if verify_code(security_key.secret_key, code):
                # timezone is already imported at the top of the file
                security_key.last_used_at = timezone.now()
                security_key.save(update_fields=['last_used_at'])
                return True, security_key
    
    elif security_key.key_type == 'fido2':
        # FIDO2 authentication is handled separately via WebAuthn API
        # This function is for code-based 2FA, so FIDO2 should be handled in the login flow
        # For now, return False (FIDO2 auth should be done via separate endpoint)
        return False, None
    
    elif security_key.key_type == 'sms' and security_key.secret_key:
        from .auth_utils import verify_code
        if verify_code(security_key.secret_key, code):
            # timezone is already imported at the top of the file
            security_key.last_used_at = timezone.now()
            security_key.save(update_fields=['last_used_at'])
            return True, security_key
    
    return False, None


def requires_2fa(user):
    """
    Check if a user requires 2FA for login.
    
    Args:
        user: The user object
    
    Returns:
        bool: True if 2FA is enabled and user has active security keys
    """
    if not user.two_factor_enabled:
        return False
    
    from .models import UserSecurityKey
    return UserSecurityKey.objects.filter(user=user, is_active=True).exists()


def get_primary_2fa_method(user):
    """
    Get the primary 2FA method for a user.
    
    Args:
        user: The user object
    
    Returns:
        str or None: The key type ('totp', 'sms', 'email', etc.) or None
    """
    from .models import UserSecurityKey
    
    primary_key = UserSecurityKey.objects.filter(
        user=user,
        is_active=True,
        is_primary=True
    ).first()
    
    if primary_key:
        return primary_key.key_type
    
    # If no primary, return the first active key type
    first_key = UserSecurityKey.objects.filter(
        user=user,
        is_active=True
    ).first()
    
    return first_key.key_type if first_key else None

