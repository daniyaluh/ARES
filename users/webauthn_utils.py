"""
WebAuthn/FIDO2 utilities for authentication.
Handles credential registration and authentication.
"""
import base64
import secrets
import json
from typing import Dict, Optional, Tuple
from django.conf import settings


def generate_registration_challenge(user_id: str, username: str, display_name: str = None) -> Dict:
    """
    Generate a WebAuthn registration challenge.
    
    Args:
        user_id: User's unique identifier (email or UUID)
        username: User's username
        display_name: User's display name (optional)
    
    Returns:
        Dictionary containing the publicKeyCredentialCreationOptions
    """
    # Generate a random challenge (minimum 16 bytes, recommended 32+ bytes)
    # Use urlsafe base64 encoding and remove padding for WebAuthn
    challenge_bytes = secrets.token_bytes(32)
    challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')
    
    # Get the relying party (RP) info from settings
    # For localhost, use 'localhost' as RP ID (WebAuthn allows this without HTTPS)
    rp_id = getattr(settings, 'WEBAUTHN_RP_ID', 'localhost')
    rp_name = getattr(settings, 'WEBAUTHN_RP_NAME', 'ARES Marketplace')
    
    # Get origin from request if available, otherwise use settings
    origin = getattr(settings, 'WEBAUTHN_ORIGIN', None)
    if not origin:
        # Default to localhost for development
        origin = 'http://localhost:8000'
    
    # Create publicKeyCredentialCreationOptions
    options = {
        'challenge': challenge,
        'rp': {
            'name': rp_name,
            'id': rp_id,
        },
        'user': {
            'id': base64.urlsafe_b64encode(user_id.encode('utf-8')).decode('utf-8').rstrip('='),
            'name': username,
            'displayName': display_name or username,
        },
        'pubKeyCredParams': [
            {'type': 'public-key', 'alg': -7},   # ES256
            {'type': 'public-key', 'alg': -257},  # RS256
        ],
        'authenticatorSelection': {
            'authenticatorAttachment': 'cross-platform',
            'requireResidentKey': False,
            'userVerification': 'preferred',
        },
        'timeout': 60000,  # 60 seconds
        'attestation': 'direct',
    }
    
    # Store challenge in session (will be handled by view)
    return {
        'options': options,
        'challenge': challenge,
    }


def generate_authentication_challenge(credential_ids: list) -> Dict:
    """
    Generate a WebAuthn authentication challenge.
    
    Args:
        credential_ids: List of credential IDs to allow
    
    Returns:
        Dictionary containing the publicKeyCredentialRequestOptions
    """
    # Generate a random challenge
    challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # Get RP info
    rp_id = getattr(settings, 'WEBAUTHN_RP_ID', 'localhost')
    origin = getattr(settings, 'WEBAUTHN_ORIGIN', 'http://localhost:8000')
    
    # Convert credential IDs to base64url format
    allow_credentials = [
        {
            'id': cred_id,
            'type': 'public-key',
        }
        for cred_id in credential_ids
    ]
    
    options = {
        'challenge': challenge,
        'rpId': rp_id,
        'allowCredentials': allow_credentials,
        'timeout': 60000,
        'userVerification': 'preferred',
    }
    
    return {
        'options': options,
        'challenge': challenge,
    }


def verify_registration_response(credential: Dict, challenge: str, user_id: str) -> Tuple[bool, Optional[Dict]]:
    """
    Verify a WebAuthn registration response.
    This is a simplified verification - in production, you should use a proper WebAuthn library.
    
    Args:
        credential: The credential object from the client
        challenge: The original challenge
        user_id: The user ID that was used for registration
    
    Returns:
        Tuple of (success: bool, credential_data: Dict or None)
    """
    try:
        # Basic validation
        if not credential:
            return False, None
        
        # Extract credential data
        raw_id = credential.get('rawId')
        response = credential.get('response', {})
        
        if not raw_id or not response:
            return False, None
        
        # For a basic implementation, we'll store the credential as-is
        # In production, you should verify the attestation using a WebAuthn library
        credential_id = base64.urlsafe_b64encode(raw_id).decode('utf-8').rstrip('=')
        client_data_json = response.get('clientDataJSON')
        attestation_object = response.get('attestationObject')
        
        if not credential_id or not client_data_json:
            return False, None
        
        # Store credential data
        credential_data = {
            'credential_id': credential_id,
            'raw_id': base64.urlsafe_b64encode(raw_id).decode('utf-8').rstrip('='),
            'public_key': base64.urlsafe_b64encode(attestation_object).decode('utf-8').rstrip('=') if attestation_object else None,
            'client_data': client_data_json,
            'attestation': attestation_object,
        }
        
        return True, credential_data
    
    except Exception as e:
        print(f"Error verifying registration: {str(e)}")
        return False, None


def verify_authentication_response(credential: Dict, challenge: str, stored_credential: Dict) -> bool:
    """
    Verify a WebAuthn authentication response.
    This is a simplified verification - in production, use a proper WebAuthn library.
    
    Args:
        credential: The credential object from the client
        challenge: The original challenge
        stored_credential: The stored credential data
    
    Returns:
        bool: True if verification succeeds
    """
    try:
        if not credential:
            return False
        
        response = credential.get('response', {})
        credential_id = credential.get('id')
        raw_id = credential.get('rawId')
        
        if not response or not credential_id:
            return False
        
        # Basic validation - check credential ID matches
        stored_credential_id = stored_credential.get('credential_id') or stored_credential.get('raw_id')
        if stored_credential_id:
            # Compare base64url encoded IDs
            raw_id_b64 = base64.urlsafe_b64encode(raw_id).decode('utf-8').rstrip('=')
            if raw_id_b64 != stored_credential_id:
                return False
        
        # Check client data
        client_data_json = response.get('clientDataJSON')
        if not client_data_json:
            return False
        
        # In production, verify the signature using the stored public key
        # For now, we'll do basic validation
        authenticator_data = response.get('authenticatorData')
        signature = response.get('signature')
        
        if not authenticator_data or not signature:
            return False
        
        # Basic success - in production, verify cryptographic signature
        return True
    
    except Exception as e:
        print(f"Error verifying authentication: {str(e)}")
        return False

