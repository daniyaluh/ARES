"""
Full System Check Script for ARES Project
"""
import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'ares_project.settings'

import django
django.setup()

from django.db.models import Count
from django.template import engines
from django.template.loader import get_template
from django.conf import settings
from users.models import CustomUser as User, Notification
from products.models import Robot, Category
from orders.models import PurchaseRequest, Invoice
from verification.models import VerificationRequest, IdentityDocument, ExportLicense
from collections import Counter
import glob

def check_duplicates():
    print("=" * 60)
    print("DUPLICATE CHECK")
    print("=" * 60)
    
    # Users with duplicate emails
    dup_emails = User.objects.values('email').annotate(cnt=Count('id')).filter(cnt__gt=1)
    if dup_emails.exists():
        print(f"⚠️  Duplicate emails found: {list(dup_emails)}")
    else:
        print("✅ No duplicate emails")
    
    # Duplicate categories
    dup_cats = Category.objects.values('name').annotate(cnt=Count('id')).filter(cnt__gt=1)
    if dup_cats.exists():
        print(f"⚠️  Duplicate categories: {list(dup_cats)}")
    else:
        print("✅ No duplicate categories")
    
    # Duplicate invoices for same purchase request
    dup_invoices = Invoice.objects.values('purchase_request').annotate(cnt=Count('id')).filter(cnt__gt=1, purchase_request__isnull=False)
    if dup_invoices.exists():
        print(f"⚠️  Multiple invoices for same request: {dup_invoices.count()}")
    else:
        print("✅ No duplicate invoices per purchase request")

def check_orphans():
    print("\n" + "=" * 60)
    print("ORPHANED RECORDS CHECK")
    print("=" * 60)
    
    # Invoices without created_by
    orphan_invoices = Invoice.objects.filter(created_by__isnull=True).count()
    print(f"{'⚠️ ' if orphan_invoices > 0 else '✅ '}Invoices without creator: {orphan_invoices}")
    
    # Purchase requests without user
    orphan_pr = PurchaseRequest.objects.filter(user__isnull=True).count()
    print(f"{'⚠️ ' if orphan_pr > 0 else '✅ '}Purchase requests without user: {orphan_pr}")
    
    # Products without category (Robot uses product.category)
    from products.models import Product
    orphan_products = Product.objects.filter(category__isnull=True).count()
    print(f"{'⚠️ ' if orphan_products > 0 else '✅ '}Products without category: {orphan_products}")
    
    # Notifications without user
    orphan_notif = Notification.objects.filter(user__isnull=True).count()
    print(f"{'⚠️ ' if orphan_notif > 0 else '✅ '}Notifications without user: {orphan_notif}")

def check_user_types():
    print("\n" + "=" * 60)
    print("USER ROLES & PERMISSIONS")
    print("=" * 60)
    
    superusers = User.objects.filter(is_superuser=True)
    staff = User.objects.filter(is_staff=True, is_superuser=False)
    regular = User.objects.filter(is_staff=False, is_superuser=False)
    verified = User.objects.filter(is_verified=True)
    
    print(f"👑 Superusers (Admin): {superusers.count()}")
    for u in superusers:
        print(f"   - {u.username} ({u.email})")
    
    print(f"👔 Staff Users: {staff.count()}")
    for u in staff:
        print(f"   - {u.username} (verified: {u.is_verified})")
    
    print(f"👤 Regular Users: {regular.count()}")
    print(f"✓  Verified Users Total: {verified.count()}")

def check_database_counts():
    print("\n" + "=" * 60)
    print("DATABASE SUMMARY")
    print("=" * 60)
    
    print(f"Users: {User.objects.count()}")
    print(f"Robots: {Robot.objects.count()}")
    print(f"Categories: {Category.objects.count()}")
    print(f"Purchase Requests: {PurchaseRequest.objects.count()}")
    print(f"  - Pending: {PurchaseRequest.objects.filter(status='pending').count()}")
    print(f"  - Approved: {PurchaseRequest.objects.filter(status='approved').count()}")
    print(f"  - Rejected: {PurchaseRequest.objects.filter(status='rejected').count()}")
    print(f"Invoices: {Invoice.objects.count()}")
    print(f"  - Draft: {Invoice.objects.filter(status='draft').count()}")
    print(f"  - Issued: {Invoice.objects.filter(status='issued').count()}")
    print(f"  - Sent: {Invoice.objects.filter(status='sent').count()}")
    print(f"  - Paid: {Invoice.objects.filter(status='paid').count()}")
    print(f"  - Overdue: {Invoice.objects.filter(status='overdue').count()}")
    print(f"  - Cancelled: {Invoice.objects.filter(status='cancelled').count()}")
    print(f"Export Licenses: {ExportLicense.objects.count()}")
    print(f"Notifications: {Notification.objects.count()}")

def check_notification_types():
    print("\n" + "=" * 60)
    print("NOTIFICATION TYPES DISTRIBUTION")
    print("=" * 60)
    
    notif_types = Counter(Notification.objects.values_list('notification_type', flat=True))
    if notif_types:
        for t, c in sorted(notif_types.items()):
            print(f"  {t}: {c}")
    else:
        print("  No notifications yet")

def check_templates():
    print("\n" + "=" * 60)
    print("TEMPLATE VALIDATION")
    print("=" * 60)
    
    template_dir = os.path.join(settings.BASE_DIR, 'templates')
    html_files = []
    for root, dirs, files in os.walk(template_dir):
        for f in files:
            if f.endswith('.html'):
                rel_path = os.path.relpath(os.path.join(root, f), template_dir)
                html_files.append(rel_path)
    
    errors = []
    for tmpl in html_files:
        try:
            get_template(tmpl)
        except Exception as e:
            errors.append((tmpl, str(e)))
    
    if errors:
        print(f"⚠️  {len(errors)} template errors found:")
        for tmpl, err in errors:
            print(f"   - {tmpl}: {err[:100]}")
    else:
        print(f"✅ All {len(html_files)} templates load successfully")

def check_model_integrity():
    print("\n" + "=" * 60)
    print("MODEL FIELD VALIDATION")
    print("=" * 60)
    
    # Check Invoice model has required fields
    from orders.models import Invoice
    invoice_fields = [f.name for f in Invoice._meta.get_fields()]
    # Invoice uses purchase_request.user or order.user, not direct user field
    required_invoice = ['status', 'purchase_request', 'total_amount', 'created_at']
    missing = [f for f in required_invoice if f not in invoice_fields]
    if missing:
        print(f"⚠️  Invoice missing fields: {missing}")
    else:
        print("✅ Invoice model has all required fields")
    
    # Check Notification model
    from users.models import Notification
    notif_fields = [f.name for f in Notification._meta.get_fields()]
    required_notif = ['user', 'title', 'message', 'notification_type', 'is_read']
    missing_notif = [f for f in required_notif if f not in notif_fields]
    if missing_notif:
        print(f"⚠️  Notification missing fields: {missing_notif}")
    else:
        print("✅ Notification model has all required fields")

def check_views_for_errors():
    print("\n" + "=" * 60)
    print("VIEWS SYNTAX CHECK")  
    print("=" * 60)
    
    view_modules = [
        'users.views',
        'products.views', 
        'orders.views',
        'verification.views',
        'analytics.views',
        'support.views',
    ]
    
    for module in view_modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except Exception as e:
            print(f"⚠️  {module} - ERROR: {e}")

def check_url_patterns():
    print("\n" + "=" * 60)
    print("URL PATTERNS CHECK")
    print("=" * 60)
    
    from django.urls import get_resolver
    resolver = get_resolver()
    
    url_count = len(resolver.url_patterns)
    print(f"✅ Main URL patterns loaded: {url_count}")
    
    # Check included URL patterns
    app_urls = ['users', 'products', 'orders', 'verification', 'analytics', 'support']
    for app in app_urls:
        try:
            __import__(f'{app}.urls')
            print(f"   ✅ {app}.urls loaded")
        except Exception as e:
            print(f"   ⚠️  {app}.urls error: {e}")

def check_military_license_logic():
    print("\n" + "=" * 60)
    print("MILITARY/RESTRICTED PRODUCT LICENSE CHECK")
    print("=" * 60)
    
    # Get military robots through product.category - include all military-related categories
    try:
        from products.models import Product
        from django.db.models import Q
        
        # Check for military/defense related categories
        military_cats = Category.objects.filter(
            Q(name__icontains='military') | 
            Q(name__icontains='defense') | 
            Q(name__icontains='war') |
            Q(name__icontains='combat')
        )
        
        if military_cats.exists():
            print(f"Military/Defense categories found: {military_cats.count()}")
            for cat in military_cats:
                products = Product.objects.filter(category=cat)
                robots = Robot.objects.filter(product__in=products)
                print(f"  {cat.name}: {robots.count()} robots")
                
            # Get all military robots
            all_mil_products = Product.objects.filter(category__in=military_cats)
            all_mil_robots = Robot.objects.filter(product__in=all_mil_products)
            
            # Check required_license distribution for all
            license_dist = Counter(all_mil_robots.values_list('required_license', flat=True))
            print(f"\nTotal military robots: {all_mil_robots.count()}")
            print("Required license distribution:")
            for lic, cnt in sorted(license_dist.items(), key=lambda x: -x[1]):
                print(f"  {lic or 'none'}: {cnt}")
        else:
            print("No military/defense categories found")
    except Exception as e:
        print(f"Error checking military: {e}")

def run_all_checks():
    print("\n" + "=" * 60)
    print("       ARES SYSTEM CHECK - FULL REPORT")
    print("=" * 60)
    
    check_database_counts()
    check_duplicates()
    check_orphans()
    check_user_types()
    check_notification_types()
    check_views_for_errors()
    check_url_patterns()
    check_templates()
    check_model_integrity()
    check_military_license_logic()
    
    print("\n" + "=" * 60)
    print("       SYSTEM CHECK COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    run_all_checks()
