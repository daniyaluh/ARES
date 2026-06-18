from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PurchaseRequest, PurchaseRequestLog, Order, OrderItem, ApprovalChain,
    Transaction, Invoice, InvoiceItem, ShippingDetail, OrderStatusHistory,
    PlatformRevenue, SellerEarnings, SellerPayout, WalletTransaction
)


class PurchaseRequestLogInline(admin.TabularInline):
    model = PurchaseRequestLog
    extra = 0
    readonly_fields = ['id', 'action', 'performed_by', 'details', 'created_at']
    can_delete = False
    ordering = ['-created_at']


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'status', 'urgency', 'purpose', 'created_at', 'has_invoice']
    list_filter = ['status', 'urgency', 'purpose', 'created_at']
    search_fields = ['user__username', 'user__email', 'product__title', 'company_name', 'notes']
    readonly_fields = ['id', 'created_at', 'updated_at', 'reviewed_at']
    raw_id_fields = ['user', 'product', 'reviewed_by']
    ordering = ['-created_at']
    inlines = [PurchaseRequestLogInline]
    
    fieldsets = (
        ('Request Info', {
            'fields': ('id', 'user', 'product', 'quantity', 'status')
        }),
        ('Buyer Information', {
            'fields': ('company_name', 'contact_name', 'contact_phone', 'contact_email'),
            'classes': ('collapse',)
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'),
            'classes': ('collapse',)
        }),
        ('Request Details', {
            'fields': ('purpose', 'intended_use', 'urgency', 'notes', 'supporting_documents')
        }),
        ('Review', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_approved', 'mark_rejected', 'mark_under_review']
    
    def has_invoice(self, obj):
        """Check if this request has an invoice."""
        has_inv = hasattr(obj, 'invoice') and obj.invoice is not None
        if has_inv:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: gray;">-</span>')
    has_invoice.short_description = 'Invoice'
    
    def mark_approved(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} request(s) marked as approved.")
    mark_approved.short_description = "Mark selected as Approved"
    
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} request(s) marked as rejected.")
    mark_rejected.short_description = "Mark selected as Rejected"
    
    def mark_under_review(self, request, queryset):
        queryset.update(status='under_review')
        self.message_user(request, f"{queryset.count()} request(s) marked as under review.")
    mark_under_review.short_description = "Mark selected as Under Review"


@admin.register(PurchaseRequestLog)
class PurchaseRequestLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'purchase_request', 'action', 'performed_by', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['purchase_request__id', 'performed_by__username', 'details']
    readonly_fields = ['id', 'purchase_request', 'action', 'performed_by', 'details', 'created_at']
    ordering = ['-created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'quantity', 'price', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at']


@admin.register(ApprovalChain)
class ApprovalChainAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['id', 'created_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'transaction_type', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    readonly_fields = ['id', 'created_at']


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ['id', 'line_total', 'created_at']
    fields = ['product', 'description', 'quantity', 'unit_price', 'discount', 'line_total']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer_name', 'status', 'total_amount', 'currency', 'issue_date', 'due_date', 'is_overdue']
    list_filter = ['status', 'currency', 'issue_date', 'created_at']
    search_fields = ['invoice_number', 'customer_name', 'customer_email', 'customer_company']
    readonly_fields = ['id', 'invoice_number', 'created_at', 'updated_at', 'sent_at', 'paid_at']
    raw_id_fields = ['order', 'purchase_request', 'created_by']
    ordering = ['-created_at']
    inlines = [InvoiceItemInline]
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Invoice Info', {
            'fields': ('id', 'invoice_number', 'status')
        }),
        ('Related Records', {
            'fields': ('order', 'purchase_request', 'created_by')
        }),
        ('Customer', {
            'fields': ('customer_name', 'customer_email', 'customer_company', 'customer_phone')
        }),
        ('Billing Address', {
            'fields': ('billing_address', 'billing_city', 'billing_state', 'billing_postal_code', 'billing_country'),
            'classes': ('collapse',)
        }),
        ('Financials', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'shipping_cost', 'total_amount', 'currency')
        }),
        ('Payment', {
            'fields': ('issue_date', 'due_date', 'payment_terms')
        }),
        ('Documents', {
            'fields': ('pdf_file',)
        }),
        ('Notes', {
            'fields': ('notes', 'internal_notes'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('sent_at', 'paid_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_issued', 'mark_sent', 'mark_paid', 'mark_cancelled']
    
    def is_overdue(self, obj):
        """Check if invoice is overdue."""
        from django.utils import timezone
        if obj.status in ['paid', 'cancelled']:
            return format_html('<span style="color: gray;">-</span>')
        if obj.due_date and obj.due_date < timezone.now().date():
            return format_html('<span style="color: red; font-weight: bold;">OVERDUE</span>')
        return format_html('<span style="color: green;">OK</span>')
    is_overdue.short_description = 'Payment Status'
    
    def mark_issued(self, request, queryset):
        queryset.update(status='issued')
        self.message_user(request, f"{queryset.count()} invoice(s) marked as issued.")
    mark_issued.short_description = "Mark as Issued"
    
    def mark_sent(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='sent', sent_at=timezone.now())
        self.message_user(request, f"{queryset.count()} invoice(s) marked as sent.")
    mark_sent.short_description = "Mark as Sent"
    
    def mark_paid(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='paid', paid_at=timezone.now())
        self.message_user(request, f"{queryset.count()} invoice(s) marked as paid.")
    mark_paid.short_description = "Mark as Paid"
    
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} invoice(s) cancelled.")
    mark_cancelled.short_description = "Cancel Invoice"


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'description', 'quantity', 'unit_price', 'line_total']
    list_filter = ['created_at']
    search_fields = ['description', 'invoice__invoice_number']
    readonly_fields = ['id', 'line_total', 'created_at']
    raw_id_fields = ['invoice', 'product']


@admin.register(ShippingDetail)
class ShippingDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'tracking_number', 'carrier', 'created_at']
    search_fields = ['tracking_number']
    readonly_fields = ['id', 'created_at']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'status', 'updated_by', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['id', 'created_at']


# ============================================================================
# FINANCIAL ADMIN REGISTRATIONS
# ============================================================================

@admin.register(PlatformRevenue)
class PlatformRevenueAdmin(admin.ModelAdmin):
    """Admin for platform revenue records."""
    list_display = ['revenue_date', 'revenue_type', 'seller_link', 'gross_amount', 'commission_rate', 'commission_amount', 'currency']
    list_filter = ['revenue_type', 'revenue_date', 'currency']
    search_fields = ['seller__username', 'description', 'notes']
    readonly_fields = ['id', 'commission_amount', 'created_at', 'updated_at']
    raw_id_fields = ['order', 'transaction', 'seller']
    ordering = ['-revenue_date']
    date_hierarchy = 'revenue_date'
    
    fieldsets = (
        ('Revenue Info', {
            'fields': ('id', 'revenue_type', 'revenue_date')
        }),
        ('Related Records', {
            'fields': ('order', 'transaction', 'seller')
        }),
        ('Financial Details', {
            'fields': ('gross_amount', 'commission_rate', 'commission_amount', 'currency')
        }),
        ('Description', {
            'fields': ('description', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def seller_link(self, obj):
        """Display seller as clickable link."""
        if obj.seller:
            return format_html('<a href="/admin/users/customuser/{}/change/">{}</a>', 
                             obj.seller.id, obj.seller.username)
        return '-'
    seller_link.short_description = 'Seller'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('seller', 'order', 'transaction')


class SellerEarningsInline(admin.TabularInline):
    """Inline for seller earnings in payout admin."""
    model = SellerEarnings
    fk_name = 'payout'
    extra = 0
    readonly_fields = ['seller', 'order', 'product', 'gross_sale_amount', 'platform_commission', 'net_earnings', 'earned_date']
    can_delete = False
    fields = ['product', 'gross_sale_amount', 'platform_commission', 'net_earnings', 'earned_date']


@admin.register(SellerEarnings)
class SellerEarningsAdmin(admin.ModelAdmin):
    """Admin for seller earnings records."""
    list_display = ['earned_date', 'seller_link', 'product_title', 'gross_sale_amount', 'platform_commission', 'net_earnings', 'status', 'is_paid_out']
    list_filter = ['status', 'is_paid_out', 'earned_date', 'currency']
    search_fields = ['seller__username', 'product__title', 'notes']
    readonly_fields = ['id', 'net_earnings', 'created_at', 'updated_at', 'paid_out_date']
    raw_id_fields = ['seller', 'order', 'product', 'transaction', 'payout']
    ordering = ['-earned_date']
    date_hierarchy = 'earned_date'
    
    fieldsets = (
        ('Earning Info', {
            'fields': ('id', 'seller', 'earned_date', 'status')
        }),
        ('Sale Details', {
            'fields': ('order', 'product', 'transaction')
        }),
        ('Financial Breakdown', {
            'fields': ('gross_sale_amount', 'platform_commission', 'net_earnings', 'currency')
        }),
        ('Payout Status', {
            'fields': ('is_paid_out', 'paid_out_date', 'payout')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'mark_on_hold']
    
    def seller_link(self, obj):
        """Display seller as clickable link."""
        if obj.seller:
            return format_html('<a href="/admin/users/customuser/{}/change/">{}</a>', 
                             obj.seller.id, obj.seller.username)
        return '-'
    seller_link.short_description = 'Seller'
    
    def product_title(self, obj):
        """Display product title."""
        return obj.product.title if obj.product else '-'
    product_title.short_description = 'Product'
    
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} earning(s) marked as completed.")
    mark_completed.short_description = "Mark as Completed"
    
    def mark_on_hold(self, request, queryset):
        queryset.update(status='on_hold')
        self.message_user(request, f"{queryset.count()} earning(s) put on hold.")
    mark_on_hold.short_description = "Put on Hold"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('seller', 'order', 'product', 'payout')


@admin.register(SellerPayout)
class SellerPayoutAdmin(admin.ModelAdmin):
    """Admin for seller payout records."""
    list_display = ['payout_number', 'seller_link', 'total_amount', 'earnings_count', 'payment_method', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'payment_method', 'created_at', 'processed_at']
    search_fields = ['payout_number', 'seller__username', 'payment_reference', 'notes']
    readonly_fields = ['id', 'payout_number', 'earnings_count', 'created_at', 'updated_at']
    raw_id_fields = ['seller', 'processed_by']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    inlines = [SellerEarningsInline]
    
    fieldsets = (
        ('Payout Info', {
            'fields': ('id', 'payout_number', 'seller', 'status')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'currency', 'earnings_count')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_reference', 'recipient_details')
        }),
        ('Processing', {
            'fields': ('processed_by', 'processed_at', 'failure_reason')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'mark_failed', 'mark_processing']
    
    def seller_link(self, obj):
        """Display seller as clickable link."""
        if obj.seller:
            return format_html('<a href="/admin/users/customuser/{}/change/">{}</a>', 
                             obj.seller.id, obj.seller.username)
        return '-'
    seller_link.short_description = 'Seller'
    
    def mark_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='completed', processed_at=timezone.now())
        # Also mark related earnings as paid
        for payout in queryset:
            payout.earnings.update(is_paid_out=True, paid_out_date=timezone.now())
        self.message_user(request, f"{queryset.count()} payout(s) marked as completed.")
    mark_completed.short_description = "Mark as Completed"
    
    def mark_failed(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f"{queryset.count()} payout(s) marked as failed.")
    mark_failed.short_description = "Mark as Failed"
    
    def mark_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, f"{queryset.count()} payout(s) marked as processing.")
    mark_processing.short_description = "Mark as Processing"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('seller', 'processed_by').prefetch_related('earnings')


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    """Admin for wallet transactions."""
    list_display = ['transaction_date', 'user_link', 'transaction_type', 'amount', 'balance_after', 'status', 'description']
    list_filter = ['transaction_type', 'status', 'transaction_date', 'currency']
    search_fields = ['user__username', 'description', 'payment_reference', 'notes']
    readonly_fields = ['id', 'balance_before', 'balance_after', 'created_at', 'updated_at']
    raw_id_fields = ['user', 'order', 'seller_earning', 'payout', 'processed_by']
    ordering = ['-transaction_date']
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('id', 'user', 'transaction_type', 'transaction_date', 'status')
        }),
        ('Amount Details', {
            'fields': ('amount', 'currency', 'balance_before', 'balance_after')
        }),
        ('Related Records', {
            'fields': ('order', 'seller_earning', 'payout'),
            'classes': ('collapse',)
        }),
        ('Payment Reference', {
            'fields': ('payment_reference',)
        }),
        ('Description', {
            'fields': ('description', 'notes'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('processed_by',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'mark_failed', 'mark_cancelled']
    
    def user_link(self, obj):
        """Display user as clickable link."""
        if obj.user:
            return format_html('<a href="/admin/users/customuser/{}/change/">{}</a>', 
                             obj.user.id, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} transaction(s) marked as completed.")
    mark_completed.short_description = "Mark as Completed"
    
    def mark_failed(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f"{queryset.count()} transaction(s) marked as failed.")
    mark_failed.short_description = "Mark as Failed"
    
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} transaction(s) cancelled.")
    mark_cancelled.short_description = "Cancel Transaction"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'order', 'processed_by')
