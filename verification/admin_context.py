"""
Admin context processor for verification notifications.
Provides pending counts for verification requests and licenses.
"""
from django.urls import reverse


def admin_notifications(request):
    """
    Context processor that adds pending verification and license counts to admin.
    Only runs for admin pages and authenticated staff users.
    """
    # Only process for admin pages and staff users
    if not request.path.startswith('/admin/') or not hasattr(request, 'user'):
        return {}
    
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}
    
    # Import here to avoid circular imports
    from verification.models import VerificationRequest, ExportLicense
    from orders.models import PurchaseRequest
    from support.models import SupportTicket
    
    # Get pending counts
    pending_verifications = VerificationRequest.objects.filter(
        status__in=['pending', 'under_review']
    ).count()
    
    pending_licenses = ExportLicense.objects.filter(
        status__in=['pending', 'under_review']
    ).count()
    
    pending_orders = PurchaseRequest.objects.filter(
        status='pending'
    ).count()
    
    pending_tickets = 0
    try:
        pending_tickets = SupportTicket.objects.filter(
            status__in=['open', 'in_progress']
        ).count()
    except:
        pass
    
    total_pending = pending_verifications + pending_licenses + pending_orders
    
    return {
        'admin_pending_verifications': pending_verifications,
        'admin_pending_licenses': pending_licenses,
        'admin_pending_orders': pending_orders,
        'admin_pending_tickets': pending_tickets,
        'admin_total_pending': total_pending,
        'admin_has_pending': total_pending > 0,
    }
