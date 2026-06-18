"""
Authentication utilities for security keys.
"""
import secrets
import string
import base64
import hashlib
from django.utils import timezone
from datetime import timedelta


def generate_backup_codes(count=10, length=8):
    """
    Generate backup codes for account recovery.
    
    Args:
        count: Number of codes to generate
        length: Length of each code
    
    Returns:
        List of backup codes
    """
    codes = []
    for _ in range(count):
        # Generate codes using uppercase letters and numbers
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))
        # Format as XXXX-XXXX for readability
        formatted_code = f"{code[:4]}-{code[4:]}"
        codes.append(formatted_code)
    return codes


def generate_sms_code(length=6):
    """
    Generate a numeric SMS verification code.
    
    Args:
        length: Length of the code
    
    Returns:
        Numeric code as string
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_email_code(length=6):
    """
    Generate an alphanumeric email verification code.
    
    Args:
        length: Length of the code
    
    Returns:
        Alphanumeric code as string
    """
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def hash_code(code):
    """
    Hash a verification code for storage.
    
    Args:
        code: The code to hash
    
    Returns:
        Hashed code as hex string
    """
    return hashlib.sha256(code.encode()).hexdigest()


def verify_code(stored_hash, provided_code):
    """
    Verify a code against a stored hash.
    
    Args:
        stored_hash: The stored hash of the code
        provided_code: The code provided by the user
    
    Returns:
        True if codes match, False otherwise
    """
    provided_hash = hash_code(provided_code)
    return secrets.compare_digest(stored_hash, provided_hash)









