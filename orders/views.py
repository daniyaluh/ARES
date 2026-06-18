"""
Views for Orders app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncDate, TruncMonth
from django.db import transaction
from decimal import Decimal
from .models import (
    PurchaseRequest, PurchaseRequestLog, Order, OrderItem, ApprovalChain,
    Transaction, Invoice, InvoiceItem, ShippingDetail, OrderStatusHistory,
    PlatformRevenue, SellerEarnings, SellerPayout, WalletTransaction
)
from .forms import PurchaseRequestForm, PurchaseRequestReviewForm
from .invoice_service import InvoiceService, create_notification_for_invoice
import logging

# Create logger for purchase request actions
purchase_request_logger = logging.getLogger('purchase_requests')


# Purchase Requests
@login_required
def purchase_request_list(request):
    """List purchase requests with filtering and stats."""
    # Get all requests for the user
    all_requests = PurchaseRequest.objects.filter(user=request.user).select_related('product')
    
    # Calculate stats
    total_requests = all_requests.count()
    pending_count = all_requests.filter(status__in=['pending', 'under_review']).count()
    approved_count = all_requests.filter(status='approved').count()
    rejected_count = all_requests.filter(status='rejected').count()
    
    # Filter by status if provided
    current_status = request.GET.get('status', '')
    if current_status and current_status in ['pending', 'under_review', 'approved', 'rejected', 'cancelled']:
        requests_list = all_requests.filter(status=current_status)
    else:
        requests_list = all_requests
    
    # Order by most recent first
    requests_list = requests_list.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(requests_list, 10)
    page = request.GET.get('page', 1)
    try:
        requests_page = paginator.page(page)
    except:
        requests_page = paginator.page(1)
    
    context = {
        'requests': requests_page,
        'total_requests': total_requests,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'current_status': current_status,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': requests_page,
    }
    
    return render(request, 'orders/purchase_request_list.html', context)


@login_required
def purchase_request_create(request):
    """Create purchase request with form for collecting detailed information."""
    from products.models import Product
    from verification.utils import can_access_robot
    from users.two_factor_utils import requires_2fa, get_primary_2fa_method, verify_2fa_code
    from users.views import is_2fa_verified

    # Handle 2FA verification callback
    if request.method == 'POST' and '2fa_code' in request.POST:
        code = request.POST.get('2fa_code', '').strip()
        product_id = request.session.get('purchase_product_id')
        
        if not code or not product_id:
            messages.error(request, "Invalid verification request.")
            return redirect('home')
        
        # Verify 2FA code
        success, security_key, method = verify_2fa_code(request.user, code, purpose='purchase')
        
        if not success:
            messages.error(request, "Invalid verification code. Please try again.")
            try:
                product = Product.objects.get(id=product_id)
                return render(request, 'orders/purchase_2fa_verify.html', {
                    'product': product,
                    'error': 'Invalid code'
                })
            except Product.DoesNotExist:
                return redirect('home')
        
        # 2FA verified - redirect to form
        request.session['2fa_verified'] = True
        request.session['2fa_verified_at'] = timezone.now().isoformat()
        request.session['2fa_verified_for'] = 'purchase'
        
        try:
            product = Product.objects.select_related('robot').get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
            return redirect('home')
        
        # Show the form
        form = PurchaseRequestForm(user=request.user)
        return render(request, 'orders/purchase_request_form.html', {
            'form': form,
            'product': product
        })

    # Initial request - check product_id
    product_id = request.POST.get('product_id') or request.GET.get('product_id')
    
    if not product_id:
        messages.error(request, "Product ID is required.")
        return redirect('home')
    
    try:
        product = Product.objects.select_related('robot').get(id=product_id)
    except (Product.DoesNotExist, ValueError):
        messages.error(request, "Product not found.")
        return redirect('home')
    
    # Check access for restricted robots (superusers bypass all checks)
    if hasattr(product, 'robot') and not request.user.is_superuser:
        robot = product.robot
        can_access, reason = can_access_robot(request.user, robot)
        if not can_access:
            messages.error(request, f"Cannot create purchase request: {reason}")
            return redirect('verification:robot-detail', robot_id=robot.id)
        
        # Check license requirement
        if robot.requires_license:
            if not robot.user_has_valid_license(request.user):
                license_info = robot.license_requirement_info
                messages.error(request, f"Cannot create purchase request: This robot requires an approved {license_info['short_label']}.")
                return redirect('verification:robot-detail', robot_id=robot.id)

    # Check if 2FA is required
    if requires_2fa(request.user) and not is_2fa_verified(request, 'purchase'):
        request.session['purchase_product_id'] = str(product.id)
        
        method = get_primary_2fa_method(request.user)
        email_code = None
        if method == 'email':
            from users.email_verification_service import generate_and_send_email_code
            code, sent, message = generate_and_send_email_code(request.user, purpose='purchase')
            if sent and settings.DEBUG:
                request.session['email_code_display'] = code
                email_code = code
                messages.info(request, f"Email verification code: {code} (Development mode)")
            else:
                messages.info(request, f"Verification code sent to {request.user.email}")
        
        messages.info(request, "Please verify your identity with 2FA to continue.")
        return render(request, 'orders/purchase_2fa_verify.html', {
            'product': product,
            'method': method,
            'email_code': email_code
        })

    if request.method == 'POST' and 'intended_use' in request.POST:
        # Form submission with all details
        form = PurchaseRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            purchase_request = form.save(commit=False)
            purchase_request.user = request.user
            purchase_request.product = product
            purchase_request.status = 'pending'
            purchase_request.save()
            
            # Log the action
            purchase_request.log_action(
                action='created',
                user=request.user,
                details=f"Purchase request created for {product.title} x{purchase_request.quantity}"
            )
            
            # Clear session data
            request.session.pop('purchase_product_id', None)
            request.session.pop('2fa_verified', None)
            request.session.pop('2fa_verified_at', None)
            request.session.pop('2fa_verified_for', None)
            
            messages.success(request, f"Purchase request submitted for {product.title}. Our team will review it shortly.")
            return redirect('orders:purchase-request-detail', request_id=purchase_request.id)
        else:
            return render(request, 'orders/purchase_request_form.html', {
                'form': form,
                'product': product
            })
    
    # Show the form (GET request or initial POST to go to form)
    form = PurchaseRequestForm(user=request.user)
    return render(request, 'orders/purchase_request_form.html', {
        'form': form,
        'product': product
    })


@login_required
def purchase_request_detail(request, request_id):
    """Purchase request detail."""
    req = get_object_or_404(PurchaseRequest.objects.select_related('product', 'product__robot'), id=request_id)
    
    # Users can only view their own requests (unless staff)
    if req.user != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to view this request.")
        return redirect('orders:purchase-request-list')
    
    # Get the invoice if it exists (for approved requests)
    invoice = None
    if req.status == 'approved':
        try:
            invoice = req.invoice
        except:
            invoice = None
    
    return render(request, 'orders/purchase_request_detail.html', {
        'request': req,
        'invoice': invoice,
    })


@login_required
def purchase_request_update(request, request_id):
    """Update purchase request."""
    req = get_object_or_404(PurchaseRequest, id=request_id, user=request.user)
    
    if req.status != 'pending':
        messages.error(request, "Cannot update a request that is not pending.")
        return redirect('orders:purchase-request-detail', request_id=request_id)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        req.notes = notes
        req.save()
        messages.success(request, "Purchase request updated.")
        return redirect('orders:purchase-request-detail', request_id=request_id)
    
    return render(request, 'orders/purchase_request_edit.html', {'request': req})


@login_required
def purchase_request_cancel(request, request_id):
    """Cancel purchase request."""
    req = get_object_or_404(PurchaseRequest, id=request_id, user=request.user)
    
    if request.method == 'POST':
        # Log the cancellation before deletion
        purchase_request_logger.info(
            f"[{req.id}] Action: cancelled | User: {request.user.username} | "
            f"Product: {req.product.title if req.product else 'N/A'}"
        )
        req.delete()
        messages.success(request, "Purchase request cancelled.")
        return redirect('orders:purchase-request-list')
    
    return render(request, 'orders/purchase_request_cancel.html', {'request': req})


@login_required
def purchase_request_approve(request, request_id):
    """Approve purchase request (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    req = get_object_or_404(PurchaseRequest, id=request_id)
    
    if request.method == 'POST':
        review_notes = request.POST.get('review_notes', '')
        
        # Calculate total amount
        product = req.product
        if not product:
            messages.error(request, "Cannot approve request without a product.")
            return redirect('orders:purchase-request-detail', request_id=request_id)
        
        quantity = req.quantity
        total_amount = product.price * quantity
        
        # Check user wallet balance
        user_balance = WalletTransaction.objects.filter(user=req.user).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        if user_balance < total_amount:
            messages.error(request, f"Insufficient wallet balance. User has ${user_balance:,.2f} but needs ${total_amount:,.2f}.")
            return redirect('orders:purchase-request-detail', request_id=request_id)
        
        try:
            with transaction.atomic():
                # Update purchase request
                req.status = 'approved'
                req.reviewed_by = request.user
                req.reviewed_at = timezone.now()
                req.review_notes = review_notes
                req.save()
                
                # Create Order
                order = Order.objects.create(
                    user=req.user,
                    order_number=f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}-{req.user.id}",
                    status='completed',
                    total_amount=total_amount
                )
                
                # Create OrderItem
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                
                # Create Transaction
                txn = Transaction.objects.create(
                    order=order,
                    amount=total_amount,
                    transaction_type='purchase'
                )
                
                # Deduct from wallet - Get current balance
                prev_txn = WalletTransaction.objects.filter(user=req.user).order_by('-created_at').first()
                balance_before = prev_txn.balance_after if prev_txn else Decimal('0')
                balance_after = balance_before - total_amount
                
                # Create wallet deduction transaction
                WalletTransaction.objects.create(
                    user=req.user,
                    transaction_type='purchase',
                    amount=-total_amount,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    description=f'Purchase: {product.title} (Qty: {quantity})',
                    order=order,
                    status='completed'
                )
                
                # Create platform revenue
                commission_rate = Decimal('15.00')  # 15% default commission
                commission_amount = (total_amount * commission_rate) / 100
                
                PlatformRevenue.objects.create(
                    order=order,
                    transaction=txn,
                    seller=product.seller,
                    gross_amount=total_amount,
                    commission_rate=commission_rate,
                    commission_amount=commission_amount
                )
                
                # Create seller earnings
                net_earnings = total_amount - commission_amount
                seller_earning = SellerEarnings.objects.create(
                    seller=product.seller,
                    order=order,
                    transaction=txn,
                    product=product,
                    gross_sale_amount=total_amount,
                    platform_commission=commission_amount,
                    net_earnings=net_earnings,
                    status='completed',
                    is_paid_out=True
                )
                
                # Credit seller's wallet with net earnings (after commission)
                seller_prev_txn = WalletTransaction.objects.filter(user=product.seller).order_by('-created_at').first()
                seller_balance_before = seller_prev_txn.balance_after if seller_prev_txn else Decimal('0')
                seller_balance_after = seller_balance_before + net_earnings
                
                WalletTransaction.objects.create(
                    user=product.seller,
                    transaction_type='sale',
                    amount=net_earnings,
                    balance_before=seller_balance_before,
                    balance_after=seller_balance_after,
                    description=f'Sale: {product.title} (Qty: {quantity}) - Net after {commission_rate}% commission',
                    order=order,
                    status='completed'
                )
                
                # Generate invoice
                invoice = InvoiceService.create_invoice_from_purchase_request(
                    purchase_request=req,
                    created_by=request.user,
                    notes=review_notes
                )
                
                # Link order to invoice
                invoice.order = order
                invoice.status = 'paid'  # Mark as paid since funds were deducted
                invoice.paid_at = timezone.now()
                invoice.save()
                
                # Log the action
                req.log_action(
                    action='approved',
                    user=request.user,
                    details=f"Approved by {request.user.username}. Order #{order.order_number} created. ${total_amount} deducted from wallet. Invoice #{invoice.invoice_number} generated."
                )
                
                # Create notification for the user
                create_notification_for_invoice(invoice)
                
                messages.success(request, f"Purchase request approved! Order #{order.order_number} created, ${total_amount:,.2f} deducted from wallet, Invoice #{invoice.invoice_number} generated.")
                
        except Exception as e:
            purchase_request_logger.error(f"Failed to process approval for {req.id}: {str(e)}")
            messages.error(request, f"Failed to process approval: {str(e)}")
            return redirect('orders:purchase-request-detail', request_id=request_id)
        
        return redirect('orders:staff-pending-requests')
    
    return redirect('orders:purchase-request-detail', request_id=request_id)


@login_required
def purchase_request_reject(request, request_id):
    """Reject purchase request (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    req = get_object_or_404(PurchaseRequest, id=request_id)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        review_notes = request.POST.get('review_notes', '')
        
        if not rejection_reason:
            messages.error(request, "Rejection reason is required.")
            return redirect('orders:staff-request-review', request_id=request_id)
        
        req.status = 'rejected'
        req.reviewed_by = request.user
        req.reviewed_at = timezone.now()
        req.rejection_reason = rejection_reason
        req.review_notes = review_notes
        req.save()
        
        # Log the action
        req.log_action(
            action='rejected',
            user=request.user,
            details=f"Rejected by {request.user.username}. Reason: {rejection_reason}"
        )
        
        messages.success(request, f"Purchase request rejected for {req.user.username}.")
        return redirect('orders:staff-pending-requests')
    
    return redirect('orders:purchase-request-detail', request_id=request_id)


@login_required
def staff_pending_requests(request):
    """Staff view for all pending purchase requests."""
    # Allow both staff and admin users (superuser or access_level >= 60)
    if not (request.user.is_staff or request.user.is_superuser or getattr(request.user, 'access_level', 0) >= 60):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'pending')
    urgency_filter = request.GET.get('urgency', '')
    
    # Base queryset
    requests = PurchaseRequest.objects.select_related('user', 'product', 'product__robot').order_by('-created_at')
    
    # Apply filters
    if status_filter:
        requests = requests.filter(status=status_filter)
    if urgency_filter:
        requests = requests.filter(urgency=urgency_filter)
    
    # Pagination
    paginator = Paginator(requests, 20)
    page = request.GET.get('page')
    requests_page = paginator.get_page(page)
    
    # Get counts for tabs
    pending_count = PurchaseRequest.objects.filter(status='pending').count()
    under_review_count = PurchaseRequest.objects.filter(status='under_review').count()
    approved_count = PurchaseRequest.objects.filter(status='approved').count()
    rejected_count = PurchaseRequest.objects.filter(status='rejected').count()
    
    return render(request, 'orders/staff_pending_requests.html', {
        'requests': requests_page,
        'status_filter': status_filter,
        'urgency_filter': urgency_filter,
        'pending_count': pending_count,
        'under_review_count': under_review_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    })


@login_required
def staff_request_review(request, request_id):
    """Staff view for reviewing a specific purchase request."""
    # Allow both staff and admin users (superuser or access_level >= 60)
    if not (request.user.is_staff or request.user.is_superuser or getattr(request.user, 'access_level', 0) >= 60):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    req = get_object_or_404(
        PurchaseRequest.objects.select_related('user', 'product', 'product__robot', 'reviewed_by'),
        id=request_id
    )
    
    # Get request logs
    logs = req.logs.select_related('performed_by').order_by('-created_at')
    
    # Check if invoice already exists
    existing_invoice = getattr(req, 'invoice', None)
    
    if request.method == 'POST':
        form = PurchaseRequestReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            review_notes = form.cleaned_data.get('review_notes', '')
            rejection_reason = form.cleaned_data.get('rejection_reason', '')
            
            if action == 'approve':
                req.status = 'approved'
                req.reviewed_by = request.user
                req.reviewed_at = timezone.now()
                req.review_notes = review_notes
                req.save()
                req.log_action(
                    action='approved',
                    user=request.user,
                    details=f"Approved by {request.user.username}. Notes: {review_notes}"
                )
                
                # Generate invoice for approved request
                try:
                    invoice = InvoiceService.create_invoice_from_purchase_request(
                        purchase_request=req,
                        created_by=request.user,
                        notes=review_notes
                    )
                    # Create notification for the user
                    create_notification_for_invoice(invoice)
                    messages.success(request, f"Purchase request approved. Invoice #{invoice.invoice_number} generated and notification sent.")
                except Exception as e:
                    purchase_request_logger.error(f"Failed to create invoice for {req.id}: {str(e)}")
                    messages.success(request, f"Purchase request approved. (Invoice generation failed: {str(e)})")
                
            elif action == 'reject':
                req.status = 'rejected'
                req.reviewed_by = request.user
                req.reviewed_at = timezone.now()
                req.rejection_reason = rejection_reason
                req.review_notes = review_notes
                req.save()
                req.log_action(
                    action='rejected',
                    user=request.user,
                    details=f"Rejected by {request.user.username}. Reason: {rejection_reason}"
                )
                
                # Create rejection notification
                try:
                    from users.models import Notification
                    product_title = req.product.title if req.product else "your order"
                    Notification.objects.create(
                        user=req.user,
                        notification_type='purchase_request_rejected',
                        title='Purchase Request Rejected',
                        message=f"Your purchase request for {product_title} has been rejected. Reason: {rejection_reason}"
                    )
                except Exception as e:
                    purchase_request_logger.error(f"Failed to create rejection notification: {str(e)}")
                
                messages.success(request, f"Purchase request rejected.")
                
            elif action == 'under_review':
                req.status = 'under_review'
                req.reviewed_by = request.user
                req.review_notes = review_notes
                req.save()
                req.log_action(
                    action='under_review',
                    user=request.user,
                    details=f"Marked under review by {request.user.username}. Notes: {review_notes}"
                )
                messages.success(request, f"Purchase request marked as under review.")
            
            return redirect('orders:staff-pending-requests')
    else:
        form = PurchaseRequestReviewForm()
    
    return render(request, 'orders/staff_request_review.html', {
        'purchase_request': req,
        'form': form,
        'logs': logs,
        'existing_invoice': existing_invoice,
    })


# Orders
@login_required
def order_list(request):
    """List all orders (staff) or user orders."""
    if request.user.is_staff:
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(user=request.user)
    
    paginator = Paginator(orders, 20)
    page = request.GET.get('page')
    orders_page = paginator.get_page(page)
    return render(request, 'orders/order_list.html', {'orders': orders_page})


@login_required
def order_my_list(request):
    """My orders."""
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_my_list.html', {'orders': orders})


@login_required
def order_create(request):
    """Create order."""
    if request.method == 'POST':
        # Placeholder - implement full order creation
        messages.success(request, "Order created successfully.")
        return redirect('orders:order-list')
    
    return render(request, 'orders/order_create.html')


def order_detail(request, order_id):
    """Order detail."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_update(request, order_id):
    """Update order."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        messages.success(request, "Order updated.")
        return redirect('orders:order-detail', order_id=order_id)
    
    return render(request, 'orders/order_edit.html', {'order': order})


@login_required
def order_cancel(request, order_id):
    """Cancel order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        order.status = 'cancelled'
        order.save()
        messages.success(request, "Order cancelled.")
        return redirect('orders:order-detail', order_id=order_id)
    
    return render(request, 'orders/order_cancel.html', {'order': order})


@login_required
def order_complete(request, order_id):
    """Complete order."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        order.status = 'completed'
        order.save()
        messages.success(request, "Order marked as completed.")
        return redirect('orders:order-detail', order_id=order_id)
    
    return redirect('orders:order-detail', order_id=order_id)


# Order Items
def order_item_list(request, order_id):
    """List order items."""
    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order)
    return render(request, 'orders/order_item_list.html', {'order': order, 'items': items})


@login_required
def order_item_create(request, order_id):
    """Add item to order."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Placeholder
        messages.success(request, "Item added to order.")
        return redirect('orders:order-item-list', order_id=order_id)
    
    return render(request, 'orders/order_item_create.html', {'order': order})


def order_item_detail(request, item_id):
    """Order item detail."""
    item = get_object_or_404(OrderItem, id=item_id)
    return render(request, 'orders/order_item_detail.html', {'item': item})


@login_required
def order_item_update(request, item_id):
    """Update order item."""
    item = get_object_or_404(OrderItem, id=item_id)
    
    if request.method == 'POST':
        messages.success(request, "Order item updated.")
        return redirect('orders:order-item-list', order_id=item.order.id)
    
    return render(request, 'orders/order_item_edit.html', {'item': item})


@login_required
def order_item_delete(request, item_id):
    """Delete order item."""
    item = get_object_or_404(OrderItem, id=item_id)
    
    if request.method == 'POST':
        order_id = item.order.id
        item.delete()
        messages.success(request, "Order item deleted.")
        return redirect('orders:order-item-list', order_id=order_id)
    
    return render(request, 'orders/order_item_delete.html', {'item': item})


# Approval Chain
def approval_chain_list(request, order_id):
    """List approval chain."""
    order = get_object_or_404(Order, id=order_id)
    approvals = ApprovalChain.objects.filter(order=order)
    return render(request, 'orders/approval_chain_list.html', {'order': order, 'approvals': approvals})


@login_required
def approval_chain_create(request, order_id):
    """Create approval chain."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Placeholder
        messages.success(request, "Approval chain created.")
        return redirect('orders:approval-chain-list', order_id=order_id)
    
    return render(request, 'orders/approval_chain_create.html', {'order': order})


@login_required
def approval_chain_approve(request, approval_id):
    """Approve in chain."""
    approval = get_object_or_404(ApprovalChain, id=approval_id)
    approval.status = 'approved'
    approval.save()
    messages.success(request, "Approved.")
    return redirect('orders:approval-chain-list', order_id=approval.order.id)


@login_required
def approval_chain_reject(request, approval_id):
    """Reject in chain."""
    approval = get_object_or_404(ApprovalChain, id=approval_id)
    approval.status = 'rejected'
    approval.save()
    messages.success(request, "Rejected.")
    return redirect('orders:approval-chain-list', order_id=approval.order.id)


# Transactions
@login_required
def transaction_list(request):
    """List transactions."""
    if request.user.is_staff:
        transactions = Transaction.objects.all()
    else:
        transactions = Transaction.objects.filter(order__user=request.user)
    
    return render(request, 'orders/transaction_list.html', {'transactions': transactions})


def transaction_detail(request, transaction_id):
    """Transaction detail."""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    return render(request, 'orders/transaction_detail.html', {'transaction': transaction})


@login_required
def transaction_create(request):
    """Create transaction."""
    messages.info(request, "Transaction creation coming soon.")
    return redirect('orders:transaction-list')


def order_transactions(request, order_id):
    """Transactions for an order."""
    order = get_object_or_404(Order, id=order_id)
    transactions = Transaction.objects.filter(order=order)
    return render(request, 'orders/order_transactions.html', {'order': order, 'transactions': transactions})


# Legacy invoice functions removed - using improved versions below

@login_required
def invoice_send(request, invoice_id):
    """Send invoice via email."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    messages.info(request, "Invoice sent.")
    return redirect('orders:invoice-detail', invoice_id=invoice_id)


def order_invoice(request, order_id):
    """Invoice for an order."""
    order = get_object_or_404(Order, id=order_id)
    invoice, created = Invoice.objects.get_or_create(order=order)
    return redirect('orders:invoice-detail', invoice_id=invoice.id)


# Shipping
def shipping_detail(request, order_id):
    """Shipping detail."""
    order = get_object_or_404(Order, id=order_id)
    shipping = getattr(order, 'shipping', None)
    return render(request, 'orders/shipping_detail.html', {'order': order, 'shipping': shipping})


@login_required
def shipping_update(request, order_id):
    """Update shipping."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        messages.success(request, "Shipping updated.")
        return redirect('orders:shipping-detail', order_id=order_id)
    
    return render(request, 'orders/shipping_edit.html', {'order': order})


def shipping_track(request, order_id):
    """Track shipping."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/shipping_track.html', {'order': order})


@login_required
def shipping_create(request):
    """Create shipping detail."""
    messages.info(request, "Shipping creation coming soon.")
    return redirect('orders:order-list')


# Order Status
def order_status_history(request, order_id):
    """Order status history."""
    order = get_object_or_404(Order, id=order_id)
    history = OrderStatusHistory.objects.filter(order=order).order_by('-created_at')
    return render(request, 'orders/order_status_history.html', {'order': order, 'history': history})


@login_required
def order_status_update(request, order_id):
    """Update order status."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        OrderStatusHistory.objects.create(order=order, status=new_status, updated_by=request.user)
        order.status = new_status
        order.save()
        messages.success(request, "Order status updated.")
        return redirect('orders:order-detail', order_id=order_id)
    
    return redirect('orders:order-detail', order_id=order_id)


# Filter & Search
def order_filter(request):
    """Filter orders."""
    status = request.GET.get('status')
    orders = Order.objects.all()
    
    if status:
        orders = orders.filter(status=status)
    
    return render(request, 'orders/order_filter.html', {'orders': orders})


def order_search(request):
    """Search orders."""
    query = request.GET.get('q', '')
    orders = Order.objects.filter(order_number__icontains=query)
    return render(request, 'orders/order_search.html', {'orders': orders, 'query': query})


def order_by_status(request, status):
    """Orders by status."""
    orders = Order.objects.filter(status=status)
    return render(request, 'orders/order_by_status.html', {'orders': orders, 'status': status})


def order_by_date(request):
    """Orders by date."""
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders/order_by_date.html', {'orders': orders})


# Analytics & Reports
@login_required
def order_analytics(request):
    """Order analytics."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    total_orders = Order.objects.count()
    return render(request, 'orders/order_analytics.html', {'total_orders': total_orders})


@login_required
def order_reports(request):
    """Order reports."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'orders/order_reports.html')


@login_required
def order_sales_report(request):
    """Sales report."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    return render(request, 'orders/order_sales_report.html')


# Invoice Views
@login_required
def invoice_list(request):
    """List user's invoices."""
    # Get invoices for the current user via their purchase requests
    invoices = Invoice.objects.filter(
        purchase_request__user=request.user
    ).select_related('purchase_request', 'purchase_request__product').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    # Get counts
    all_count = Invoice.objects.filter(purchase_request__user=request.user).count()
    pending_count = Invoice.objects.filter(purchase_request__user=request.user, status__in=['draft', 'issued', 'sent']).count()
    paid_count = Invoice.objects.filter(purchase_request__user=request.user, status='paid').count()
    
    # Pagination
    paginator = Paginator(invoices, 10)
    page = request.GET.get('page')
    invoices_page = paginator.get_page(page)
    
    return render(request, 'orders/invoice_list.html', {
        'invoices': invoices_page,
        'status_filter': status_filter,
        'all_count': all_count,
        'pending_count': pending_count,
        'paid_count': paid_count,
    })


@login_required
def invoice_detail(request, invoice_id):
    """View invoice details."""
    invoice = get_object_or_404(
        Invoice.objects.select_related('purchase_request', 'purchase_request__product', 'purchase_request__user', 'created_by'),
        id=invoice_id
    )
    
    # Check access - user can only see their own invoices, staff can see all
    if not request.user.is_staff:
        if invoice.purchase_request and invoice.purchase_request.user != request.user:
            messages.error(request, "Access denied.")
            return redirect('orders:invoice-list')
        if invoice.order and invoice.order.user != request.user:
            messages.error(request, "Access denied.")
            return redirect('orders:invoice-list')
    
    # Get invoice items
    items = invoice.items.select_related('product').all()
    
    # Get company info
    company = InvoiceService.COMPANY_INFO
    
    return render(request, 'orders/invoice_detail.html', {
        'invoice': invoice,
        'items': items,
        'company': company,
    })


@login_required  
def invoice_download(request, invoice_id):
    """Download invoice as PDF (placeholder - returns HTML printable version)."""
    invoice = get_object_or_404(
        Invoice.objects.select_related('purchase_request', 'purchase_request__product', 'purchase_request__user', 'created_by'),
        id=invoice_id
    )
    
    # Check access
    if not request.user.is_staff:
        if invoice.purchase_request and invoice.purchase_request.user != request.user:
            messages.error(request, "Access denied.")
            return redirect('orders:invoice-list')
    
    # Get invoice items
    items = invoice.items.select_related('product').all()
    
    # Get company info
    company = InvoiceService.COMPANY_INFO
    
    return render(request, 'orders/invoice_print.html', {
        'invoice': invoice,
        'items': items,
        'company': company,
    })


# Staff Invoice Views
@login_required
def staff_invoice_list(request):
    """Staff view for all invoices."""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    invoices = Invoice.objects.select_related(
        'purchase_request', 'purchase_request__user', 'purchase_request__product', 'created_by'
    ).order_by('-created_at')
    
    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    # Search
    search = request.GET.get('q', '')
    if search:
        from django.db.models import Q
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(customer_email__icontains=search) |
            Q(customer_company__icontains=search)
        )
    
    # Stats
    total_count = Invoice.objects.count()
    issued_count = Invoice.objects.filter(status='issued').count()
    sent_count = Invoice.objects.filter(status='sent').count()
    paid_count = Invoice.objects.filter(status='paid').count()
    overdue_count = Invoice.objects.filter(status='overdue').count()
    
    # Pagination
    paginator = Paginator(invoices, 20)
    page = request.GET.get('page')
    invoices_page = paginator.get_page(page)
    
    return render(request, 'orders/staff_invoice_list.html', {
        'invoices': invoices_page,
        'status_filter': status_filter,
        'search': search,
        'total_count': total_count,
        'issued_count': issued_count,
        'sent_count': sent_count,
        'paid_count': paid_count,
        'overdue_count': overdue_count,
    })


@login_required
def staff_invoice_update_status(request, invoice_id):
    """Staff action to update invoice status with notifications and logging."""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status', '')
        valid_statuses = ['draft', 'issued', 'sent', 'paid', 'overdue', 'cancelled']
        
        if new_status in valid_statuses:
            old_status = invoice.status
            
            # Don't update if same status
            if old_status == new_status:
                messages.info(request, f"Invoice is already {new_status}.")
                return redirect('orders:staff-invoice-list')
            
            invoice.status = new_status
            
            # Set timestamps and handle specific status transitions
            if new_status == 'sent' and not invoice.sent_at:
                invoice.sent_at = timezone.now()
            elif new_status == 'paid' and not invoice.paid_at:
                invoice.paid_at = timezone.now()
            
            invoice.save()
            
            # Create notification for the user
            customer = None
            if invoice.purchase_request:
                customer = invoice.purchase_request.user
            elif invoice.order:
                customer = invoice.order.user
            
            if customer:
                from users.models import Notification
                
                # Different notification messages based on status
                notification_messages = {
                    'draft': {
                        'title': f'Invoice {invoice.invoice_number} Draft',
                        'message': f'Your invoice #{invoice.invoice_number} has been set to draft status.',
                        'type': 'general',
                    },
                    'issued': {
                        'title': f'Invoice {invoice.invoice_number} Issued',
                        'message': f'Your invoice #{invoice.invoice_number} for ${invoice.total_amount} has been issued. Please review and proceed with payment.',
                        'type': 'invoice_issued',
                    },
                    'sent': {
                        'title': f'Invoice {invoice.invoice_number} Sent',
                        'message': f'Your invoice #{invoice.invoice_number} has been sent. Due date: {invoice.due_date.strftime("%B %d, %Y") if invoice.due_date else "N/A"}.',
                        'type': 'invoice_sent',
                    },
                    'paid': {
                        'title': f'Payment Received - Invoice {invoice.invoice_number}',
                        'message': f'Thank you! Your payment of ${invoice.total_amount} for invoice #{invoice.invoice_number} has been received.',
                        'type': 'invoice_paid',
                    },
                    'overdue': {
                        'title': f'Invoice {invoice.invoice_number} Overdue',
                        'message': f'Your invoice #{invoice.invoice_number} for ${invoice.total_amount} is now overdue. Please make payment as soon as possible.',
                        'type': 'invoice_overdue',
                    },
                    'cancelled': {
                        'title': f'Invoice {invoice.invoice_number} Cancelled',
                        'message': f'Your invoice #{invoice.invoice_number} has been cancelled. If you have questions, please contact support.',
                        'type': 'invoice_cancelled',
                    },
                }
                
                if new_status in notification_messages:
                    notif_data = notification_messages[new_status]
                    try:
                        Notification.objects.create(
                            user=customer,
                            notification_type=notif_data.get('type', 'general'),
                            title=notif_data['title'],
                            message=notif_data['message'],
                        )
                    except Exception as e:
                        # Log error but don't fail the status update
                        purchase_request_logger.error(f"Failed to create notification: {e}")
            
            # Log the status change
            purchase_request_logger.info(
                f"Invoice {invoice.invoice_number} status changed from {old_status} to {new_status} by {request.user.username}"
            )
            
            messages.success(request, f"Invoice {invoice.invoice_number} status updated from '{old_status}' to '{new_status}'.")
        else:
            messages.error(request, "Invalid status.")
    
    return redirect('orders:staff-invoice-list')

@login_required
def generate_invoice_for_request(request, request_id):
    """Generate an invoice for an approved purchase request that doesn't have one yet."""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    purchase_request = get_object_or_404(PurchaseRequest, id=request_id)
    
    # Check if already has an invoice
    if hasattr(purchase_request, 'invoice'):
        messages.info(request, f"Invoice {purchase_request.invoice.invoice_number} already exists for this request.")
        return redirect('orders:invoice-detail', invoice_id=purchase_request.invoice.id)
    
    # Only generate for approved requests
    if purchase_request.status != 'approved':
        messages.error(request, "Invoices can only be generated for approved purchase requests.")
        return redirect('orders:staff-purchase-requests')
    
    # Generate the invoice
    invoice = InvoiceService.create_invoice_from_purchase_request(purchase_request)
    
    if invoice:
        messages.success(request, f"Invoice {invoice.invoice_number} has been generated successfully.")
        return redirect('orders:invoice-detail', invoice_id=invoice.id)
    else:
        messages.error(request, "Failed to generate invoice.")
        return redirect('orders:staff-purchase-requests')


@login_required
def generate_missing_invoices(request):
    """Staff view to generate invoices for all approved requests without invoices."""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    # Find all approved requests without invoices
    approved_requests = PurchaseRequest.objects.filter(status='approved')
    missing_invoice_requests = []
    
    for pr in approved_requests:
        if not hasattr(pr, 'invoice'):
            missing_invoice_requests.append(pr)
    
    if request.method == 'POST':
        generated_count = 0
        for pr in missing_invoice_requests:
            invoice = InvoiceService.create_invoice_from_purchase_request(pr)
            if invoice:
                generated_count += 1
        
        messages.success(request, f"Generated {generated_count} invoices.")
        return redirect('orders:staff-invoice-list')
    
    return render(request, 'orders/generate_missing_invoices.html', {
        'missing_count': len(missing_invoice_requests),
        'missing_requests': missing_invoice_requests[:20],  # Show first 20
    })


@login_required
def order_export(request):
    """Export orders."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    messages.info(request, "Export functionality coming soon.")
    return redirect('orders:order-reports')


# ============================================================================
# FINANCIAL VIEWS - Revenue Tracking & Payment Management
# ============================================================================

# ADMIN/STAFF FINANCE VIEWS

@login_required
def admin_finance_dashboard(request):
    """
    Admin finance dashboard showing platform revenue, seller earnings, and analytics.
    Only accessible to staff and superusers.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('home')
    
    # Date filters
    from datetime import timedelta
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Total Company Revenue (Gross Sales from all orders)
    total_gross_sales = PlatformRevenue.objects.aggregate(
        total=Sum('gross_amount')
    )['total'] or 0
    
    gross_sales_last_30_days = PlatformRevenue.objects.filter(
        revenue_date__gte=thirty_days_ago
    ).aggregate(total=Sum('gross_amount'))['total'] or 0
    
    # Platform Revenue Stats (Commission earned)
    total_revenue = PlatformRevenue.objects.aggregate(
        total=Sum('commission_amount')
    )['total'] or 0
    
    revenue_last_30_days = PlatformRevenue.objects.filter(
        revenue_date__gte=thirty_days_ago
    ).aggregate(total=Sum('commission_amount'))['total'] or 0
    
    revenue_today = PlatformRevenue.objects.filter(
        revenue_date__date=today
    ).aggregate(total=Sum('commission_amount'))['total'] or 0
    
    # Seller Earnings Stats (Money paid to sellers)
    total_seller_earnings = SellerEarnings.objects.aggregate(
        total=Sum('net_earnings')
    )['total'] or 0
    
    pending_seller_earnings = SellerEarnings.objects.filter(
        is_paid_out=False,
        status='completed'
    ).aggregate(total=Sum('net_earnings'))['total'] or 0
    
    # Total number of sales/orders
    total_sales_count = PlatformRevenue.objects.count()
    
    # Payout Stats
    pending_payouts = SellerPayout.objects.filter(
        status='pending'
    ).count()
    
    total_payouts_amount = SellerPayout.objects.filter(
        status='completed'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Transaction Stats
    total_transactions = Transaction.objects.count()
    
    # Recent Platform Revenue (last 10)
    recent_revenues = PlatformRevenue.objects.select_related(
        'order', 'seller', 'transaction'
    ).order_by('-revenue_date')[:10]
    
    # Revenue by Day (last 30 days)
    daily_revenue = PlatformRevenue.objects.filter(
        revenue_date__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('revenue_date')
    ).values('date').annotate(
        total=Sum('commission_amount')
    ).order_by('date')
    
    # Top Sellers by Revenue Generated for Platform
    top_sellers = PlatformRevenue.objects.filter(
        seller__isnull=False
    ).values(
        'seller__username', 'seller__id'
    ).annotate(
        total_commission=Sum('commission_amount'),
        total_sales=Sum('gross_amount'),
        sales_count=Count('id')
    ).order_by('-total_sales')[:10]
    
    context = {
        'total_gross_sales': total_gross_sales,
        'gross_sales_last_30_days': gross_sales_last_30_days,
        'total_revenue': total_revenue,
        'revenue_last_30_days': revenue_last_30_days,
        'revenue_today': revenue_today,
        'total_seller_earnings': total_seller_earnings,
        'pending_seller_earnings': pending_seller_earnings,
        'pending_payouts': pending_payouts,
        'total_payouts_amount': total_payouts_amount,
        'total_transactions': total_transactions,
        'total_sales_count': total_sales_count,
        'recent_revenues': recent_revenues,
        'daily_revenue': list(daily_revenue),
        'top_sellers': top_sellers,
    }
    
    return render(request, 'orders/finance/admin_dashboard.html', context)


@login_required
def admin_platform_revenue_list(request):
    """
    List all platform revenue records.
    Staff/admin only.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    # Filters
    revenue_type = request.GET.get('type', '')
    seller_id = request.GET.get('seller', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    revenues = PlatformRevenue.objects.select_related(
        'order', 'seller', 'transaction'
    ).order_by('-revenue_date')
    
    # Apply filters
    if revenue_type:
        revenues = revenues.filter(revenue_type=revenue_type)
    
    if seller_id:
        revenues = revenues.filter(seller_id=seller_id)
    
    if date_from:
        revenues = revenues.filter(revenue_date__gte=date_from)
    
    if date_to:
        revenues = revenues.filter(revenue_date__lte=date_to)
    
    # Calculate totals
    total_commission = revenues.aggregate(total=Sum('commission_amount'))['total'] or 0
    
    # Pagination
    paginator = Paginator(revenues, 25)
    page = request.GET.get('page', 1)
    revenues_page = paginator.get_page(page)
    
    context = {
        'revenues': revenues_page,
        'total_commission': total_commission,
        'revenue_type': revenue_type,
        'seller_id': seller_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'orders/finance/admin_revenue_list.html', context)


@login_required
def admin_all_transactions(request):
    """
    View all transactions across the platform.
    Staff/admin only.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    # Filters
    transaction_type = request.GET.get('type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    transactions = Transaction.objects.select_related(
        'order'
    ).order_by('-created_at')
    
    # Apply filters
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    if date_from:
        transactions = transactions.filter(created_at__gte=date_from)
    
    if date_to:
        transactions = transactions.filter(created_at__lte=date_to)
    
    # Pagination
    paginator = Paginator(transactions, 50)
    page = request.GET.get('page', 1)
    transactions_page = paginator.get_page(page)
    
    context = {
        'transactions': transactions_page,
        'transaction_type': transaction_type,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'orders/finance/admin_transactions.html', context)


@login_required
def admin_seller_earnings_list(request):
    """
    View all seller earnings across platform.
    Staff/admin only.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    # Filters
    seller_id = request.GET.get('seller', '')
    status = request.GET.get('status', '')
    paid_status = request.GET.get('paid', '')
    
    earnings = SellerEarnings.objects.select_related(
        'seller', 'order', 'product', 'payout'
    ).order_by('-earned_date')
    
    # Apply filters
    if seller_id:
        earnings = earnings.filter(seller_id=seller_id)
    
    if status:
        earnings = earnings.filter(status=status)
    
    if paid_status == 'paid':
        earnings = earnings.filter(is_paid_out=True)
    elif paid_status == 'unpaid':
        earnings = earnings.filter(is_paid_out=False)
    
    # Calculate totals
    total_earnings = earnings.aggregate(total=Sum('net_earnings'))['total'] or 0
    unpaid_earnings = earnings.filter(is_paid_out=False).aggregate(
        total=Sum('net_earnings')
    )['total'] or 0
    
    # Pagination
    paginator = Paginator(earnings, 25)
    page = request.GET.get('page', 1)
    earnings_page = paginator.get_page(page)
    
    # Get all sellers for filter dropdown
    from django.contrib.auth import get_user_model
    User = get_user_model()
    sellers = User.objects.filter(
        earnings__isnull=False
    ).distinct().order_by('username')
    
    context = {
        'earnings': earnings_page,
        'total_earnings': total_earnings,
        'unpaid_earnings': unpaid_earnings,
        'sellers': sellers,
        'selected_seller': seller_id,
        'selected_status': status,
        'selected_paid': paid_status,
    }
    
    return render(request, 'orders/finance/admin_seller_earnings.html', context)


@login_required
def admin_payouts_list(request):
    """
    View and manage seller payouts.
    Staff/admin only.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    # Filters
    status = request.GET.get('status', '')
    seller_id = request.GET.get('seller', '')
    
    payouts = SellerPayout.objects.select_related(
        'seller', 'processed_by'
    ).prefetch_related('earnings').order_by('-created_at')
    
    # Apply filters
    if status:
        payouts = payouts.filter(status=status)
    
    if seller_id:
        payouts = payouts.filter(seller_id=seller_id)
    
    # Stats
    pending_count = SellerPayout.objects.filter(status='pending').count()
    total_paid = SellerPayout.objects.filter(status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Pagination
    paginator = Paginator(payouts, 20)
    page = request.GET.get('page', 1)
    payouts_page = paginator.get_page(page)
    
    context = {
        'payouts': payouts_page,
        'pending_count': pending_count,
        'total_paid': total_paid,
        'selected_status': status,
        'selected_seller': seller_id,
    }
    
    return render(request, 'orders/finance/admin_payouts.html', context)


@login_required
def admin_payout_detail(request, payout_id):
    """
    View payout details and process payout.
    Staff/admin only.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    payout = get_object_or_404(
        SellerPayout.objects.select_related('seller', 'processed_by').prefetch_related('earnings'),
        id=payout_id
    )
    
    # Handle payout processing
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            payout.status = 'completed'
            payout.processed_by = request.user
            payout.processed_at = timezone.now()
            payout.save()
            
            # Mark earnings as paid
            payout.earnings.update(is_paid_out=True, paid_out_date=timezone.now())
            
            messages.success(request, f"Payout {payout.payout_number} has been approved and completed.")
            
        elif action == 'reject':
            payout.status = 'failed'
            payout.failure_reason = request.POST.get('failure_reason', 'Rejected by admin')
            payout.processed_by = request.user
            payout.processed_at = timezone.now()
            payout.save()
            
            messages.warning(request, f"Payout {payout.payout_number} has been rejected.")
        
        return redirect('orders:admin-payout-detail', payout_id=payout.id)
    
    context = {
        'payout': payout,
        'earnings_list': payout.earnings.select_related('product', 'order').all(),
    }
    
    return render(request, 'orders/finance/admin_payout_detail.html', context)


@login_required
def admin_sales_analytics(request):
    """
    Advanced sales analytics for admin.
    Shows sales per product, per seller, trends, etc.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')
    
    from datetime import timedelta
    from products.models import Product
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Sales by Product
    sales_by_product = SellerEarnings.objects.filter(
        product__isnull=False
    ).values(
        'product__title', 'product__id'
    ).annotate(
        total_sales=Sum('gross_sale_amount'),
        units_sold=Count('id'),
        platform_commission=Sum('platform_commission')
    ).order_by('-total_sales')[:20]
    
    # Sales by Seller
    sales_by_seller = SellerEarnings.objects.values(
        'seller__username', 'seller__id'
    ).annotate(
        total_sales=Sum('gross_sale_amount'),
        net_earnings=Sum('net_earnings'),
        sales_count=Count('id')
    ).order_by('-total_sales')[:20]
    
    # Monthly revenue trend (last 6 months)
    from datetime import timedelta
    six_months_ago = today - timedelta(days=180)
    
    monthly_revenue = PlatformRevenue.objects.filter(
        revenue_date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('revenue_date')
    ).values('month').annotate(
        total=Sum('commission_amount')
    ).order_by('month')
    
    context = {
        'sales_by_product': sales_by_product,
        'sales_by_seller': sales_by_seller,
        'monthly_revenue': list(monthly_revenue),
    }
    
    return render(request, 'orders/finance/admin_analytics.html', context)


# SELLER FINANCE VIEWS

@login_required
def seller_finance_dashboard(request):
    """
    Seller finance dashboard showing their earnings, sales, and payouts.
    Only accessible to sellers (users with seller role).
    """
    user = request.user
    
    # Check if user is a seller or has products
    from products.models import Product
    if not Product.objects.filter(seller=user).exists():
        messages.info(request, "You don't have any products listed yet. Become a seller to access finance dashboard.")
        return redirect('products:product-create')
    
    from datetime import timedelta
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Total Earnings
    total_earnings = SellerEarnings.objects.filter(
        seller=user
    ).aggregate(total=Sum('net_earnings'))['total'] or 0
    
    # Pending Earnings (not paid out yet)
    pending_earnings = SellerEarnings.objects.filter(
        seller=user,
        is_paid_out=False,
        status='completed'
    ).aggregate(total=Sum('net_earnings'))['total'] or 0
    
    # Paid Out Earnings
    paid_earnings = SellerEarnings.objects.filter(
        seller=user,
        is_paid_out=True
    ).aggregate(total=Sum('net_earnings'))['total'] or 0
    
    # Earnings last 30 days
    earnings_30_days = SellerEarnings.objects.filter(
        seller=user,
        earned_date__gte=thirty_days_ago
    ).aggregate(total=Sum('net_earnings'))['total'] or 0
    
    # Sales Count
    total_sales = SellerEarnings.objects.filter(seller=user).count()
    
    # Recent Earnings (last 10)
    recent_earnings = SellerEarnings.objects.filter(
        seller=user
    ).select_related('product', 'order').order_by('-earned_date')[:10]
    
    # Earnings by Product
    earnings_by_product = SellerEarnings.objects.filter(
        seller=user,
        product__isnull=False
    ).values(
        'product__title', 'product__id'
    ).annotate(
        total=Sum('net_earnings'),
        sales_count=Count('id')
    ).order_by('-total')[:10]
    
    # Recent Payouts
    recent_payouts = SellerPayout.objects.filter(
        seller=user
    ).order_by('-created_at')[:5]
    
    # Daily earnings (last 30 days)
    daily_earnings = SellerEarnings.objects.filter(
        seller=user,
        earned_date__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('earned_date')
    ).values('date').annotate(
        total=Sum('net_earnings')
    ).order_by('date')
    
    context = {
        'total_earnings': total_earnings,
        'pending_earnings': pending_earnings,
        'paid_earnings': paid_earnings,
        'earnings_30_days': earnings_30_days,
        'total_sales': total_sales,
        'recent_earnings': recent_earnings,
        'earnings_by_product': earnings_by_product,
        'recent_payouts': recent_payouts,
        'daily_earnings': list(daily_earnings),
    }
    
    return render(request, 'orders/finance/seller_dashboard.html', context)


@login_required
def seller_earnings_list(request):
    """
    List all earnings for the seller with filtering.
    """
    user = request.user
    
    # Filters
    status = request.GET.get('status', '')
    product_id = request.GET.get('product', '')
    paid_status = request.GET.get('paid', '')
    
    earnings = SellerEarnings.objects.filter(
        seller=user
    ).select_related('product', 'order', 'payout').order_by('-earned_date')
    
    # Apply filters
    if status:
        earnings = earnings.filter(status=status)
    
    if product_id:
        earnings = earnings.filter(product_id=product_id)
    
    if paid_status == 'paid':
        earnings = earnings.filter(is_paid_out=True)
    elif paid_status == 'unpaid':
        earnings = earnings.filter(is_paid_out=False)
    
    # Calculate totals
    total_earnings = earnings.aggregate(total=Sum('net_earnings'))['total'] or 0
    
    # Pagination
    paginator = Paginator(earnings, 25)
    page = request.GET.get('page', 1)
    earnings_page = paginator.get_page(page)
    
    # Get seller's products for filter
    from products.models import Product
    seller_products = Product.objects.filter(seller=user).order_by('title')
    
    context = {
        'earnings': earnings_page,
        'total_earnings': total_earnings,
        'seller_products': seller_products,
        'selected_status': status,
        'selected_product': product_id,
        'selected_paid': paid_status,
    }
    
    return render(request, 'orders/finance/seller_earnings.html', context)


@login_required
def seller_payouts_list(request):
    """
    List all payouts for the seller.
    """
    user = request.user
    
    payouts = SellerPayout.objects.filter(
        seller=user
    ).prefetch_related('earnings').order_by('-created_at')
    
    # Stats
    total_received = payouts.filter(status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    pending_amount = payouts.filter(status='pending').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Pagination
    paginator = Paginator(payouts, 15)
    page = request.GET.get('page', 1)
    payouts_page = paginator.get_page(page)
    
    context = {
        'payouts': payouts_page,
        'total_received': total_received,
        'pending_amount': pending_amount,
    }
    
    return render(request, 'orders/finance/seller_payouts.html', context)


@login_required
def seller_payout_detail(request, payout_id):
    """
    View details of a specific payout.
    """
    user = request.user
    
    payout = get_object_or_404(
        SellerPayout.objects.prefetch_related('earnings__product'),
        id=payout_id,
        seller=user
    )
    
    context = {
        'payout': payout,
        'earnings_list': payout.earnings.select_related('product', 'order').all(),
    }
    
    return render(request, 'orders/finance/seller_payout_detail.html', context)


# USER FINANCE VIEWS

@login_required
def user_payment_history(request):
    """
    User's personal payment history showing all their purchases.
    """
    user = request.user
    
    # Get all wallet transactions for the user
    transactions = WalletTransaction.objects.filter(
        user=user
    ).select_related('order').order_by('-transaction_date')
    
    # Filter by type
    transaction_type = request.GET.get('type', '')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Calculate totals
    total_spent = WalletTransaction.objects.filter(
        user=user,
        transaction_type='purchase',
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_refunds = WalletTransaction.objects.filter(
        user=user,
        transaction_type='refund',
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Pagination
    paginator = Paginator(transactions, 25)
    page = request.GET.get('page', 1)
    transactions_page = paginator.get_page(page)
    
    context = {
        'transactions': transactions_page,
        'total_spent': abs(total_spent) if total_spent else 0,
        'total_refunds': total_refunds,
        'selected_type': transaction_type,
        'current_balance': user.balance,
    }
    
    return render(request, 'orders/finance/user_payment_history.html', context)


@login_required
def user_wallet(request):
    """
    User's wallet showing balance, recent transactions, and deposit/withdrawal options.
    """
    user = request.user

    # Staff should not access user-only wallet; redirect to admin finance
    if user.is_staff and not user.is_superuser:
        messages.info(request, "Staff should use Finance > Admin views.")
        return redirect('orders:admin-finance-dashboard')
    
    # Sellers should not access buyer wallet; redirect to seller finance
    if user.role == 'seller' or user.is_seller:
        messages.info(request, "Sellers should use Seller Finance Dashboard.")
        return redirect('orders:seller-finance-dashboard')
    
    from datetime import timedelta
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    
    # Get recent transactions (last 20)
    recent_transactions = WalletTransaction.objects.filter(
        user=user
    ).select_related('order').order_by('-transaction_date')[:20]
    
    # Transaction stats for last 30 days
    deposits_30d = WalletTransaction.objects.filter(
        user=user,
        transaction_type='deposit',
        transaction_date__gte=thirty_days_ago,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    purchases_30d = WalletTransaction.objects.filter(
        user=user,
        transaction_type='purchase',
        transaction_date__gte=thirty_days_ago,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Compute current balance dynamically from transactions (deposits - purchases)
    current_balance = (
        WalletTransaction.objects.filter(user=user)
        .aggregate(total=Sum('amount'))['total'] or Decimal('0')
    )

    context = {
        'current_balance': current_balance,
        'recent_transactions': recent_transactions,
        'deposits_30d': deposits_30d,
        'purchases_30d': abs(purchases_30d) if purchases_30d else 0,
    }
    
    return render(request, 'orders/finance/user_wallet.html', context)


@login_required
def user_purchased_products(request):
    """
    List all products purchased by the user.
    """
    user = request.user

    # Staff should not access user-only purchases; redirect to admin finance
    if user.is_staff and not user.is_superuser:
        messages.info(request, "Staff should use Finance > Admin views.")
        return redirect('orders:admin-finance-dashboard')
    
    # Sellers should not access buyer purchases; redirect to seller finance
    if user.role == 'seller' or user.is_seller:
        messages.info(request, "Sellers should use Seller Finance Dashboard.")
        return redirect('orders:seller-finance-dashboard')
    
    # Get all order items for this user's orders
    purchased_items = OrderItem.objects.filter(
        order__user=user
    ).select_related('order', 'product', 'product__seller', 'product__category').order_by('-order__created_at')
    
    # Pagination
    paginator = Paginator(purchased_items, 15)
    page = request.GET.get('page', 1)
    items_page = paginator.get_page(page)
    
    # Calculate stats
    total_purchased = purchased_items.count()
    active_count = purchased_items.filter(product__status='active').count()
    
    # Calculate total spent from orders (not items to avoid double counting)
    orders = Order.objects.filter(user=user)
    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'purchased_products': items_page,
        'total_purchased': total_purchased,
        'active_count': active_count,
        'total_spent': total_spent,
    }
    
    return render(request, 'orders/finance/user_purchased_products.html', context)


# =============================================================================
# STAFF FINANCE VIEWS (view specific seller/buyer)
# =============================================================================

@login_required
def staff_view_seller_finance(request, seller_id):
    """Staff view of a specific seller's earnings and payouts."""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')

    from django.contrib.auth import get_user_model
    User = get_user_model()
    seller = get_object_or_404(User, id=seller_id)

    earnings = SellerEarnings.objects.select_related('seller', 'order', 'product').filter(
        seller_id=seller_id
    ).order_by('-earned_date')

    total_earnings = earnings.aggregate(total=Sum('net_earnings'))['total'] or 0
    unpaid_earnings = earnings.filter(is_paid_out=False).aggregate(total=Sum('net_earnings'))['total'] or 0

    paginator = Paginator(earnings, 25)
    page = request.GET.get('page', 1)
    earnings_page = paginator.get_page(page)

    context = {
        'earnings': earnings_page,
        'total_earnings': total_earnings,
        'unpaid_earnings': unpaid_earnings,
        'selected_seller': str(seller_id),
        'viewing_seller': seller,
    }

    return render(request, 'orders/finance/admin_seller_earnings.html', context)


@login_required
def staff_view_buyer_finance(request, user_id):
    """Staff view of a specific buyer's wallet, transactions, and orders."""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect('home')

    from django.contrib.auth import get_user_model
    User = get_user_model()
    target_user = get_object_or_404(User, id=user_id)

    wallet_txns = WalletTransaction.objects.filter(user=target_user).order_by('-transaction_date')
    orders = Order.objects.filter(user=target_user).order_by('-created_at')

    current_balance = WalletTransaction.objects.filter(user=target_user).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0

    paginator = Paginator(wallet_txns, 25)
    page = request.GET.get('page', 1)
    txns_page = paginator.get_page(page)

    context = {
        'target_user': target_user,
        'current_balance': current_balance,
        'total_spent': total_spent,
        'transactions': txns_page,
        'orders': orders[:10],
    }

    return render(request, 'orders/finance/staff_buyer_finance.html', context)
