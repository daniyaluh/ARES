"""
Invoice generation and management service.
"""
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from decimal import Decimal
import logging

from .models import Invoice, InvoiceItem, PurchaseRequest

logger = logging.getLogger(__name__)


class InvoiceService:
    """Service for creating and managing invoices."""
    
    # Company information - can be customized in settings
    COMPANY_INFO = {
        'name': getattr(settings, 'COMPANY_NAME', 'ARES Robotics Corp'),
        'address': getattr(settings, 'COMPANY_ADDRESS', '1234 Tech Boulevard'),
        'city': getattr(settings, 'COMPANY_CITY', 'San Francisco'),
        'state': getattr(settings, 'COMPANY_STATE', 'CA'),
        'postal_code': getattr(settings, 'COMPANY_POSTAL_CODE', '94102'),
        'country': getattr(settings, 'COMPANY_COUNTRY', 'United States'),
        'phone': getattr(settings, 'COMPANY_PHONE', '+1 (555) 123-4567'),
        'email': getattr(settings, 'COMPANY_EMAIL', 'sales@ares-robotics.com'),
        'website': getattr(settings, 'COMPANY_WEBSITE', 'www.ares-robotics.com'),
        'tax_id': getattr(settings, 'COMPANY_TAX_ID', 'XX-XXXXXXX'),
    }
    
    # Default tax rate (can be overridden per invoice)
    DEFAULT_TAX_RATE = Decimal(getattr(settings, 'DEFAULT_TAX_RATE', '0.00'))
    
    # Default payment terms in days
    DEFAULT_PAYMENT_DAYS = getattr(settings, 'DEFAULT_PAYMENT_DAYS', 30)
    
    @classmethod
    def create_invoice_from_purchase_request(cls, purchase_request, created_by=None, tax_rate=None, notes=''):
        """
        Create an invoice from an approved purchase request.
        
        Args:
            purchase_request: The PurchaseRequest object
            created_by: The user who created/approved the invoice
            tax_rate: Optional custom tax rate (Decimal)
            notes: Optional notes to add to the invoice
            
        Returns:
            Invoice object
        """
        if purchase_request.status != 'approved':
            raise ValueError("Cannot create invoice for non-approved purchase request")
        
        # Check if invoice already exists
        if hasattr(purchase_request, 'invoice') and purchase_request.invoice is not None:
            logger.warning(f"Invoice already exists for purchase request {purchase_request.id}")
            return purchase_request.invoice
        
        # Get customer information
        user = purchase_request.user
        
        # Generate invoice number
        invoice_number = Invoice.generate_invoice_number()
        
        # Calculate due date
        due_date = timezone.now().date() + timedelta(days=cls.DEFAULT_PAYMENT_DAYS)
        
        # Get product price
        product = purchase_request.product
        if product and hasattr(product, 'price'):
            unit_price = Decimal(str(product.price)) if product.price else Decimal('0')
        else:
            unit_price = Decimal('0')
        
        quantity = purchase_request.quantity
        subtotal = unit_price * quantity
        
        # Calculate tax
        tax_rate_to_use = tax_rate if tax_rate is not None else cls.DEFAULT_TAX_RATE
        tax_amount = (subtotal * tax_rate_to_use) / 100
        total_amount = subtotal + tax_amount
        
        # Create the invoice
        invoice = Invoice.objects.create(
            purchase_request=purchase_request,
            invoice_number=invoice_number,
            status='issued',
            
            # Customer info
            customer_name=purchase_request.contact_name or user.get_full_name() or user.username,
            customer_email=purchase_request.contact_email or user.email,
            customer_company=purchase_request.company_name or '',
            customer_phone=purchase_request.contact_phone or '',
            
            # Billing address (use shipping address if available)
            billing_address=purchase_request.shipping_address or '',
            billing_city=purchase_request.shipping_city or '',
            billing_state=purchase_request.shipping_state or '',
            billing_postal_code=purchase_request.shipping_postal_code or '',
            billing_country=purchase_request.shipping_country or '',
            
            # Financials
            subtotal=subtotal,
            tax_rate=tax_rate_to_use,
            tax_amount=tax_amount,
            total_amount=total_amount,
            
            # Payment terms
            issue_date=timezone.now().date(),
            due_date=due_date,
            payment_terms=f"Net {cls.DEFAULT_PAYMENT_DAYS}",
            
            # Metadata
            notes=notes,
            created_by=created_by,
        )
        
        # Create invoice line item for the product
        if product:
            InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                description=product.title,
                quantity=quantity,
                unit_price=unit_price,
                line_total=subtotal,
                sku=str(product.id)[:8] if product.id else '',
            )
        
        logger.info(f"Invoice {invoice_number} created for purchase request {purchase_request.id}")
        
        return invoice
    
    @classmethod
    def mark_invoice_sent(cls, invoice):
        """Mark an invoice as sent."""
        invoice.status = 'sent'
        invoice.sent_at = timezone.now()
        invoice.save()
        logger.info(f"Invoice {invoice.invoice_number} marked as sent")
        return invoice
    
    @classmethod
    def mark_invoice_paid(cls, invoice):
        """Mark an invoice as paid."""
        invoice.status = 'paid'
        invoice.paid_at = timezone.now()
        invoice.save()
        logger.info(f"Invoice {invoice.invoice_number} marked as paid")
        return invoice
    
    @classmethod
    def cancel_invoice(cls, invoice, reason=''):
        """Cancel an invoice."""
        invoice.status = 'cancelled'
        if reason:
            invoice.internal_notes = f"{invoice.internal_notes}\nCancelled: {reason}".strip()
        invoice.save()
        logger.info(f"Invoice {invoice.invoice_number} cancelled")
        return invoice
    
    @classmethod
    def check_overdue_invoices(cls):
        """Check for overdue invoices and update their status."""
        today = timezone.now().date()
        overdue_invoices = Invoice.objects.filter(
            status__in=['issued', 'sent'],
            due_date__lt=today
        )
        
        count = overdue_invoices.update(status='overdue')
        if count > 0:
            logger.warning(f"Marked {count} invoice(s) as overdue")
        
        return count
    
    @classmethod
    def get_invoice_context(cls, invoice):
        """Get context dictionary for invoice rendering."""
        items = invoice.items.all()
        
        return {
            'invoice': invoice,
            'items': items,
            'company': cls.COMPANY_INFO,
            'issue_date': invoice.issue_date,
            'due_date': invoice.due_date,
        }


def create_notification_for_invoice(invoice, notification_type='purchase_request_approved'):
    """
    Create a notification for the user about their invoice.
    
    Args:
        invoice: The Invoice object
        notification_type: Type of notification to create
    """
    from users.models import Notification
    
    # Get the user from the purchase request
    user = None
    title = ""
    message = ""
    
    if invoice.purchase_request:
        user = invoice.purchase_request.user
        product_title = invoice.purchase_request.product.title if invoice.purchase_request.product else "your order"
        title = "Purchase Request Approved"
        message = f"Your purchase request for {product_title} has been approved. Invoice #{invoice.invoice_number} has been generated. Total amount: ${invoice.total_amount}"
    elif invoice.order:
        user = invoice.order.user
        title = "Invoice Generated"
        message = f"Invoice #{invoice.invoice_number} has been generated for your order. Total amount: ${invoice.total_amount}"
    
    if user:
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
        )
        logger.info(f"Notification created for user {user.username}: {title}")
        return notification
    
    return None
