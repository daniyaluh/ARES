"""
Signals for Verification app to create notifications.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VerificationRequest


@receiver(post_save, sender=VerificationRequest)
def notify_verification_status_change(sender, instance, created, **kwargs):
    """Create notifications when verification status changes."""
    from users.models import Notification
    
    # Skip on creation (user just submitted, they know)
    if created:
        return
    
    # Check if status actually changed using _original_status set by approve/reject methods
    if hasattr(instance, '_original_status'):
        old_status = instance._original_status
        if old_status == instance.status:
            return  # No status change
    else:
        # If we can't determine change, only notify for approved/rejected
        if instance.status not in ['approved', 'rejected']:
            return
    
    # Check user notification preferences
    try:
        prefs = instance.user.notification_preferences
        if not prefs.site_verification_updates:
            return
    except:
        pass  # If no preferences, send notification
    
    if instance.status == 'approved':
        Notification.objects.create(
            user=instance.user,
            notification_type='verification_approved',
            title='Verification Approved',
            message=f'Your verification request has been approved. You now have {instance.current_clearance.name if instance.current_clearance else "clearance"} clearance.',
            verification_request=instance
        )
    elif instance.status == 'rejected':
        Notification.objects.create(
            user=instance.user,
            notification_type='verification_rejected',
            title='Verification Rejected',
            message=f'Your verification request has been rejected. Reason: {instance.rejection_reason[:100] if instance.rejection_reason else "See details for more information."}',
            verification_request=instance
        )
    elif instance.status in ['expired', 'revoked']:
        Notification.objects.create(
            user=instance.user,
            notification_type='verification_updated',
            title='Verification Status Updated',
            message=f'Your verification request status has been updated to: {instance.get_status_display()}',
            verification_request=instance
        )

