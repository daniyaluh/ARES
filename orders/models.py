"""
Models for Orders app.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
import logging

# Create logger for purchase request actions
purchase_request_logger = logging.getLogger('purchase_requests')


class PurchaseRequest(models.Model):
    """Purchase request model with comprehensive information collection."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    URGENCY_CHOICES = [
        ('low', 'Low - Within 30 days'),
        ('normal', 'Normal - Within 14 days'),
        ('high', 'High - Within 7 days'),
        ('urgent', 'Urgent - ASAP'),
    ]
    
    PURPOSE_CHOICES = [
        ('commercial', 'Commercial Use'),
        ('research', 'Research & Development'),
        ('government', 'Government/Military'),
        ('education', 'Educational'),
        ('personal', 'Personal Use'),
        ('other', 'Other'),
    ]
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchase_requests')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='purchase_requests', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Buyer Information
    company_name = models.CharField(max_length=255, blank=True, help_text="Company or organization name")
    contact_name = models.CharField(max_length=255, blank=True, help_text="Primary contact person")
    contact_phone = models.CharField(max_length=50, blank=True, help_text="Contact phone number")
    contact_email = models.EmailField(blank=True, help_text="Contact email (if different from account)")
    
    # Shipping Information
    shipping_address = models.TextField(blank=True, help_text="Full shipping address")
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=100, blank=True)
    
    # Request Details
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='commercial')
    intended_use = models.TextField(blank=True, help_text="Detailed description of intended use")
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='normal')
    notes = models.TextField(blank=True, help_text="Additional notes or requirements")
    
    # Document uploads
    supporting_documents = models.FileField(upload_to='purchase_requests/documents/', blank=True, null=True)
    
    # Review fields
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_purchase_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, help_text="Admin/staff review notes")
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection if rejected")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_purchase_request'
        verbose_name = 'purchase request'
        verbose_name_plural = 'purchase requests'
        ordering = ['-created_at']
    
    def __str__(self):
        product_title = self.product.title if self.product else "No Product"
        return f"Purchase Request for {product_title} by {self.user.username}"
    
    def log_action(self, action, user=None, details=""):
        """Log an action on this purchase request."""
        log_entry = PurchaseRequestLog.objects.create(
            purchase_request=self,
            action=action,
            performed_by=user,
            details=details
        )
        # Also log to file
        purchase_request_logger.info(
            f"[{self.id}] Action: {action} | User: {user.username if user else 'System'} | "
            f"Product: {self.product.title if self.product else 'N/A'} | Details: {details}"
        )
        return log_entry


class PurchaseRequestLog(models.Model):
    """Log model for tracking all purchase request actions."""
    ACTION_CHOICES = [
        ('created', 'Request Created'),
        ('updated', 'Request Updated'),
        ('submitted', 'Request Submitted'),
        ('under_review', 'Marked Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('note_added', 'Note Added'),
        ('document_uploaded', 'Document Uploaded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_request = models.ForeignKey(
        PurchaseRequest, 
        on_delete=models.CASCADE, 
        related_name='logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orders_purchase_request_log'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.purchase_request.id}"


class Order(models.Model):
    """Order model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    """Order item model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    license_key = models.CharField(max_length=255, blank=True, null=True)  # For digital products
    created_at = models.DateTimeField(auto_now_add=True)


class ApprovalChain(models.Model):
    """Approval chain model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    """Transaction model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)


class Invoice(models.Model):
    """Invoice model with comprehensive invoice details."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Links - can be associated with Order or PurchaseRequest
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice', null=True, blank=True)
    purchase_request = models.OneToOneField(PurchaseRequest, on_delete=models.CASCADE, related_name='invoice', null=True, blank=True)
    
    # Invoice Identification
    invoice_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Customer Information (copied from request for invoice permanence)
    customer_name = models.CharField(max_length=255, default='')
    customer_email = models.EmailField(default='')
    customer_company = models.CharField(max_length=255, blank=True, default='')
    customer_phone = models.CharField(max_length=50, blank=True, default='')
    
    # Billing Address
    billing_address = models.TextField(blank=True, default='')
    billing_city = models.CharField(max_length=100, blank=True, default='')
    billing_state = models.CharField(max_length=100, blank=True, default='')
    billing_postal_code = models.CharField(max_length=20, blank=True, default='')
    billing_country = models.CharField(max_length=100, blank=True, default='')
    
    # Financial Details
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    
    # Payment Terms
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    payment_terms = models.CharField(max_length=100, default='Net 30')
    
    # PDF Storage
    pdf_file = models.FileField(upload_to='invoices/pdf/', null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, default='', help_text="Notes visible on invoice")
    internal_notes = models.TextField(blank=True, default='', help_text="Internal notes - not shown on invoice")
    
    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_invoices'
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_invoice'
        verbose_name = 'invoice'
        verbose_name_plural = 'invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    @classmethod
    def generate_invoice_number(cls):
        """Generate a unique invoice number."""
        from django.utils import timezone
        import random
        prefix = "INV"
        date_part = timezone.now().strftime("%Y%m%d")
        random_part = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        invoice_number = f"{prefix}-{date_part}-{random_part}"
        
        # Ensure uniqueness
        while cls.objects.filter(invoice_number=invoice_number).exists():
            random_part = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            invoice_number = f"{prefix}-{date_part}-{random_part}"
        
        return invoice_number
    
    def calculate_totals(self):
        """Calculate tax and total from subtotal."""
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
        return self.total_amount


class InvoiceItem(models.Model):
    """Individual line items on an invoice."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    
    # Product Reference
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice_items'
    )
    
    # Line Item Details
    description = models.CharField(max_length=500)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Metadata
    sku = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orders_invoice_item'
        verbose_name = 'invoice item'
        verbose_name_plural = 'invoice items'
    
    def __str__(self):
        return f"{self.description} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate line total before saving."""
        self.line_total = (self.unit_price * self.quantity) - self.discount
        super().save(*args, **kwargs)


class ShippingDetail(models.Model):
    """Shipping detail model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping')
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderStatusHistory(models.Model):
    """Order status history model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# ============================================================================
# FINANCIAL MODELS - Revenue Tracking & Payment Management
# ============================================================================

class PlatformRevenue(models.Model):
    """
    Track platform revenue from commissions on sales.
    Central record for all money earned by the platform.
    """
    
    REVENUE_TYPE_CHOICES = [
        ('commission', 'Sales Commission'),
        ('listing_fee', 'Listing Fee'),
        ('premium_feature', 'Premium Feature'),
        ('subscription', 'Subscription Fee'),
        ('other', 'Other Revenue'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Links to related records
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='platform_revenues',
        null=True,
        blank=True,
        help_text="Related order if revenue comes from a sale"
    )
    transaction = models.ForeignKey(
        'Transaction',
        on_delete=models.SET_NULL,
        related_name='platform_revenues',
        null=True,
        blank=True,
        help_text="Related transaction record"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='platform_revenues_from',
        null=True,
        blank=True,
        help_text="Seller from whose sale this commission was generated"
    )
    
    # Revenue Details
    revenue_type = models.CharField(
        max_length=30,
        choices=REVENUE_TYPE_CHOICES,
        default='commission'
    )
    gross_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total sale amount before commission"
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        help_text="Commission percentage (e.g., 10.00 for 10%)"
    )
    commission_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Platform commission earned"
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Metadata
    description = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    revenue_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_platform_revenue'
        verbose_name = 'platform revenue'
        verbose_name_plural = 'platform revenues'
        ordering = ['-revenue_date']
        indexes = [
            models.Index(fields=['revenue_type', '-revenue_date']),
            models.Index(fields=['seller', '-revenue_date']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"Platform Revenue: {self.commission_amount} {self.currency} ({self.revenue_type})"
    
    def save(self, *args, **kwargs):
        """Calculate commission amount if not provided."""
        if not self.commission_amount and self.gross_amount and self.commission_rate:
            self.commission_amount = (self.gross_amount * self.commission_rate) / 100
        super().save(*args, **kwargs)


class SellerEarnings(models.Model):
    """
    Track individual seller earnings from each sale.
    Represents money owed to or earned by sellers.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Seller & Sale Information
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='earnings',
        help_text="Seller who earned this amount"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='seller_earnings',
        help_text="Order that generated this earning"
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='seller_earnings',
        help_text="Product sold"
    )
    transaction = models.ForeignKey(
        'Transaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='seller_earnings'
    )
    
    # Earnings Breakdown
    gross_sale_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total sale amount before deductions"
    )
    platform_commission = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Platform commission deducted"
    )
    net_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount seller receives (gross - commission)"
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Status & Payment
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    is_paid_out = models.BooleanField(
        default=False,
        help_text="Whether this earning has been paid to seller"
    )
    payout = models.ForeignKey(
        'SellerPayout',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='earnings',
        help_text="Payout record if this earning has been paid"
    )
    
    # Dates
    earned_date = models.DateTimeField(default=timezone.now)
    paid_out_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_seller_earnings'
        verbose_name = 'seller earning'
        verbose_name_plural = 'seller earnings'
        ordering = ['-earned_date']
        indexes = [
            models.Index(fields=['seller', '-earned_date']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['order']),
            models.Index(fields=['is_paid_out']),
        ]
    
    def __str__(self):
        seller_name = self.seller.username if self.seller else "Unknown"
        return f"{seller_name} - {self.net_earnings} {self.currency}"
    
    def save(self, *args, **kwargs):
        """Calculate net earnings if not provided."""
        if not self.net_earnings and self.gross_sale_amount:
            self.net_earnings = self.gross_sale_amount - self.platform_commission
        super().save(*args, **kwargs)


class SellerPayout(models.Model):
    """
    Track payouts made to sellers.
    Groups multiple earnings into a single payout.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('check', 'Check'),
        ('cryptocurrency', 'Cryptocurrency'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Payout Identification
    payout_number = models.CharField(max_length=100, unique=True)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payouts',
        help_text="Seller receiving this payout"
    )
    
    # Payout Details
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total amount being paid out"
    )
    currency = models.CharField(max_length=3, default='USD')
    earnings_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of earnings included in this payout"
    )
    
    # Payment Information
    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default='bank_transfer'
    )
    payment_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Payment reference number or transaction ID"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Bank/Payment Details (can be encrypted in production)
    recipient_details = models.TextField(
        blank=True,
        help_text="Bank account or payment details (JSON format)"
    )
    
    # Processing
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payouts',
        help_text="Admin/staff who processed this payout"
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_seller_payout'
        verbose_name = 'seller payout'
        verbose_name_plural = 'seller payouts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['payout_number']),
        ]
    
    def __str__(self):
        return f"Payout {self.payout_number} - {self.seller.username}"
    
    @classmethod
    def generate_payout_number(cls):
        """Generate a unique payout number."""
        import random
        prefix = "PAYOUT"
        date_part = timezone.now().strftime("%Y%m%d")
        random_part = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        payout_number = f"{prefix}-{date_part}-{random_part}"
        
        # Ensure uniqueness
        while cls.objects.filter(payout_number=payout_number).exists():
            random_part = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            payout_number = f"{prefix}-{date_part}-{random_part}"
        
        return payout_number


class WalletTransaction(models.Model):
    """
    Track all wallet transactions for users.
    Includes deposits, withdrawals, purchases, refunds.
    """
    
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('purchase', 'Purchase Payment'),
        ('refund', 'Refund'),
        ('earnings', 'Seller Earnings Added'),
        ('payout', 'Seller Payout Deduction'),
        ('admin_adjustment', 'Admin Adjustment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('reversed', 'Reversed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User & Transaction Info
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet_transactions',
        help_text="User whose wallet is affected"
    )
    transaction_type = models.CharField(
        max_length=30,
        choices=TRANSACTION_TYPE_CHOICES
    )
    
    # Amount Details
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Transaction amount (positive for credits, negative for debits)"
    )
    balance_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="User's balance before this transaction"
    )
    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="User's balance after this transaction"
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Related Records
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wallet_transactions'
    )
    seller_earning = models.ForeignKey(
        SellerEarnings,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wallet_transactions'
    )
    payout = models.ForeignKey(
        SellerPayout,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wallet_transactions'
    )
    
    # Status & Processing
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_reference = models.CharField(max_length=255, blank=True)
    
    # Metadata
    description = models.CharField(max_length=500)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_wallet_transactions'
    )
    
    # Timestamps
    transaction_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_wallet_transaction'
        verbose_name = 'wallet transaction'
        verbose_name_plural = 'wallet transactions'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['user', '-transaction_date']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['status']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} {self.currency}"
