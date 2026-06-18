"""
Security Middleware for ARES Platform.
Provides automatic clearance checking for protected paths.
"""
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.urls import resolve, Resolver404
import logging

logger = logging.getLogger(__name__)


class ClearanceRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that automatically enforces clearance requirements for specific URL patterns.
    
    Configure protected paths in settings.py:
    CLEARANCE_PROTECTED_PATHS = {
        '/military-robots/': 'military',
        '/classified/': 'top_secret',
        '/export-controlled/': 'secret',
    }
    """
    
    def process_request(self, request):
        """Process request before view is called."""
        try:
            # Skip for admin and static files
            if request.path.startswith('/admin/') or request.path.startswith('/static/') or request.path.startswith('/media/'):
                return None
            
            # Skip for unauthenticated users (handled by view decorators)
            if not request.user.is_authenticated:
                return None
            
            # Superusers and staff bypass all checks
            if request.user.is_superuser or request.user.is_staff:
                return None
            
            # Get protected paths from settings
            protected_paths = getattr(
                settings,
                'CLEARANCE_PROTECTED_PATHS',
                {}
            )
            
            # Check if current path requires clearance
            required_clearance = None
            for path_pattern, clearance_level in protected_paths.items():
                if request.path.startswith(path_pattern):
                    required_clearance = clearance_level
                    break
            
            if not required_clearance:
                return None
            
            # Check user clearance
            try:
                from .utils import get_user_clearance, has_clearance
                
                # Use has_clearance which handles priority checking internally
                if not has_clearance(request.user, required_clearance):
                    logger.warning(
                        f"User {request.user.username} attempted to access {request.path} "
                        f"without clearance (required: {required_clearance})"
                    )
                    messages.error(
                        request,
                        f"This area requires {required_clearance.upper()} clearance level."
                    )
                    # Redirect to verification request creation page
                    try:
                        return redirect('verification:request')
                    except Exception as redirect_error:
                        # Fallback to home if URL doesn't exist
                        logger.error(f"Redirect error: {str(redirect_error)}")
                        return redirect('home')
            except Exception as e:
                # If there's an error checking clearance, log it but don't block the request
                # This prevents middleware from breaking the entire application
                logger.error(f"Error checking clearance in middleware: {str(e)}")
                # Allow the request to proceed - view-level decorators will handle security
                pass
        except Exception as e:
            # Catch any other errors in the middleware
            logger.error(f"Unexpected error in ClearanceRequiredMiddleware: {str(e)}")
            # Don't block the request - let it proceed
            pass
        
        return None


class SecurityAuditMiddleware(MiddlewareMixin):
    """
    Middleware that logs security-relevant events for audit purposes.
    """
    
    def process_request(self, request):
        """Log security events."""
        try:
            # Log access to sensitive areas
            sensitive_paths = [
                '/military-robots/',
                '/verification/review/',
                '/analytics/',
                '/orders/purchase-requests/',
            ]
            
            if any(request.path.startswith(path) for path in sensitive_paths):
                if request.user.is_authenticated:
                    try:
                        from .models import VerificationLog
                        from .utils import get_user_clearance
                        
                        user_clearance = get_user_clearance(request.user)
                        clearance_name = user_clearance.name if user_clearance else 'None'
                        
                        logger.info(
                            f"Security Audit: User {request.user.username} "
                            f"(Clearance: {clearance_name}) accessed {request.path} "
                            f"from IP {request.META.get('REMOTE_ADDR')}"
                        )
                    except Exception as e:
                        # Don't break the application if logging fails
                        logger.error(f"Error in security audit logging: {str(e)}")
        except Exception as e:
            # Don't break the application if middleware fails
            logger.error(f"Error in SecurityAuditMiddleware: {str(e)}")
        
        return None
    
    def process_response(self, request, response):
        """Log security events in response."""
        # Log 403/401 responses for security analysis
        if response.status_code in [401, 403]:
            if request.user.is_authenticated:
                logger.warning(
                    f"Security Event: User {request.user.username} received "
                    f"{response.status_code} for {request.path} "
                    f"from IP {request.META.get('REMOTE_ADDR')}"
                )
        
        return response


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    Middleware for IP whitelisting (optional, for extra security).
    Configure in settings: CLEARANCE_IP_WHITELIST = ['192.168.1.0/24']
    """
    
    def process_request(self, request):
        """Check IP whitelist for sensitive areas."""
        # Only check for sensitive paths
        sensitive_paths = getattr(
            settings,
            'CLEARANCE_IP_WHITELIST_PATHS',
            ['/military-robots/', '/verification/review/']
        )
        
        if not any(request.path.startswith(path) for path in sensitive_paths):
            return None
        
        # Get whitelist from settings
        whitelist = getattr(settings, 'CLEARANCE_IP_WHITELIST', None)
        
        if not whitelist:
            return None
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Check if IP is whitelisted (simple check, can be enhanced with ipaddress module)
        if client_ip not in whitelist:
            logger.warning(
                f"IP {client_ip} attempted to access {request.path} but is not whitelisted"
            )
            messages.error(request, "Access denied: IP address not authorized.")
            return redirect('home')
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

