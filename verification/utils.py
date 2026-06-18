"""
Utility functions for the Verification Engine.
"""
from django.core.exceptions import PermissionDenied
from django.conf import settings
from .models import VerificationRequest, ClearanceLevel


def get_user_clearance(user):
    """
    Get the current active clearance level for a user.
    Returns the highest approved clearance level.
    """
    if not user or not user.is_authenticated:
        return None
    
    # Get approved verification requests with clearance
    approved_requests = VerificationRequest.objects.filter(
        user=user,
        status='approved',
        current_clearance__isnull=False
    ).select_related('current_clearance').exclude(
        reviewed_at__isnull=True
    ).order_by('-reviewed_at', '-current_clearance__priority')
    
    # Also check requests without reviewed_at (shouldn't happen, but just in case)
    if not approved_requests.exists():
        approved_requests = VerificationRequest.objects.filter(
            user=user,
            status='approved',
            current_clearance__isnull=False
        ).select_related('current_clearance').order_by('-current_clearance__priority', '-created_at')
    
    # Get the first non-expired request
    for approved_request in approved_requests:
        if not approved_request.is_expired:
            return approved_request.current_clearance
    
    return None


def has_clearance(user, required_clearance_code):
    """
    Check if user has the required clearance level.
    
    Args:
        user: User instance
        required_clearance_code: Code of the required clearance level
    
    Returns:
        bool: True if user has sufficient clearance
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusers and staff bypass all checks
    if user.is_superuser or user.is_staff:
        return True
    
    user_clearance = get_user_clearance(user)
    if not user_clearance:
        return False
    
    # Get required clearance level
    try:
        required_clearance = ClearanceLevel.objects.get(code=required_clearance_code, is_active=True)
    except ClearanceLevel.DoesNotExist:
        return False
    
    # Compare priority (higher priority = higher clearance)
    return user_clearance.priority >= required_clearance.priority


def can_access_robot(user, robot):
    """
    Check if user can access a specific robot based on restrictions.
    
    Args:
        user: User instance
        robot: Robot instance
    
    Returns:
        tuple: (can_access: bool, reason: str)
    """
    if not user or not user.is_authenticated:
        return False, "Authentication required"
    
    # Superusers and staff bypass all checks
    if user.is_superuser or user.is_staff:
        return True, "Staff/Admin access"
    
    # Check if robot requires verification
    if not robot.requires_verification and not robot.is_restricted:
        return True, "No restrictions"
    
    # Get usage restrictions
    try:
        usage_restriction = robot.usage_restriction
    except AttributeError:
        # Robot doesn't have usage restriction, check robot flags
        if robot.is_restricted or robot.requires_verification:
            user_clearance = get_user_clearance(user)
            if not user_clearance:
                return False, "Verification required for this product"
            
            # Check if clearance allows access to restricted items
            if not user_clearance.can_access_restricted:
                return False, "Insufficient clearance level"
            
            return True, "Access granted"
    
    # Check restriction level
    restriction_level = usage_restriction.restriction_level
    
    if restriction_level == 'none':
        return True, "No restrictions"
    
    if restriction_level in ['banned']:
        return False, "Product is banned"
    
    # Check age-restricted access
    if restriction_level == 'age_restricted':
        minimum_age = usage_restriction.minimum_age or 18  # Default to 18+ if not specified
        
        # Check user age if available (requires user profile with date_of_birth)
        if hasattr(user, 'profile') and hasattr(user.profile, 'date_of_birth') and user.profile.date_of_birth:
            from datetime import date
            today = date.today()
            birth_date = user.profile.date_of_birth
            user_age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if user_age < minimum_age:
                return False, f"Must be {minimum_age} years or older to access this product. You are {user_age} years old."
            # Age verified via profile, allow access
            return True, "Age verification passed"
        else:
            # If age cannot be verified from profile, check clearance level
            # Users with clearance priority >= 25 (age_restricted, military, research) can access 18+ content
            user_clearance = get_user_clearance(user)
            if user_clearance and user_clearance.priority >= 25:
                # User has clearance level >= 25, which includes age_restricted (25), military (40), research (50)
                return True, f"Access granted via {user_clearance.name} clearance"
            elif not user_clearance:
                return False, f"Age verification clearance required (must be {minimum_age}+). Please submit a verification request."
            else:
                # User has clearance but priority < 25 (e.g., public at 10)
                return False, f"Age verification clearance required (must be {minimum_age}+). Your current clearance ({user_clearance.name}) does not grant access to age-restricted content."
    
    # Check if verification is required
    if usage_restriction.requires_verification or restriction_level in ['clearance_required', 'military_only']:
        user_clearance = get_user_clearance(user)
        
        if not user_clearance:
            return False, "Verification and clearance required for this product"
        
        # Check military-only access
        if restriction_level == 'military_only':
            if not user_clearance.can_access_military:
                return False, "Military clearance required"
        
        # Check export-controlled access
        # NOTE: We now check for actual export license ownership, not just clearance capability
        if usage_restriction.requires_export_license:
            # User needs an actual export license, not just clearance
            # Check if robot has a SPECIFIC license requirement
            if robot.required_license != 'none':
                # Specific license required - this will be checked by user_has_valid_license
                # The can_access_robot only checks general access here
                pass
            else:
                # No specific license required, but export license needed
                # Check if user has ANY valid export license
                if not robot.user_has_any_valid_export_license(user):
                    return False, "An export license is required to purchase this product. Please apply for an export license."
        
        # Check clearance level priority
        if restriction_level == 'clearance_required':
            # Require at least 'secret' level for clearance_required
            required_clearance = ClearanceLevel.objects.filter(
                code__in=['secret', 'top_secret', 'military', 'government']
            ).order_by('-priority').first()
            
            if required_clearance and user_clearance.priority < required_clearance.priority:
                return False, f"Insufficient clearance level. Required: {required_clearance.name}"
    
    # Check geographic restrictions
    if hasattr(user, 'address_book'):
        user_addresses = user.address_book.filter(is_default=True, is_active=True).first()
        if user_addresses:
            user_country = user_addresses.country
            
            if usage_restriction.restricted_countries and user_country in usage_restriction.restricted_countries:
                return False, f"Product restricted in {user_country}"
            
            if usage_restriction.embargoed_countries and user_country in usage_restriction.embargoed_countries:
                return False, f"Product embargoed in {user_country}"
            
            if usage_restriction.allowed_countries and user_country not in usage_restriction.allowed_countries:
                return False, f"Product not available in {user_country}"
    
    # Check age restrictions
    if usage_restriction.minimum_age:
        # Assuming user has a profile with birth_date or age
        # This would need to be implemented based on your user model
        pass
    
    return True, "Access granted"


def is_military_grade_robot(robot):
    """
    Check if a robot is classified as military-grade.
    
    Args:
        robot: Robot instance
    
    Returns:
        bool: True if robot is military-grade
    """
    # Check robot type
    if robot.robot_type == 'military_autonomous':
        return True
    
    # Check if marked as restricted
    if robot.is_restricted:
        return True
    
    # Check usage restrictions
    try:
        usage_restriction = robot.usage_restriction
        if usage_restriction.restriction_level in ['military_only', 'clearance_required']:
            return True
        if usage_restriction.military_use_allowed and not usage_restriction.commercial_use_allowed:
            return True
    except AttributeError:
        pass
    
    return False


def requires_verification(robot):
    """
    Check if a robot requires verification.
    
    Args:
        robot: Robot instance
    
    Returns:
        bool: True if verification is required
    """
    if robot.requires_verification:
        return True
    
    try:
        usage_restriction = robot.usage_restriction
        if usage_restriction.requires_verification:
            return True
        if usage_restriction.restriction_level in ['clearance_required', 'military_only', 'license_required']:
            return True
    except AttributeError:
        pass
    
    return False

