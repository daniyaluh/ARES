"""
Simplified test data setup for ARES Financial System
Works with actual model structure
"""

import os
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ares_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from orders.models import (
    Order, OrderItem, Transaction, PlatformRevenue, 
    SellerEarnings, SellerPayout, WalletTransaction
)
from products.models import Product, Category
from django.db import transaction as db_transaction

User = get_user_model()

print("=" * 70)
print("🧹 CLEARING PREVIOUS DATA")
print("=" * 70)

# Clear all financial data
print("\n1. Clearing transactions and invoices...")
WalletTransaction.objects.all().delete()
SellerPayout.objects.all().delete()
SellerEarnings.objects.all().delete()
PlatformRevenue.objects.all().delete()
Transaction.objects.all().delete()
OrderItem.objects.all().delete()
Order.objects.all().delete()
print("   ✓ All previous transactions and invoices cleared!")

print("\n" + "=" * 70)
print("🏗️  CREATING TEST DATA")
print("=" * 70)

# Get or create test users
print("\n2. Setting up users...")
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@ares.mil',
        'is_staff': True,
        'is_superuser': True,
        'first_name': 'System',
        'last_name': 'Administrator'
    }
)
admin_user.set_password('admin123')
admin_user.save()
print(f"   ✓ Admin: {admin_user.username}")

# Create test sellers and buyers
# Get existing seller
seller1 = User.objects.filter(role='seller').first()
if not seller1:
    seller1, _ = User.objects.get_or_create(
        username='seller1',
        defaults={
            'email': 'seller1@ares.com',
            'first_name': 'Sarah',
            'last_name': 'Chen',
            'role': 'seller'
        }
    )
    seller1.set_password('seller123')
    seller1.save()
print(f"   ✓ Using seller: {seller1.username}")

# Use existing user account
try:
    buyer1 = User.objects.get(email='user@ares.com')
    print(f"   ✓ Using existing user: {buyer1.username} ({buyer1.email})")
except User.DoesNotExist:
    print(f"   ⚠ User with email 'user@ares.com' not found, using any regular user")
    buyer1 = User.objects.filter(role='buyer').first()
    if not buyer1:
        buyer1 = User.objects.filter(is_staff=False, is_superuser=False).first()
    print(f"   ✓ Using user: {buyer1.username} (will get $500K wallet)")

# Find or create some products
print("\n3. Finding products...")
products = list(Product.objects.filter(status='active')[:10])
if not products:
    print("   ⚠ No active products found. Please create some products first.")
    print("   Creating sample products...")
    
    category, _ = Category.objects.get_or_create(
        name='Defense Systems',
        defaults={'description': 'Military and defense equipment'}
    )
    
    for i in range(5):
        product, _ = Product.objects.get_or_create(
            title=f'Test Product {i+1}',
            defaults={
                'seller': seller1,
                'category': category,
                'shipping_type': 'digital',
                'description': f'Test product for financial system demo',
                'price': Decimal(str(random.randint(10000, 100000))),
                'status': 'active',
                'is_digital': True,
                'stock_quantity': 999
            }
        )
        products.append(product)
        print(f"   ✓ Created product: {product.title}")
else:
    print(f"   ✓ Found {len(products)} products")

# Add $500,000 to buyer1's wallet FIRST
print("\n4. Adding $500,000 to buyer1 wallet...")
deposit_amount = Decimal('500000.00')

WalletTransaction.objects.create(
    user=buyer1,
    transaction_type='deposit',
    amount=deposit_amount,
    balance_before=Decimal('0'),
    balance_after=deposit_amount,
    description='Initial wallet funding - Military Contract Payment',
    status='completed'
)
print(f"   ✓ Added ${deposit_amount:,.2f} to {buyer1.username}'s wallet")

# Create realistic orders
print("\n5. Creating orders and transactions...")
base_date = timezone.now() - timedelta(days=90)
commission_rates = [10, 12, 15, 18, 20]

for i in range(30):
    # Random date in past 90 days
    days_ago = random.randint(0, 90)
    order_date = base_date + timedelta(days=days_ago)
    
    # Select random product
    product = random.choice(products)
    quantity = random.randint(1, 2)
    item_price = product.price * quantity
    
    # Generate unique order number
    order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{i+1:04d}"
    
    # Create order
    order = Order.objects.create(
        user=buyer1,
        order_number=order_number,
        status='completed',
        total_amount=item_price,
        created_at=order_date,
        updated_at=order_date
    )
    
    # Create order item
    order_item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        price=product.price
    )
    
    # Create transaction
    transaction = Transaction.objects.create(
        order=order,
        amount=item_price,
        transaction_type='purchase'
    )
    # Update created_at manually
    transaction.created_at = order_date
    transaction.save()
    
    # Create platform revenue
    commission_rate = Decimal(str(random.choice(commission_rates)))
    commission_amount = (item_price * commission_rate) / 100
    revenue = PlatformRevenue.objects.create(
        order=order,
        transaction=transaction,
        seller=product.seller,
        gross_amount=item_price,
        commission_rate=commission_rate,
        commission_amount=commission_amount
    )
    revenue.revenue_date = order_date
    revenue.save()
    
    # Create seller earnings
    platform_commission = commission_amount
    net_earnings = item_price - platform_commission
    earning = SellerEarnings.objects.create(
        seller=product.seller,
        order=order,
        transaction=transaction,
        product=product,
        gross_sale_amount=item_price,
        platform_commission=platform_commission,
        net_earnings=net_earnings,
        is_paid_out=random.choice([True, False, False])
    )
    earning.earned_date = order_date
    earning.save()
    
    # Create wallet transaction for buyer (debit)
    # Calculate current balance
    prev_balance = WalletTransaction.objects.filter(user=buyer1).order_by('-created_at').first()
    balance_before = prev_balance.balance_after if prev_balance else Decimal('0')
    
    wallet_txn = WalletTransaction.objects.create(
        user=buyer1,
        transaction_type='purchase',
        amount=-item_price,
        balance_before=balance_before,
        balance_after=balance_before - item_price,
        description=f'Purchase: {product.title}',
        order=order,
        status='completed'
    )
    wallet_txn.created_at = order_date
    wallet_txn.save()
    
    print(f"   ✓ Order #{order.order_number[:8]}... - ${item_price:,.2f}")

# Create payout requests
print("\n6. Creating payout requests...")
unpaid_earnings = SellerEarnings.objects.filter(
    seller=seller1,
    is_paid_out=False
)

if unpaid_earnings.exists():
    # Create 2 payouts
    for p in range(2):
        earnings_batch = list(unpaid_earnings[p*3:(p+1)*5])
        if not earnings_batch:
            continue
            
        payout = SellerPayout.objects.create(
            seller=seller1,
            total_amount=sum(e.net_earnings for e in earnings_batch),
            earnings_count=len(earnings_batch),
            status=random.choice(['pending', 'completed']),
            payment_method='bank_transfer',
            created_at=timezone.now() - timedelta(days=random.randint(1, 20))
        )
        
        for earning in earnings_batch:
            earning.payout = payout
            if payout.status == 'completed':
                earning.is_paid_out = True
            earning.save()
        
        print(f"   ✓ Payout #{payout.payout_number[:8]}... - ${payout.total_amount:,.2f} ({payout.status})")

# Print summary
print("\n" + "=" * 70)
print("📊 TEST DATA SUMMARY")
print("=" * 70)

from django.db.models import Sum
total_revenue = PlatformRevenue.objects.aggregate(total=Sum('commission_amount'))['total'] or 0
total_earnings = SellerEarnings.objects.aggregate(total=Sum('net_earnings'))['total'] or 0
total_sales = Order.objects.filter(status='completed').count()
buyer1_balance = WalletTransaction.objects.filter(user=buyer1).aggregate(total=Sum('amount'))['total'] or 0

print(f"""
Users:
  • Admin: admin / admin123
  • Seller: {seller1.username} / seller123
  • User: {buyer1.username} ({buyer1.email}) - has $500K wallet

Products: {len(products)}

Financial Data:
  • Total Orders: {Order.objects.count()}
  • Completed Sales: {total_sales}
  • Platform Revenue: ${total_revenue:,.2f}
  • Seller Earnings: ${total_earnings:,.2f}
  • Payout Requests: {SellerPayout.objects.count()}
  • Wallet Transactions: {WalletTransaction.objects.count()}

Buyer1 Wallet Balance: ${buyer1_balance:,.2f}
""")

print("=" * 70)
print("✅ TEST DATA SETUP COMPLETE!")
print("=" * 70)
print("\n🌐 Access the Finance System:")
print("  Admin Dashboard:  /orders/finance/admin/dashboard/")
print("  Revenue List:     /orders/finance/admin/revenue/")
print("  Seller Dashboard: /orders/finance/seller/dashboard/")
print("  User Wallet:      /orders/finance/user/wallet/")
print("\n🚀 Server is already running at http://127.0.0.1:8000/")
print("=" * 70)
