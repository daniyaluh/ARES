"""
Decorators for access control based on verification and clearance.
"""
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .utils import can_access_robot, has_clearance, requires_verification, is_military_grade_robot


def require_verification(view_func):
    """
    Decorator to require user verification for accessing a view.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from .models import VerificationRequest
        
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('users:login')
        
        # Staff and superusers bypass verification
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        # Check if user has approved verification
        approved_request = VerificationRequest.objects.filter(
            user=request.user,
            status='approved',
            current_clearance__isnull=False
        ).first()
        
        if not approved_request or approved_request.is_expired:
            messages.warning(
                request,
                "Verification required. Please submit a verification request to access restricted products."
            )
            return redirect('verification:request')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def require_clearance(clearance_code):
    """
    Decorator to require a specific clearance level.
    
    Usage:
        @require_clearance('secret')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to access this page.")
                return redirect('users:login')
            
            if not has_clearance(request.user, clearance_code):
                messages.error(
                    request,
                    f"You do not have the required clearance level ({clearance_code}) to access this page."
                )
                raise PermissionDenied("Insufficient clearance level")
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator


def require_robot_access(view_func):
    """
    Decorator to check if user can access a robot.
    Expects 'robot_id' or 'product_id' in kwargs or URL.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from products.models import Robot, Product
        
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('users:login')
        
        # Get robot from kwargs
        robot_id = kwargs.get('robot_id')
        product_id = kwargs.get('product_id')
        
        robot = None
        
        if robot_id:
            try:
                robot = Robot.objects.select_related('product', 'usage_restriction').get(id=robot_id)
            except Robot.DoesNotExist:
                messages.error(request, "Robot not found.")
                raise PermissionDenied("Robot not found")
        
        elif product_id:
            try:
                product = Product.objects.get(id=product_id)
                robot = getattr(product, 'robot', None)
            except Product.DoesNotExist:
                messages.error(request, "Product not found.")
                raise PermissionDenied("Product not found")
        
        if not robot:
            # If no robot found, allow access (might be a regular product)
            return view_func(request, *args, **kwargs)
        
        # Check access
        can_access, reason = can_access_robot(request.user, robot)
        
        if not can_access:
            messages.error(request, reason)
            
            # If verification is required, redirect to verification request
            if requires_verification(robot):
                return redirect('verification:request')
            
            raise PermissionDenied(reason)
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def require_military_clearance(view_func):
    """
    Decorator specifically for military-grade robot access.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('users:login')
        
        if not has_clearance(request.user, 'military'):
            # Check if user has any military-related clearance
            from .models import VerificationRequest
            approved_request = VerificationRequest.objects.filter(
                user=request.user,
                status='approved',
                current_clearance__can_access_military=True
            ).first()
            
            if not approved_request or approved_request.is_expired:
                messages.error(
                    request,
                    "Military clearance required to access military-grade autonomous systems."
                )
                return redirect('verification:request')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view









