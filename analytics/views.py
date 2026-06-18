"""
Views for Analytics app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import (
    SystemHealthLog, SalesMetric, UserActivityLog,
    InventorySnapshot, MarketTrend, PlatformConfig
)


# Dashboard
@login_required
def analytics_dashboard(request):
    """Analytics dashboard."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'analytics/analytics_dashboard.html')


@login_required
def analytics_overview(request):
    """Analytics overview."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'analytics/analytics_overview.html')


@login_required
def analytics_realtime(request):
    """Realtime analytics."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'analytics/analytics_realtime.html')


# System Health
@login_required
def system_health_list(request):
    """List system health logs."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    logs = SystemHealthLog.objects.all().order_by('-created_at')[:100]
    return render(request, 'analytics/system_health_list.html', {'logs': logs})


def system_health_detail(request, log_id):
    """System health log detail."""
    log = get_object_or_404(SystemHealthLog, id=log_id)
    return render(request, 'analytics/system_health_detail.html', {'log': log})


@login_required
def system_health_latest(request):
    """Latest system health."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    latest = SystemHealthLog.objects.first()
    return render(request, 'analytics/system_health_latest.html', {'latest': latest})


@login_required
def system_health_alerts(request):
    """System health alerts."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    alerts = SystemHealthLog.objects.filter(severity__in=['critical', 'warning'])
    return render(request, 'analytics/system_health_alerts.html', {'alerts': alerts})


# Sales Metrics
@login_required
def sales_metric_list(request):
    """List sales metrics."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    metrics = SalesMetric.objects.all().order_by('-created_at')[:100]
    return render(request, 'analytics/sales_metric_list.html', {'metrics': metrics})


@login_required
def sales_metrics_dashboard(request):
    """Sales metrics dashboard."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'analytics/sales_metrics_dashboard.html')


@login_required
def sales_revenue_analytics(request):
    """Sales revenue analytics."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'analytics/sales_revenue_analytics.html')


@login_required
def sales_product_analytics(request):
    """Product sales analytics."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'analytics/sales_product_analytics.html')


@login_required
def sales_seller_analytics(request):
    """Seller analytics."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'analytics/sales_seller_analytics.html')


@login_required
def sales_export(request):
    """Export sales data."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    messages.info(request, "Export functionality coming soon.")
    return redirect('analytics:sales-metrics-dashboard')


# User Activity
@login_required
def user_activity_log_list(request):
    """List user activity logs."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    logs = UserActivityLog.objects.all().order_by('-created_at')[:200]
    return render(request, 'analytics/user_activity_log_list.html', {'logs': logs})


def user_activity_log_detail(request, log_id):
    """User activity log detail."""
    log = get_object_or_404(UserActivityLog, id=log_id)
    return render(request, 'analytics/user_activity_log_detail.html', {'log': log})


@login_required
def user_activity_by_user(request, user_id):
    """User activity by user."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user_obj = get_object_or_404(User, id=user_id)
    logs = UserActivityLog.objects.filter(user=user_obj)
    return render(request, 'analytics/user_activity_by_user.html', {'user_obj': user_obj, 'logs': logs})


@login_required
def user_activity_by_type(request, activity_type):
    """User activity by type."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    logs = UserActivityLog.objects.filter(activity_type=activity_type)
    return render(request, 'analytics/user_activity_by_type.html', {'logs': logs, 'activity_type': activity_type})


@login_required
def user_activity_recent(request):
    """Recent user activity."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    logs = UserActivityLog.objects.all().order_by('-created_at')[:50]
    return render(request, 'analytics/user_activity_recent.html', {'logs': logs})


# Inventory
@login_required
def inventory_snapshot_list(request):
    """List inventory snapshots."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    snapshots = InventorySnapshot.objects.all().order_by('-created_at')[:100]
    return render(request, 'analytics/inventory_snapshot_list.html', {'snapshots': snapshots})


def inventory_snapshot_detail(request, snapshot_id):
    """Inventory snapshot detail."""
    snapshot = get_object_or_404(InventorySnapshot, id=snapshot_id)
    return render(request, 'analytics/inventory_snapshot_detail.html', {'snapshot': snapshot})


@login_required
def inventory_snapshot_latest(request):
    """Latest inventory snapshot."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    latest = InventorySnapshot.objects.first()
    return render(request, 'analytics/inventory_snapshot_latest.html', {'latest': latest})


@login_required
def inventory_product_analytics(request):
    """Product inventory analytics."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'analytics/inventory_product_analytics.html')


@login_required
def inventory_low_stock(request):
    """Low stock inventory."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'analytics/inventory_low_stock.html')


# Market Trends
@login_required
def market_trend_list(request):
    """List market trends."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    trends = MarketTrend.objects.all().order_by('-created_at')
    return render(request, 'analytics/market_trend_list.html', {'trends': trends})


def market_trend_detail(request, trend_id):
    """Market trend detail."""
    trend = get_object_or_404(MarketTrend, id=trend_id)
    return render(request, 'analytics/market_trend_detail.html', {'trend': trend})


@login_required
def market_trend_current(request):
    """Current market trends."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    current = MarketTrend.objects.first()
    return render(request, 'analytics/market_trend_current.html', {'current': current})


@login_required
def market_trend_analysis(request):
    """Market trend analysis."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'analytics/market_trend_analysis.html')


def market_trend_by_category(request, category_id):
    """Market trends by category."""
    trends = MarketTrend.objects.filter(category_id=category_id)
    return render(request, 'analytics/market_trend_by_category.html', {'trends': trends})


# Platform Configuration
@login_required
def platform_config_list(request):
    """List platform configs."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    configs = PlatformConfig.objects.all()
    return render(request, 'analytics/platform_config_list.html', {'configs': configs})


def platform_config_detail(request, config_id):
    """Platform config detail."""
    config = get_object_or_404(PlatformConfig, id=config_id)
    return render(request, 'analytics/platform_config_detail.html', {'config': config})


@login_required
def platform_config_update(request, config_id):
    """Update platform config."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    config = get_object_or_404(PlatformConfig, id=config_id)
    
    if request.method == 'POST':
        config.value = request.POST.get('value', config.value)
        config.save()
        messages.success(request, "Config updated.")
        return redirect('analytics:platform-config-detail', config_id=config_id)
    
    return render(request, 'analytics/platform_config_edit.html', {'config': config})


# Reports & Exports
@login_required
def analytics_reports(request):
    """Analytics reports."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'analytics/analytics_reports.html')


@login_required
def analytics_report_generate(request):
    """Generate analytics report."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    messages.info(request, "Report generation coming soon.")
    return redirect('analytics:analytics-reports')


@login_required
def analytics_report_download(request, report_id):
    """Download analytics report."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    messages.info(request, "Report download coming soon.")
    return redirect('analytics:analytics-reports')


@login_required
def analytics_export(request):
    """Export analytics data."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    messages.info(request, "Export functionality coming soon.")
    return redirect('analytics:analytics-reports')
