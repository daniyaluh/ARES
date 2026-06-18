"""
Mixins for class-based views with verification and clearance checks.
"""
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect
from .utils import can_access_robot, has_clearance, requires_verification, is_military_grade_robot


class VerificationRequiredMixin:
    """
    Mixin to require user verification for accessing a view.
    """
    def dispatch(self, request, *args, **kwargs):
        from .models import VerificationRequest
        
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('users:login')
        
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
        
        return super().dispatch(request, *args, **kwargs)


class ClearanceRequiredMixin:
    """
    Mixin to require a specific clearance level.
    
    Usage:
        class MyView(ClearanceRequiredMixin, ListView):
            required_clearance = 'secret'
    """
    required_clearance = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('users:login')
        
        if self.required_clearance and not has_clearance(request.user, self.required_clearance):
            messages.error(
                request,
                f"You do not have the required clearance level ({self.required_clearance}) to access this page."
            )
            raise PermissionDenied("Insufficient clearance level")
        
        return super().dispatch(request, *args, **kwargs)


class RobotAccessMixin:
    """
    Mixin to check if user can access a robot.
    Automatically checks access based on robot in the view context.
    """
    def dispatch(self, request, *args, **kwargs):
        from products.models import Robot, Product
        
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('users:login')
        
        # Get robot from URL kwargs
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
        
        if robot:
            # Check access
            can_access, reason = can_access_robot(request.user, robot)
            
            if not can_access:
                messages.error(request, reason)
                
                # If verification is required, redirect to verification request
                if requires_verification(robot):
                    return redirect('verification:request')
                
                raise PermissionDenied(reason)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add robot access info to context
        robot_id = self.kwargs.get('robot_id')
        product_id = self.kwargs.get('product_id')
        
        if robot_id:
            from products.models import Robot
            try:
                robot = Robot.objects.select_related('product', 'usage_restriction').get(id=robot_id)
                context['robot'] = robot
                context['can_access'] = True
            except Robot.DoesNotExist:
                pass
        
        elif product_id:
            from products.models import Product
            try:
                product = Product.objects.get(id=product_id)
                robot = getattr(product, 'robot', None)
                if robot:
                    context['robot'] = robot
                    context['can_access'] = True
            except Product.DoesNotExist:
                pass
        
        return context


class MilitaryClearanceMixin:
    """
    Mixin specifically for military-grade robot access.
    """
    def dispatch(self, request, *args, **kwargs):
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
        
        return super().dispatch(request, *args, **kwargs)


class FilterRestrictedProductsMixin:
    """
    Mixin to filter out restricted products from queryset based on user clearance.
    Works with Robot queryset (not Product).
    """
    def get_queryset(self):
        from products.models import Robot
        # Get base queryset from parent or create new one
        if hasattr(super(), 'get_queryset'):
            queryset = super().get_queryset()
        else:
            queryset = Robot.objects.all()
        
        # Only show robots with active products (filter out paused, discontinued, etc.)
        queryset = queryset.filter(product__status='active')
        
        if not self.request.user.is_authenticated:
            # Non-authenticated users can only see non-restricted robots
            return queryset.filter(
                requires_verification=False,
                is_restricted=False
            )
        
        # Superusers see everything
        if self.request.user.is_superuser:
            return queryset
        
        # Get user clearance
        from .utils import get_user_clearance
        user_clearance = get_user_clearance(self.request.user)
        
        # Filter based on clearance level
        if not user_clearance:
            # No clearance - only show non-restricted robots
            return queryset.filter(
                requires_verification=False,
                is_restricted=False
            )
        
        # Users with clearance can see restricted products
        if user_clearance.can_access_restricted:
            # Still filter out military-only if they don't have military clearance
            if not user_clearance.can_access_military:
                return queryset.exclude(
                    usage_restriction__restriction_level='military_only'
                )
            return queryset
        
        # No restricted access - filter out all restricted
        return queryset.filter(
            requires_verification=False,
            is_restricted=False
        )

