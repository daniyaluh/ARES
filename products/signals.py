"""
Signals for Products app to create notifications.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Product, Robot

User = get_user_model()


@receiver(post_save, sender=Product)
def notify_new_product(sender, instance, created, **kwargs):
    """Create notifications when a new product is added."""
    if created and instance.visibility and instance.status == 'published':
        from users.models import Notification
        
        # Notify users who have site_promotions enabled
        users = User.objects.filter(is_active=True)
        
        for user in users:
            # Check notification preferences
            try:
                prefs = user.notification_preferences
                if not prefs.site_promotions:
                    continue
            except:
                pass  # If no preferences, send notification
            
            Notification.objects.create(
                user=user,
                notification_type='product_added',
                title='New Product Available',
                message=f'A new product "{instance.title}" has been added to the marketplace.',
                product=instance
            )


@receiver(post_save, sender=Robot)
def notify_new_robot(sender, instance, created, **kwargs):
    """Create notifications when a new robot is added."""
    if created:
        from users.models import Notification
        
        # Notify all users about new robots
        users = User.objects.filter(is_active=True)
        
        for user in users:
            # Check if user has notification preferences
            try:
                prefs = user.notification_preferences
                if not prefs.site_promotions:
                    continue
            except:
                pass  # If no preferences, send notification
            
            Notification.objects.create(
                user=user,
                notification_type='robot_added',
                title='New Robot Added',
                message=f'A new robot "{instance.product.title}" ({instance.get_robot_type_display()}) has been added to the marketplace.',
                product=instance.product
            )

