"""
Models for Analytics app.
"""
from django.db import models
from django.conf import settings
import uuid


class SystemHealthLog(models.Model):
    """System health log model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    severity = models.CharField(max_length=20, default='info')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class SalesMetric(models.Model):
    """Sales metric model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_type = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


class UserActivityLog(models.Model):
    """User activity log model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InventorySnapshot(models.Model):
    """Inventory snapshot model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    snapshot_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class MarketTrend(models.Model):
    """Market trend model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_id = models.UUIDField(null=True, blank=True)
    trend_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class PlatformConfig(models.Model):
    """Platform configuration model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
