import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ares_project.settings')
django.setup()

from users.models import CustomUser

# Update admin password
try:
    admin = CustomUser.objects.get(email='admin@ares.mil')
    admin.set_password('admin1234')
    admin.save()
    print(f"✅ Password updated for {admin.email} ({admin.username})")
except CustomUser.DoesNotExist:
    print("❌ Admin user with email admin@ares.mil not found")
