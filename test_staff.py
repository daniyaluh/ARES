"""
Test script for staff dashboard functionality.
"""
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ares_project.settings')

import django
django.setup()

from users.models import CustomUser
from products.models import Product, Robot
from verification.models import VerificationRequest, ExportLicense
from orders.models import PurchaseRequest
from django.urls import reverse

print("=" * 60)
print("STAFF DASHBOARD TESTING SCRIPT")
print("=" * 60)

# 1. Check staff user
print("\n=== 1. STAFF USER DETAILS ===")
try:
    staff = CustomUser.objects.get(username='staff')
    print(f"Username: {staff.username}")
    print(f"Email: {staff.email}")
    print(f"Role: {staff.role}")
    print(f"is_staff: {staff.is_staff}")
    print(f"Access Level: {staff.access_level}")
    print(f"Can Approve Sellers: {staff.can_approve_sellers}")
    print(f"Can Approve Products: {staff.can_approve_products}")
    print(f"Permissions count: {staff.user_permissions.count()}")
except Exception as e:
    print(f"ERROR: {e}")

# 2. Check URLs
print("\n=== 2. URL RESOLUTION ===")
urls_to_check = [
    'users:staff-dashboard',
    'users:staff-pending-products',
    'users:staff-pending-sellers',
    'verification:review-list',
    'verification:license-list',
]
for url_name in urls_to_check:
    try:
        url = reverse(url_name)
        print(f"OK: {url_name} -> {url}")
    except Exception as e:
        print(f"ERROR: {url_name} -> {e}")

# 3. Check pending items counts
print("\n=== 3. PENDING ITEMS ===")
try:
    pending_products = Product.objects.filter(status='pending').count()
    print(f"Pending Products: {pending_products}")
    
    pending_sellers = CustomUser.objects.filter(role='seller', is_seller_approved=False).count()
    print(f"Pending Sellers: {pending_sellers}")
    
    pending_verifications = VerificationRequest.objects.filter(status__in=['pending', 'under_review']).count()
    print(f"Pending Verifications: {pending_verifications}")
    
    pending_licenses = ExportLicense.objects.filter(status__in=['pending', 'under_review']).count()
    print(f"Pending Licenses: {pending_licenses}")
    
    pending_orders = PurchaseRequest.objects.filter(status='pending').count()
    print(f"Pending Orders: {pending_orders}")
except Exception as e:
    print(f"ERROR: {e}")

# 4. List products that can be reviewed
print("\n=== 4. PRODUCTS FOR REVIEW ===")
try:
    products = Product.objects.filter(status='pending')[:5]
    if products:
        for p in products:
            print(f"  - {p.title} (ID: {p.id}) by {p.seller}")
    else:
        print("  No pending products")
except Exception as e:
    print(f"ERROR: {e}")

# 5. Check all users who need seller approval
print("\n=== 5. SELLERS PENDING APPROVAL ===")
try:
    sellers = CustomUser.objects.filter(role='seller', is_seller_approved=False)[:5]
    if sellers:
        for s in sellers:
            print(f"  - {s.username} ({s.email})")
    else:
        print("  No pending seller applications")
except Exception as e:
    print(f"ERROR: {e}")

# 6. Test product approval flow
print("\n=== 6. PRODUCT APPROVAL TEST ===")
try:
    product = Product.objects.filter(status='pending').first()
    if product:
        print(f"Test product: {product.title}")
        print(f"Current status: {product.status}")
        print(f"Seller: {product.seller}")
        # Don't actually approve, just check we can access it
        review_url = reverse('users:staff-review-product', kwargs={'product_id': product.id})
        print(f"Review URL: {review_url}")
    else:
        print("No pending products to test")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
