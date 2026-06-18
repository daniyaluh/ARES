"""
Advanced Security Layer for ARES Platform.
Custom decorators and middleware for clearance-based access control.
"""
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


# Clearance level priority mapping (higher = more clearance)
CLEARANCE_PRIORITY = {
    'none': 0,
    'public': 10,  # Public Trust - Level 0 access
    'age_restricted': 25,  # Age-restricted content (18+) - Adult content
    'confidential': 15,
    'secret': 20,
    'top_secret': 35,
    'military': 40,  # Military Clearance
    'government': 40,
    'contractor': 35,
    'research': 50,  # Research & Advanced Robotics - Maximum priority
}


def get_clearance_priority(clearance_code):
    """Get priority level for a clearance code."""
    return CLEARANCE_PRIORITY.get(clearance_code.lower(), 0)


def clearance_required(level='secret', redirect_url=None, api_response=False):
    """
    Decorator to require a specific clearance level for accessing a view.
    
    Args:
        level: Required clearance level (e.g., 'secret', 'top_secret', 'military')
        redirect_url: URL to redirect to if clearance insufficient (default: verification request)
        api_response: If True, return JSON response instead of redirect (for API views)
    
    Usage:
        @clearance_required(level='TOP_SECRET')
        def sensitive_view(request):
            ...
        
        @clearance_required(level='military', api_response=True)
        def api_endpoint(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            from .models import VerificationRequest
            from .utils import get_user_clearance, has_clearance
            
            # Check authentication
            if not request.user.is_authenticated:
                if api_response:
                    return JsonResponse({
                        'error': 'Authentication required',
                        'code': 'AUTH_REQUIRED'
                    }, status=401)
                messages.error(request, "You must be logged in to access this page.")
                return redirect('users:login')
            
            # Superusers bypass all checks
            if request.user.is_superuser:
                logger.info(f"Superuser {request.user.username} bypassed clearance check for {level}")
                return view_func(request, *args, **kwargs)
            
            # Get user's current clearance
            user_clearance = get_user_clearance(request.user)
            
            if not user_clearance:
                logger.warning(
                    f"User {request.user.username} attempted to access {level} resource without clearance. "
                    f"IP: {request.META.get('REMOTE_ADDR')}"
                )
                
                if api_response:
                    return JsonResponse({
                        'error': 'Clearance required',
                        'code': 'CLEARANCE_REQUIRED',
                        'required_level': level,
                        'message': f'This resource requires {level.upper()} clearance level'
                    }, status=403)
                
                messages.error(
                    request,
                    f"This resource requires {level.upper()} clearance level. "
                    "Please submit a verification request."
                )
                return redirect(redirect_url or 'verification:request')
            
            # Check if user has sufficient clearance
            required_priority = get_clearance_priority(level)
            user_priority = get_clearance_priority(user_clearance.code)
            
            if user_priority < required_priority:
                logger.warning(
                    f"User {request.user.username} (clearance: {user_clearance.code}, priority: {user_priority}) "
                    f"attempted to access {level} resource (required priority: {required_priority}). "
                    f"IP: {request.META.get('REMOTE_ADDR')}"
                )
                
                if api_response:
                    return JsonResponse({
                        'error': 'Insufficient clearance',
                        'code': 'INSUFFICIENT_CLEARANCE',
                        'required_level': level,
                        'required_priority': required_priority,
                        'user_level': user_clearance.code,
                        'user_priority': user_priority,
                        'message': f'This resource requires {level.upper()} clearance. '
                                  f'Your current clearance: {user_clearance.name}'
                    }, status=403)
                
                messages.error(
                    request,
                    f"Insufficient clearance level. This resource requires {level.upper()} clearance. "
                    f"Your current clearance: {user_clearance.name}"
                )
                return redirect(redirect_url or 'verification:my-clearance')
            
            # Check if clearance is expired
            approved_request = VerificationRequest.objects.filter(
                user=request.user,
                status='approved',
                current_clearance=user_clearance
            ).first()
            
            if approved_request and approved_request.is_expired:
                logger.warning(
                    f"User {request.user.username} attempted to access {level} resource with expired clearance"
                )
                
                if api_response:
                    return JsonResponse({
                        'error': 'Clearance expired',
                        'code': 'CLEARANCE_EXPIRED',
                        'message': 'Your clearance has expired. Please renew your verification.'
                    }, status=403)
                
                messages.warning(
                    request,
                    "Your clearance has expired. Please renew your verification to access this resource."
                )
                return redirect('verification:clearance-renew')
            
            # Log successful access
            logger.info(
                f"User {request.user.username} (clearance: {user_clearance.code}) "
                f"accessed {level} resource successfully"
            )
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator


def military_clearance_required(redirect_url=None, api_response=False):
    """
    Decorator specifically for military-grade resources.
    Shorthand for @clearance_required(level='military')
    
    Usage:
        @military_clearance_required()
        def military_robot_view(request):
            ...
    """
    return clearance_required(level='military', redirect_url=redirect_url, api_response=api_response)


def top_secret_clearance_required(redirect_url=None, api_response=False):
    """
    Decorator for TOP_SECRET level resources.
    Shorthand for @clearance_required(level='top_secret')
    
    Usage:
        @top_secret_clearance_required()
        def classified_view(request):
            ...
    """
    return clearance_required(level='top_secret', redirect_url=redirect_url, api_response=api_response)


def restricted_access_required(api_response=False):
    """
    Decorator for any restricted resource (requires any clearance above 'none').
    
    Usage:
        @restricted_access_required()
        def restricted_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            from .utils import get_user_clearance
            
            if not request.user.is_authenticated:
                if api_response:
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                messages.error(request, "You must be logged in to access this page.")
                return redirect('users:login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            user_clearance = get_user_clearance(request.user)
            
            if not user_clearance:
                if api_response:
                    return JsonResponse({
                        'error': 'Verification required',
                        'code': 'VERIFICATION_REQUIRED'
                    }, status=403)
                messages.error(request, "Verification required to access this resource.")
                return redirect('verification:request')
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator


# Class-based view decorator
def class_clearance_required(level='secret'):
    """
    Decorator for class-based views.
    
    Usage:
        @method_decorator(clearance_required(level='top_secret'), name='dispatch')
        class ClassifiedView(ListView):
            ...
    """
    def decorator(cls):
        original_dispatch = cls.dispatch
        
        @method_decorator(clearance_required(level=level))
        def dispatch(self, request, *args, **kwargs):
            return original_dispatch(self, request, *args, **kwargs)
        
        cls.dispatch = dispatch
        return cls
    return decorator


# Permission-based decorators
def can_access_military_robots(view_func):
    """
    Decorator to check if user can access military-grade robots.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from .utils import get_user_clearance
        
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('users:login')
        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        user_clearance = get_user_clearance(request.user)
        
        if not user_clearance or not user_clearance.can_access_military:
            messages.error(
                request,
                "Military clearance required to access military-grade autonomous systems."
            )
            return redirect('verification:request')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def can_access_export_controlled(view_func):
    """
    Decorator to check if user can access export-controlled products.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from .utils import get_user_clearance
        
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('users:login')
        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        user_clearance = get_user_clearance(request.user)
        
        if not user_clearance or not user_clearance.can_access_export_controlled:
            messages.error(
                request,
                "Export license clearance required to access export-controlled products."
            )
            return redirect('verification:request')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view



