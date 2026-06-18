"""
Clear all transaction and order data for testing.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ares_project.settings')
django.setup()

from orders.models import (
    WalletTransaction, SellerPayout, SellerEarnings, 
    PlatformRevenue, Transaction, OrderItem, Order,
    PurchaseRequest, PurchaseRequestLog, Invoice
)

print("=" * 70)
print("🧹 CLEARING ALL TRANSACTION DATA")
print("=" * 70)

# Clear all financial and order data
print("\n1. Clearing wallet transactions...")
count = WalletTransaction.objects.all().delete()[0]
print(f"   ✓ Deleted {count} wallet transactions")

print("\n2. Clearing seller payouts...")
count = SellerPayout.objects.all().delete()[0]
print(f"   ✓ Deleted {count} seller payouts")

print("\n3. Clearing seller earnings...")
count = SellerEarnings.objects.all().delete()[0]
print(f"   ✓ Deleted {count} seller earnings")

print("\n4. Clearing platform revenue...")
count = PlatformRevenue.objects.all().delete()[0]
print(f"   ✓ Deleted {count} platform revenue records")

print("\n5. Clearing invoices...")
count = Invoice.objects.all().delete()[0]
print(f"   ✓ Deleted {count} invoices")

print("\n6. Clearing purchase request logs...")
count = PurchaseRequestLog.objects.all().delete()[0]
print(f"   ✓ Deleted {count} purchase request logs")

print("\n7. Clearing purchase requests...")
count = PurchaseRequest.objects.all().delete()[0]
print(f"   ✓ Deleted {count} purchase requests")

print("\n8. Clearing transactions...")
count = Transaction.objects.all().delete()[0]
print(f"   ✓ Deleted {count} transactions")

print("\n9. Clearing order items...")
count = OrderItem.objects.all().delete()[0]
print(f"   ✓ Deleted {count} order items")

print("\n10. Clearing orders...")
count = Order.objects.all().delete()[0]
print(f"   ✓ Deleted {count} orders")

print("\n" + "=" * 70)
print("✅ ALL DATA CLEARED SUCCESSFULLY!")
print("=" * 70)
print("\nYou can now test the purchase request approval flow from scratch.")
print("All user wallet balances have been reset to $0.")
