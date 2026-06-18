"""
URL patterns for Orders app.
Comprehensive order management and transaction handling.
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Purchase Requests (Non-direct buy)
    path('purchase-requests/', views.purchase_request_list, name='purchase-request-list'),
    path('purchase-requests/create/', views.purchase_request_create, name='purchase-request-create'),
    path('purchase-requests/<uuid:request_id>/', views.purchase_request_detail, name='purchase-request-detail'),
    path('purchase-requests/<uuid:request_id>/edit/', views.purchase_request_update, name='purchase-request-edit'),
    path('purchase-requests/<uuid:request_id>/cancel/', views.purchase_request_cancel, name='purchase-request-cancel'),
    path('purchase-requests/<uuid:request_id>/approve/', views.purchase_request_approve, name='purchase-request-approve'),
    path('purchase-requests/<uuid:request_id>/reject/', views.purchase_request_reject, name='purchase-request-reject'),
    
    # Staff Purchase Request Management
    path('staff/pending-requests/', views.staff_pending_requests, name='staff-pending-requests'),
    path('staff/request-review/<uuid:request_id>/', views.staff_request_review, name='staff-request-review'),
    
    # Orders
    path('', views.order_list, name='order-list'),
    path('my-orders/', views.order_my_list, name='order-my-list'),
    path('create/', views.order_create, name='order-create'),
    path('<uuid:order_id>/', views.order_detail, name='order-detail'),
    path('<uuid:order_id>/edit/', views.order_update, name='order-edit'),
    path('<uuid:order_id>/cancel/', views.order_cancel, name='order-cancel'),
    path('<uuid:order_id>/complete/', views.order_complete, name='order-complete'),
    
    # Order Items
    path('<uuid:order_id>/items/', views.order_item_list, name='order-item-list'),
    path('<uuid:order_id>/items/add/', views.order_item_create, name='order-item-create'),
    path('items/<uuid:item_id>/', views.order_item_detail, name='order-item-detail'),
    path('items/<uuid:item_id>/edit/', views.order_item_update, name='order-item-edit'),
    path('items/<uuid:item_id>/delete/', views.order_item_delete, name='order-item-delete'),
    
    # Approval Chain
    path('<uuid:order_id>/approvals/', views.approval_chain_list, name='approval-chain-list'),
    path('<uuid:order_id>/approvals/create/', views.approval_chain_create, name='approval-chain-create'),
    path('approvals/<uuid:approval_id>/approve/', views.approval_chain_approve, name='approval-chain-approve'),
    path('approvals/<uuid:approval_id>/reject/', views.approval_chain_reject, name='approval-chain-reject'),
    
    # Transactions
    path('transactions/', views.transaction_list, name='transaction-list'),
    path('transactions/<uuid:transaction_id>/', views.transaction_detail, name='transaction-detail'),
    path('transactions/create/', views.transaction_create, name='transaction-create'),
    path('<uuid:order_id>/transactions/', views.order_transactions, name='order-transactions'),
    
    # Invoices (User)
    path('invoices/', views.invoice_list, name='invoice-list'),
    path('invoices/<uuid:invoice_id>/', views.invoice_detail, name='invoice-detail'),
    path('invoices/<uuid:invoice_id>/download/', views.invoice_download, name='invoice-download'),
    path('invoices/<uuid:invoice_id>/send/', views.invoice_send, name='invoice-send'),
    path('<uuid:order_id>/invoice/', views.order_invoice, name='order-invoice'),
    
    # Invoices (Staff)
    path('staff/invoices/', views.staff_invoice_list, name='staff-invoice-list'),
    path('staff/invoices/<uuid:invoice_id>/status/', views.staff_invoice_update_status, name='staff-invoice-update-status'),
    path('staff/invoices/generate-missing/', views.generate_missing_invoices, name='generate-missing-invoices'),
    path('staff/purchase-requests/<uuid:request_id>/generate-invoice/', views.generate_invoice_for_request, name='generate-invoice-for-request'),
    
    # Shipping
    path('<uuid:order_id>/shipping/', views.shipping_detail, name='shipping-detail'),
    path('<uuid:order_id>/shipping/edit/', views.shipping_update, name='shipping-update'),
    path('<uuid:order_id>/shipping/track/', views.shipping_track, name='shipping-track'),
    path('shipping/create/', views.shipping_create, name='shipping-create'),
    
    # Order Status History
    path('<uuid:order_id>/status-history/', views.order_status_history, name='order-status-history'),
    path('<uuid:order_id>/status/update/', views.order_status_update, name='order-status-update'),
    
    # Filter & Search
    path('filter/', views.order_filter, name='order-filter'),
    path('search/', views.order_search, name='order-search'),
    path('by-status/<str:status>/', views.order_by_status, name='order-by-status'),
    path('by-date/', views.order_by_date, name='order-by-date'),
    
    # Analytics & Reports
    path('analytics/', views.order_analytics, name='order-analytics'),
    path('reports/', views.order_reports, name='order-reports'),
    path('reports/sales/', views.order_sales_report, name='order-sales-report'),
    path('reports/export/', views.order_export, name='order-export'),
    
    # ===== FINANCE URLS =====
    
    # Admin/Staff Finance
    path('finance/admin/dashboard/', views.admin_finance_dashboard, name='admin-finance-dashboard'),
    path('finance/admin/revenue/', views.admin_platform_revenue_list, name='admin-revenue-list'),
    path('finance/admin/transactions/', views.admin_all_transactions, name='admin-all-transactions'),
    path('finance/admin/seller-earnings/', views.admin_seller_earnings_list, name='admin-seller-earnings'),
    path('finance/admin/payouts/', views.admin_payouts_list, name='admin-payouts-list'),
    path('finance/admin/payouts/<uuid:payout_id>/', views.admin_payout_detail, name='admin-payout-detail'),
    path('finance/admin/analytics/', views.admin_sales_analytics, name='admin-sales-analytics'),

    # Staff view specific accounts
    path('finance/staff/seller/<uuid:seller_id>/', views.staff_view_seller_finance, name='staff-view-seller-finance'),
    path('finance/staff/buyer/<uuid:user_id>/', views.staff_view_buyer_finance, name='staff-view-buyer-finance'),
    
    # Seller Finance
    path('finance/seller/dashboard/', views.seller_finance_dashboard, name='seller-finance-dashboard'),
    path('finance/seller/earnings/', views.seller_earnings_list, name='seller-earnings-list'),
    path('finance/seller/payouts/', views.seller_payouts_list, name='seller-payouts-list'),
    path('finance/seller/payouts/<uuid:payout_id>/', views.seller_payout_detail, name='seller-payout-detail'),
    
    # User Finance
    path('finance/user/payments/', views.user_payment_history, name='user-payment-history'),
    path('finance/user/wallet/', views.user_wallet, name='user-wallet'),
    path('finance/user/purchases/', views.user_purchased_products, name='user-purchased-products'),
]









