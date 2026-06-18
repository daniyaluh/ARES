"""
Setup realistic test data for ARES Financial System
This script creates comprehensive test data including orders, revenue, earnings, and transactions
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

# Create seller users
seller_names = [
    ('RoboTech Industries', 'robotech', 'sarah.chen@robotech.com', 'Sarah', 'Chen'),
    ('Nexus Automation', 'nexus', 'james.wright@nexus.com', 'James', 'Wright'),
    ('Titan Defense Systems', 'titan', 'maya.patel@titan.mil', 'Maya', 'Patel'),
    ('Quantum Robotics', 'quantum', 'david.kim@quantum.com', 'David', 'Kim'),
]

sellers = []
for company, username, email, first, last in seller_names:
    seller, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'is_staff': False,
            'first_name': first,
            'last_name': last,
            'role': 'seller'
        }
    )
    seller.set_password('seller123')
    seller.save()
    sellers.append(seller)
    print(f"   ✓ Seller: {username} ({company})")

# Create buyer users
buyer_names = [
    ('buyer1', 'john.doe@darpa.mil', 'John', 'Doe'),
    ('buyer2', 'alice.smith@navy.mil', 'Alice', 'Smith'),
    ('buyer3', 'bob.johnson@usaf.mil', 'Bob', 'Johnson'),
    ('buyer4', 'emma.wilson@army.mil', 'Emma', 'Wilson'),
    ('buyer5', 'michael.brown@spaceforce.mil', 'Michael', 'Brown'),
]

buyers = []
for username, email, first, last in buyer_names:
    buyer, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'is_staff': False,
            'first_name': first,
            'last_name': last,
            'role': 'user'
        }
    )
    buyer.set_password('buyer123')
    buyer.save()
    buyers.append(buyer)
    print(f"   ✓ Buyer: {username}")

# Create categories
print("\n3. Setting up product categories...")
category_names = [
    'Autonomous Ground Vehicles',
    'Aerial Drones',
    'Industrial Robots',
    'Defense Systems',
    'AI Controllers',
    'Surveillance Equipment'
]

categories = []
for name in category_names:
    cat, _ = Category.objects.get_or_create(
        name=name,
        defaults={'description': f'Advanced {name.lower()} for military and industrial use'}
    )
    categories.append(cat)
    print(f"   ✓ Category: {name}")

# Create products
print("\n4. Creating products...")
product_data = [
    ("ARES-X1 Combat Robot", 45000, "physical", "Advanced autonomous combat unit with AI targeting"),
    ("SkyGuard Surveillance Drone", 28000, "physical", "High-altitude reconnaissance drone with thermal imaging"),
    ("TitanArm Industrial Lifter", 85000, "physical", "Heavy-duty robotic arm for industrial applications"),
    ("Neural Command Interface", 12000, "digital", "AI control software for autonomous systems"),
    ("Quantum Sensor Array", 67000, "physical", "Advanced sensor package for threat detection"),
    ("AutoPatrol Security Robot", 38000, "physical", "Autonomous perimeter security system"),
    ("Phoenix Tactical Drone", 52000, "physical", "VTOL combat drone with weapon systems"),
    ("AI Vision Pro Software", 8500, "digital", "Computer vision and object recognition system"),
    ("Sentinel Defense Grid", 125000, "physical", "Automated defensive network controller"),
    ("CyberHawk Recon Drone", 34000, "physical", "Stealth reconnaissance drone"),
]

products = []
for idx, (title, price, ptype, desc) in enumerate(product_data):
    seller = sellers[idx % len(sellers)]
    category = categories[idx % len(categories)]
    
    product, _ = Product.objects.get_or_create(
        title=title,
        defaults={
            'seller': seller,
            'category': category,
            'shipping_type': ptype,
            'description': desc,
            'price': Decimal(str(price)),
            'status': 'active',
            'is_digital': True if ptype == 'digital' else False,
            'stock_quantity': 10 if ptype == 'physical' else 999
        }
    )
    products.append(product)
    print(f"   ✓ Product: {title} (${price:,})")

# Create realistic orders over the past 90 days
print("\n5. Creating orders and transactions...")
base_date = timezone.now() - timedelta(days=90)
total_orders = 50
commission_rates = [10, 12, 15, 18, 20]  # Various commission rates

for i in range(total_orders):
    buyer = random.choice(buyers)
    
    # Random date in the past 90 days
    days_ago = random.randint(0, 90)
    order_date = base_date + timedelta(days=days_ago)
    
    # Create order
    order = Order.objects.create(
        user=buyer,
        status=random.choice(['completed', 'completed', 'completed', 'pending']),
        total_amount=Decimal('0'),
        created_at=order_date,
        updated_at=order_date
    )
    
    # Add 1-3 items per order
    num_items = random.randint(1, 3)
    order_total = Decimal('0')
    
    for _ in range(num_items):
        product = random.choice(products)
        quantity = random.randint(1, 2)
        item_price = product.price * quantity
        
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )
        
        order_total += item_price
        
        # Create transaction
        transaction = Transaction.objects.create(
            order=order,
            user=buyer,
            amount=item_price,
            transaction_type='purchase',
            status='completed',
            payment_method=random.choice(['credit_card', 'bank_transfer', 'paypal']),
            created_at=order_date
        )
        
        # Create platform revenue
        commission_rate = Decimal(str(random.choice(commission_rates)))
        revenue = PlatformRevenue.objects.create(
            order=order,
            transaction=transaction,
            seller=product.seller,
            product=product,
            gross_amount=item_price,
            commission_rate=commission_rate,
            created_at=order_date
        )
        
        # Create seller earnings
        SellerEarnings.objects.create(
            seller=product.seller,
            order=order,
            transaction=transaction,
            product=product,
            gross_sale_amount=item_price,
            commission_rate=commission_rate,
            earned_date=order_date,
            is_paid_out=random.choice([True, False, False])  # Some paid, most unpaid
        )
        
        # Create wallet transaction for buyer (debit)
        WalletTransaction.objects.create(
            user=buyer,
            transaction_type='purchase',
            amount=-item_price,
            balance_after=Decimal('0'),  # Will update later
            description=f'Purchase: {product.title}',
            order=order,
            created_at=order_date
        )
    
    order.total_amount = order_total
    order.save()
    
    print(f"   ✓ Order #{order.order_number[:8]} - ${order_total:,.2f} ({num_items} items)")

# Create some payout requests
print("\n6. Creating seller payout requests...")
payout_count = 0
for seller in sellers:
    # Get unpaid earnings for this seller
    unpaid_earnings = SellerEarnings.objects.filter(
        seller=seller,
        is_paid_out=False
    )
    
    if unpaid_earnings.exists():
        # Create 1-2 payouts per seller
        num_payouts = random.randint(1, 2)
        
        for _ in range(num_payouts):
            # Take a subset of unpaid earnings
            earnings_batch = list(unpaid_earnings[:random.randint(3, 7)])
            
            if not earnings_batch:
                continue
            
            payout = SellerPayout.objects.create(
                seller=seller,
                total_amount=sum(e.net_earnings for e in earnings_batch),
                earnings_count=len(earnings_batch),
                status=random.choice(['pending', 'pending', 'completed']),
                payment_method=random.choice(['bank_transfer', 'paypal', 'crypto']),
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
            
            # Link earnings to payout
            for earning in earnings_batch:
                earning.payout = payout
                if payout.status == 'completed':
                    earning.is_paid_out = True
                earning.save()
            
            payout_count += 1
            print(f"   ✓ Payout for {seller.username}: ${payout.total_amount:,.2f} ({payout.status})")

# Add $500,000 to buyer1's wallet
print("\n7. Adding $500,000 to buyer1 wallet...")
buyer1 = User.objects.get(username='buyer1')
deposit_amount = Decimal('500000.00')

WalletTransaction.objects.create(
    user=buyer1,
    transaction_type='deposit',
    amount=deposit_amount,
    balance_after=deposit_amount,
    description='Initial wallet funding - Test deposit',
    created_at=timezone.now()
)
print(f"   ✓ Added ${deposit_amount:,.2f} to {buyer1.username}'s wallet")

# Calculate and update wallet balances
print("\n8. Calculating wallet balances...")
for user in User.objects.all():
    transactions = WalletTransaction.objects.filter(user=user).order_by('created_at')
    running_balance = Decimal('0')
    
    for txn in transactions:
        running_balance += txn.amount
        txn.balance_after = running_balance
        txn.save(update_fields=['balance_after'])
    
    if transactions.exists():
        print(f"   ✓ {user.username}: ${running_balance:,.2f}")

# Print summary
print("\n" + "=" * 70)
print("📊 TEST DATA SUMMARY")
print("=" * 70)

total_revenue = PlatformRevenue.objects.aggregate(total=django.db.models.Sum('net_commission'))['total'] or 0
total_earnings = SellerEarnings.objects.aggregate(total=django.db.models.Sum('net_earnings'))['total'] or 0
total_sales = Order.objects.filter(status='completed').count()

print(f"""
Users Created:
  • Admin: 1
  • Sellers: {len(sellers)}
  • Buyers: {len(buyers)}

Products: {Product.objects.count()}
Categories: {Category.objects.count()}

Financial Data:
  • Orders: {Order.objects.count()}
  • Completed Sales: {total_sales}
  • Platform Revenue: ${total_revenue:,.2f}
  • Seller Earnings: ${total_earnings:,.2f}
  • Payout Requests: {SellerPayout.objects.count()}
  • Wallet Transactions: {WalletTransaction.objects.count()}

Buyer1 Wallet Balance: $500,000.00

Test Accounts:
  • Admin: admin / admin123
  • Seller: robotech / seller123
  • Buyer: buyer1 / buyer123 (has $500K wallet)
""")

print("=" * 70)
print("✅ TEST DATA SETUP COMPLETE!")
print("=" * 70)
print("\nYou can now test the finance system at:")
print("  Admin Dashboard: /orders/finance/admin/dashboard/")
print("  Seller Dashboard: /orders/finance/seller/dashboard/")
print("  User Wallet: /orders/finance/user/wallet/")
print("\n🚀 Start server with: python manage.py runserver")
print("=" * 70)
