"""
URL patterns for Analytics app.
Comprehensive analytics dashboards and reporting.
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.analytics_dashboard, name='analytics-dashboard'),
    path('dashboard/overview/', views.analytics_overview, name='analytics-overview'),
    path('dashboard/realtime/', views.analytics_realtime, name='analytics-realtime'),
    
    # System Health
    path('system-health/', views.system_health_list, name='system-health-list'),
    path('system-health/<uuid:log_id>/', views.system_health_detail, name='system-health-detail'),
    path('system-health/latest/', views.system_health_latest, name='system-health-latest'),
    path('system-health/alerts/', views.system_health_alerts, name='system-health-alerts'),
    
    # Sales Metrics
    path('sales/', views.sales_metric_list, name='sales-metric-list'),
    path('sales/metrics/', views.sales_metrics_dashboard, name='sales-metrics-dashboard'),
    path('sales/revenue/', views.sales_revenue_analytics, name='sales-revenue-analytics'),
    path('sales/products/', views.sales_product_analytics, name='sales-product-analytics'),
    path('sales/sellers/', views.sales_seller_analytics, name='sales-seller-analytics'),
    path('sales/export/', views.sales_export, name='sales-export'),
    
    # User Activity
    path('user-activity/', views.user_activity_log_list, name='user-activity-log-list'),
    path('user-activity/<uuid:log_id>/', views.user_activity_log_detail, name='user-activity-log-detail'),
    path('user-activity/user/<uuid:user_id>/', views.user_activity_by_user, name='user-activity-by-user'),
    path('user-activity/by-type/<str:activity_type>/', views.user_activity_by_type, name='user-activity-by-type'),
    path('user-activity/recent/', views.user_activity_recent, name='user-activity-recent'),
    
    # Inventory
    path('inventory/', views.inventory_snapshot_list, name='inventory-snapshot-list'),
    path('inventory/<uuid:snapshot_id>/', views.inventory_snapshot_detail, name='inventory-snapshot-detail'),
    path('inventory/latest/', views.inventory_snapshot_latest, name='inventory-snapshot-latest'),
    path('inventory/products/', views.inventory_product_analytics, name='inventory-product-analytics'),
    path('inventory/low-stock/', views.inventory_low_stock, name='inventory-low-stock'),
    
    # Market Trends
    path('market-trends/', views.market_trend_list, name='market-trend-list'),
    path('market-trends/<uuid:trend_id>/', views.market_trend_detail, name='market-trend-detail'),
    path('market-trends/current/', views.market_trend_current, name='market-trend-current'),
    path('market-trends/analysis/', views.market_trend_analysis, name='market-trend-analysis'),
    path('market-trends/by-category/<uuid:category_id>/', views.market_trend_by_category, name='market-trend-by-category'),
    
    # Platform Configuration (Analytics)
    path('config/', views.platform_config_list, name='platform-config-list'),
    path('config/<uuid:config_id>/', views.platform_config_detail, name='platform-config-detail'),
    path('config/<uuid:config_id>/edit/', views.platform_config_update, name='platform-config-update'),
    
    # Reports & Exports
    path('reports/', views.analytics_reports, name='analytics-reports'),
    path('reports/generate/', views.analytics_report_generate, name='analytics-report-generate'),
    path('reports/<uuid:report_id>/download/', views.analytics_report_download, name='analytics-report-download'),
    path('export/', views.analytics_export, name='analytics-export'),
]









