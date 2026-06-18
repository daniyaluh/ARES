"""
User views for ARES platform.
"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

User = get_user_model()
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationPreference
import pyotp
import qrcode
import io
import base64
from .auth_utils import generate_backup_codes, generate_sms_code, generate_email_code, hash_code


def create_user_session(request, user):
    """
    Create a UserSession record when a user logs in.
    Tracks the session for the Active Sessions page.
    """
    from .models import UserSession
    from datetime import timedelta
    import re
    
    # Get IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
    
    # Get user agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Parse user agent for device, browser, OS info
    device_type = 'Desktop'
    browser = 'Unknown'
    os = 'Unknown'
    
    # Simple user agent parsing
    ua_lower = user_agent.lower()
    
    # Detect device type
    if 'mobile' in ua_lower or 'android' in ua_lower and 'mobile' in ua_lower:
        device_type = 'Mobile'
    elif 'tablet' in ua_lower or 'ipad' in ua_lower:
        device_type = 'Tablet'
    
    # Detect browser
    if 'edg/' in ua_lower or 'edge/' in ua_lower:
        browser = 'Microsoft Edge'
    elif 'chrome/' in ua_lower and 'safari/' in ua_lower:
        browser = 'Chrome'
    elif 'firefox/' in ua_lower:
        browser = 'Firefox'
    elif 'safari/' in ua_lower and 'chrome/' not in ua_lower:
        browser = 'Safari'
    elif 'opera' in ua_lower or 'opr/' in ua_lower:
        browser = 'Opera'
    elif 'msie' in ua_lower or 'trident/' in ua_lower:
        browser = 'Internet Explorer'
    
    # Detect OS
    if 'windows nt 10' in ua_lower:
        os = 'Windows 10/11'
    elif 'windows nt' in ua_lower:
        os = 'Windows'
    elif 'mac os x' in ua_lower:
        os = 'macOS'
    elif 'linux' in ua_lower:
        os = 'Linux'
    elif 'android' in ua_lower:
        os = 'Android'
    elif 'iphone' in ua_lower or 'ipad' in ua_lower:
        os = 'iOS'
    
    # Get session key (ensure session exists)
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    
    # Calculate session expiry (default 2 weeks)
    expires_at = timezone.now() + timedelta(days=14)
    
    # Check if session already exists and update it, or create new
    session, created = UserSession.objects.update_or_create(
        session_key=session_key,
        defaults={
            'user': user,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'device_type': device_type,
            'browser': browser,
            'os': os,
            'is_active': True,
            'expires_at': expires_at,
            'last_activity': timezone.now(),
        }
    )
    
    return session


# Notification views
@login_required
def notification_list(request):
    """Get list of notifications for current user."""
    notifications = request.user.notifications.all()[:20]  # Latest 20
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request - return JSON
        return JsonResponse({
            'notifications': [
                {
                    'id': str(n.id),
                    'title': n.title,
                    'message': n.message,
                    'type': n.notification_type,
                    'is_read': n.is_read,
                    'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
                }
                for n in notifications
            ],
            'unread_count': unread_count
        })
    
    return render(request, 'users/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })


@login_required
def notification_mark_read(request, notification_id):
    """Mark a notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('users:notification-list')


@login_required
def notification_mark_all_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, "All notifications marked as read.")
    return redirect('users:notification-list')


@login_required
def notification_preferences(request):
    """Notification preferences view."""
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
    return render(request, 'users/notification_preferences.html', {'prefs': prefs})


@login_required
def notification_preferences_update(request):
    """Update notification preferences."""
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update preferences from POST data
        for field in NotificationPreference._meta.fields:
            if field.name not in ['id', 'user', 'created_at', 'updated_at']:
                if field.name in request.POST:
                    setattr(prefs, field.name, request.POST.get(field.name) == 'on')
        prefs.save()
        messages.success(request, "Notification preferences updated.")
        return redirect('users:notification-preferences')
    
    return render(request, 'users/notification_preferences.html', {'prefs': prefs})


# Authentication views
def login_view(request):
    """User login view with 2FA support."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        # Check if this is a 2FA verification step
        if 'two_factor_code' in request.POST:
            # 2FA verification step
            user_id = request.session.get('2fa_user_id')
            code = request.POST.get('two_factor_code', '').strip()
            
            if not user_id or not code:
                messages.error(request, "Invalid verification request.")
                return render(request, 'users/login_2fa.html', {'error': 'Invalid code'})
            
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                messages.error(request, "Invalid verification request.")
                return render(request, 'users/login_2fa.html', {'error': 'Invalid user'})
            
            # Verify 2FA code
            from .two_factor_utils import verify_2fa_code
            success, security_key, method = verify_2fa_code(user, code, purpose='2fa')
            
            if success:
                # Clear 2FA session
                request.session.pop('2fa_user_id', None)
                request.session.pop('2fa_required', None)
                
                # Complete login
                login(request, user)
                
                # Create session tracking record
                create_user_session(request, user)
                
                messages.success(request, f"Welcome back, {user.username}!")
                next_url = request.GET.get('next', None)
                if next_url:
                    return redirect(next_url)
                elif user.is_superuser:
                    return redirect('admin:index')
                elif user.is_staff:
                    return redirect('users:staff-dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Invalid verification code. Please try again.")
                return render(request, 'users/login_2fa.html', {
                    'user': user,
                    'error': 'Invalid code'
                })
        
        # Regular login step
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, "Please provide both email and password.")
            return render(request, 'users/login.html')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                # Check if 2FA is required
                from .two_factor_utils import requires_2fa, get_primary_2fa_method
                
                if requires_2fa(user):
                    # Store user ID in session for 2FA verification
                    request.session['2fa_user_id'] = str(user.id)
                    request.session['2fa_required'] = True
                    method = get_primary_2fa_method(user)
                    
                    # If email method, generate and display code
                    email_code = None
                    if method == 'email':
                        from .email_verification_service import generate_and_send_email_code
                        code, sent, message = generate_and_send_email_code(user, purpose='2fa')
                        if sent:
                            # Store code for display in development mode
                            email_code = code if settings.DEBUG else None
                            if settings.DEBUG:
                                messages.info(request, f"Email verification code generated (Development mode - check code below)")
                            else:
                                messages.info(request, f"Verification code sent to {user.email}")
                    
                    messages.info(request, "Please enter your 2FA verification code to complete login.")
                    return render(request, 'users/login_2fa.html', {
                        'user': user,
                        'method': method,
                        'email_code': email_code
                    })
                else:
                    # No 2FA required, login directly
                    login(request, user)
                    
                    # Create session tracking record
                    create_user_session(request, user)
                    
                    messages.success(request, f"Welcome back, {user.username}!")
                    next_url = request.GET.get('next', None)
                    if next_url:
                        return redirect(next_url)
                    elif user.is_superuser:
                        return redirect('admin:index')
                    elif user.is_staff:
                        return redirect('users:staff-dashboard')
                    else:
                        return redirect('home')
            else:
                messages.error(request, "Your account has been disabled.")
        else:
            messages.error(request, "Invalid email or password.")
    
    return render(request, 'users/login.html')


def login_2fa_view(request):
    """2FA verification view (redirects to login if not in 2FA flow)."""
    if request.user.is_authenticated:
        return redirect('home')
    
    # Check if user is in 2FA flow
    if '2fa_user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('users:login')
    
    if request.method == 'POST':
        return login_view(request)  # Use the login view's 2FA handling
    
    from .two_factor_utils import get_primary_2fa_method
    try:
        user = User.objects.get(id=request.session.get('2fa_user_id'))
        method = get_primary_2fa_method(user)
        
        # If email method, generate and display code
        email_code = None
        if method == 'email':
            from .email_verification_service import generate_and_send_email_code
            code, sent, message = generate_and_send_email_code(user, purpose='2fa')
            if sent:
                # Store code for display in development mode
                email_code = code if settings.DEBUG else None
                if settings.DEBUG:
                    messages.info(request, f"Email verification code generated (Development mode - check code below)")
                else:
                    messages.info(request, f"Verification code sent to {user.email}")
        
        return render(request, 'users/login_2fa.html', {
            'user': user,
            'method': method,
            'email_code': email_code
        })
    except User.DoesNotExist:
        messages.error(request, "Invalid session.")
        return redirect('users:login')


def logout_view(request):
    """User logout view."""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out successfully.")
    return redirect('home')


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        # Basic registration logic - can be expanded
        messages.info(request, "Registration functionality coming soon.")
        return redirect('users:login')
    
    return render(request, 'users/register.html')


def password_reset_view(request):
    """Password reset view."""
    return render(request, 'users/password_reset.html')


def password_reset_confirm_view(request, token):
    """Password reset confirm view."""
    return render(request, 'users/password_reset_confirm.html')


@login_required
def profile_detail(request):
    """User profile detail view."""
    from verification.utils import get_user_clearance
    from verification.models import VerificationRequest, ExportLicense
    
    user = request.user
    user_clearance = get_user_clearance(user)
    
    # Get pending verification requests
    pending_requests = VerificationRequest.objects.filter(
        user=user,
        status__in=['pending', 'under_review']
    ).select_related('requested_clearance').order_by('-submitted_at')[:5]
    
    # Get export licenses
    all_licenses = ExportLicense.objects.filter(user=user).order_by('-created_at')
    valid_licenses = [l for l in all_licenses if l.is_valid]
    pending_licenses = ExportLicense.objects.filter(
        user=user,
        status__in=['pending', 'under_review', 'additional_info_required']
    ).order_by('-created_at')[:5]
    
    # Check if clearance is expired or expiring soon
    clearance_expiring_soon = False
    clearance_expired = False
    if user_clearance:
        approved_request = VerificationRequest.objects.filter(
            user=user,
            status='approved',
            current_clearance=user_clearance
        ).order_by('-reviewed_at').first()
        
        if approved_request and approved_request.expires_at:
            days_until_expiry = (approved_request.expires_at - timezone.now()).days
            if days_until_expiry < 0:
                clearance_expired = True
            elif days_until_expiry <= 30:
                clearance_expiring_soon = True
    
    # Determine if user should be considered verified based on clearance
    # If user has an active clearance level, they are effectively verified
    is_effectively_verified = user.is_verified or (user_clearance is not None)
    
    context = {
        'user': user,
        'user_clearance': user_clearance,
        'pending_requests': pending_requests,
        'clearance_expiring_soon': clearance_expiring_soon,
        'clearance_expired': clearance_expired,
        'is_effectively_verified': is_effectively_verified,
        'valid_licenses': valid_licenses,
        'pending_licenses': pending_licenses,
        'has_valid_license': len(valid_licenses) > 0,
    }
    
    return render(request, 'users/profile_detail.html', context)


@login_required
def profile_update(request):
    """User profile update view."""
    user = request.user
    
    if request.method == 'POST':
        # Update user fields
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.display_name = request.POST.get('display_name', '').strip()
        user.phone_number = request.POST.get('phone_number', '').strip()
        user.bio = request.POST.get('bio', '').strip()
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        # Determine which fields to update
        update_fields = ['first_name', 'last_name', 'display_name', 'phone_number', 'bio', 'updated_at']
        if 'avatar' in request.FILES:
            update_fields.append('avatar')
        
        user.save(update_fields=update_fields)
        
        # Refresh user object from database to get updated avatar URL
        user.refresh_from_db()
        
        # Update profile last_update timestamp if profile exists
        if hasattr(user, 'profile'):
            from django.utils import timezone
            user.profile.last_profile_update = timezone.now()
            user.profile.save(update_fields=['last_profile_update'])
        
        messages.success(request, "Profile updated successfully.")
        return redirect('users:profile')
    
    return render(request, 'users/profile_edit.html', {'user': user})


def get_location_from_ip(ip_address):
    """
    Get country and city from IP address using free ip-api.com service.
    Returns dict with country, country_code, city, timezone.
    """
    import requests
    
    # Don't query for localhost/private IPs
    if ip_address in ['127.0.0.1', 'localhost', '::1'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
        return {
            'country': 'Local Development',
            'country_code': 'XX',
            'city': 'Localhost',
            'timezone': 'UTC'
        }
    
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', 'XX'),
                    'city': data.get('city', 'Unknown'),
                    'timezone': data.get('timezone', 'UTC')
                }
    except Exception:
        pass
    
    return {
        'country': 'Unknown',
        'country_code': 'XX',
        'city': 'Unknown',
        'timezone': 'UTC'
    }


@login_required
def profile_settings(request):
    """User profile settings view."""
    from .models import Profile
    
    # Get or create profile for user
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Get user's IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
    
    # Auto-detect location if not already set or if it's a new request
    location_info = get_location_from_ip(ip_address)
    
    # Update profile with detected location
    if not profile.detected_country or profile.detected_country == 'Unknown':
        profile.detected_country = location_info['country']
        profile.detected_country_code = location_info['country_code']
        profile.detected_city = location_info['city']
        profile.timezone = location_info['timezone']
        profile.save(update_fields=['detected_country', 'detected_country_code', 'detected_city', 'timezone'])
    
    if request.method == 'POST':
        # Update profile settings
        profile.preferred_language = request.POST.get('preferred_language', 'en')
        profile.company_name = request.POST.get('company_name', '').strip()
        profile.job_title = request.POST.get('job_title', '').strip()
        profile.industry = request.POST.get('industry', '').strip()
        profile.website = request.POST.get('website', '').strip()
        profile.last_profile_update = timezone.now()
        profile.save()
        
        # Set the language in session for Django's translation system
        from django.utils import translation
        translation.activate(profile.preferred_language)
        request.session['django_language'] = profile.preferred_language
        
        messages.success(request, "Settings updated successfully.")
        return redirect('users:profile-settings')
    
    # Languages
    languages = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('ja', 'Japanese'),
        ('zh', 'Chinese'),
        ('ko', 'Korean'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
        ('ar', 'Arabic'),
    ]
    
    context = {
        'profile': profile,
        'languages': languages,
        'ip_address': ip_address,
        'location_info': location_info,
    }
    
    return render(request, 'users/profile_settings.html', context)


@login_required
def profile_security(request):
    """User profile security view."""
    return render(request, 'users/profile_security.html')


def user_list(request):
    """User list view."""
    from .models import CustomUser
    users = CustomUser.objects.all()[:50]
    return render(request, 'users/user_list.html', {'users': users})


def user_detail(request, user_id):
    """User detail view."""
    from .models import CustomUser
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'users/user_detail.html', {'user_obj': user})


@login_required
def user_update(request, user_id):
    """User update view."""
    from .models import CustomUser
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'users/user_edit.html', {'user_obj': user})


@login_required
def user_delete(request, user_id):
    """User delete view."""
    from .models import CustomUser
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'users/user_delete.html', {'user_obj': user})


@login_required
def address_list(request):
    """Address list view."""
    addresses = request.user.address_book.all()
    return render(request, 'users/address_list.html', {'addresses': addresses})


@login_required
def address_create(request):
    """Address create view."""
    from .models import AddressBook
    if request.method == 'POST':
        # Create address logic here
        pass
    return render(request, 'users/address_create.html')


@login_required
def address_detail(request, address_id):
    """Address detail view."""
    from .models import AddressBook
    address = get_object_or_404(AddressBook, id=address_id, user=request.user)
    return render(request, 'users/address_detail.html', {'address': address})


@login_required
def address_update(request, address_id):
    """Address update view."""
    from .models import AddressBook
    address = get_object_or_404(AddressBook, id=address_id, user=request.user)
    return render(request, 'users/address_edit.html', {'address': address})


@login_required
def address_delete(request, address_id):
    """Address delete view."""
    from .models import AddressBook
    address = get_object_or_404(AddressBook, id=address_id, user=request.user)
    return render(request, 'users/address_delete.html', {'address': address})


@login_required
def address_set_default(request, address_id):
    """Set default address."""
    from .models import AddressBook
    address = get_object_or_404(AddressBook, id=address_id, user=request.user)
    # Set as default logic here
    return redirect('users:address-list')


def role_list(request):
    """Role list view."""
    from .models import Role
    roles = Role.objects.all()
    return render(request, 'users/role_list.html', {'roles': roles})


def role_detail(request, role_id):
    """Role detail view."""
    from .models import Role
    role = get_object_or_404(Role, id=role_id)
    return render(request, 'users/role_detail.html', {'role': role})


def role_permissions(request, role_id):
    """Role permissions view."""
    from .models import Role
    role = get_object_or_404(Role, id=role_id)
    return render(request, 'users/role_permissions.html', {'role': role})


@login_required
def session_list(request):
    """Session list view."""
    from .models import UserSession
    from django.contrib.sessions.models import Session
    
    # Get current session key
    if not request.session.session_key:
        request.session.save()
    current_session_key = request.session.session_key
    
    # Check if current session exists in UserSession, if not create it
    # This handles users who were logged in before session tracking was added
    if not UserSession.objects.filter(session_key=current_session_key, user=request.user).exists():
        create_user_session(request, request.user)
    
    # Get all user sessions
    user_sessions = request.user.sessions.filter(is_active=True).order_by('-last_activity')
    
    # Mark which session is the current one
    sessions = []
    for session in user_sessions:
        session.is_current_session = (session.session_key == current_session_key)
        sessions.append(session)
    
    return render(request, 'users/session_list.html', {'sessions': sessions})


@login_required
def session_revoke(request, session_id):
    """Revoke session."""
    from .models import UserSession
    from django.contrib.sessions.models import Session
    
    session = get_object_or_404(UserSession, id=session_id, user=request.user)
    
    # Don't allow revoking the current session (user should logout instead)
    if session.session_key == request.session.session_key:
        messages.error(request, "You cannot revoke your current session. Please logout instead.")
        return redirect('users:session-list')
    
    # Deactivate the session
    session.is_active = False
    session.save()
    
    # Delete the Django session if it exists
    try:
        Session.objects.get(session_key=session.session_key).delete()
    except Session.DoesNotExist:
        pass
    
    messages.success(request, "Session terminated successfully.")
    return redirect('users:session-list')


@login_required
def activity_log_list(request):
    """Activity log list view."""
    from .models import UserActivityLog
    logs = request.user.activity_logs.all()[:50]
    return render(request, 'users/activity_log_list.html', {'logs': logs})


@login_required
def activity_log_detail(request, log_id):
    """Activity log detail view."""
    from .models import UserActivityLog
    log = get_object_or_404(UserActivityLog, id=log_id, user=request.user)
    return render(request, 'users/activity_log_detail.html', {'log': log})


@login_required
def security_key_list(request):
    """Security key list view."""
    from .models import UserSecurityKey
    keys = request.user.security_keys.all()
    return render(request, 'users/security_key_list.html', {'keys': keys})


@login_required
def security_key_create(request):
    """Security key create view."""
    from .models import UserSecurityKey
    
    if request.method == 'POST':
        key_type = request.POST.get('key_type')
        name = request.POST.get('name', '').strip()
        is_primary = request.POST.get('is_primary') == 'on'
        
        if not key_type or not name:
            messages.error(request, "Key type and name are required.")
            return render(request, 'users/security_key_create.html')
        
        # If this is set as primary, unset other primary keys
        if is_primary:
            UserSecurityKey.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
        
        security_key = None
        qr_code_data = None
        backup_codes = None
        verification_code = None
        
        if key_type == 'totp':
            # Generate TOTP secret
            secret = pyotp.random_base32()
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=request.user.email,
                issuer_name="ARES Marketplace"
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert QR code to base64 for display
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_data = base64.b64encode(buffer.getvalue()).decode()
            
            security_key = UserSecurityKey.objects.create(
                user=request.user,
                key_type=key_type,
                name=name,
                secret_key=secret,  # Store the secret for verification
                is_primary=is_primary,
                is_active=True
            )
            messages.success(request, f"TOTP key '{name}' registered successfully. Scan the QR code with your authenticator app.")
            
        elif key_type == 'backup':
            # Generate backup codes
            backup_codes = generate_backup_codes(count=10, length=8)
            # Store hashed codes in secret_key field (comma-separated)
            hashed_codes = ','.join([hash_code(code) for code in backup_codes])
            
            security_key = UserSecurityKey.objects.create(
                user=request.user,
                key_type=key_type,
                name=name,
                secret_key=hashed_codes,
                is_primary=is_primary,
                is_active=True
            )
            messages.success(request, f"Backup codes generated for '{name}'. Please save them securely!")
            
        elif key_type == 'sms':
            # Generate SMS code
            verification_code = generate_sms_code(length=6)
            # Store hashed code
            hashed_code = hash_code(verification_code)
            
            security_key = UserSecurityKey.objects.create(
                user=request.user,
                key_type=key_type,
                name=name,
                secret_key=hashed_code,
                is_primary=is_primary,
                is_active=True
            )
            
            # Send SMS (in production, use a service like Twilio)
            # For now, just show the code
            messages.success(request, f"SMS key '{name}' registered. Verification code: {verification_code} (Normally sent via SMS)")
            
        elif key_type == 'email':
            # Email keys don't store a code - they generate fresh codes on demand
            # Store a placeholder to indicate this is an email key
            security_key = UserSecurityKey.objects.create(
                user=request.user,
                key_type=key_type,
                name=name,
                secret_key='email_key_placeholder',  # Placeholder - actual codes are generated on demand
                is_primary=is_primary,
                is_active=True
            )
            
            messages.success(request, f"Email key '{name}' registered successfully. A verification code will be sent to {request.user.email} when you use 2FA.")
            
        elif key_type == 'fido2':
            # FIDO2/WebAuthn registration is handled via AJAX in the template
            # Return a flag to indicate FIDO2 flow should start
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                request.session['fido2_key_name'] = name
                request.session['fido2_is_primary'] = is_primary
                return JsonResponse({
                    'status': 'fido2_ready',
                    'message': 'FIDO2 registration ready'
                })
            else:
                # Regular form submission - redirect back with message
                messages.info(request, "Please use the browser's WebAuthn prompt to complete FIDO2 registration.")
                return render(request, 'users/security_key_create.html')
        
        # Store data in session for display
        if qr_code_data:
            request.session['totp_qr_code'] = qr_code_data
            request.session['totp_secret'] = secret
            request.session['security_key_id'] = str(security_key.id)
            return redirect('users:security-key-totp-setup')
        
        if backup_codes:
            request.session['backup_codes'] = backup_codes
            request.session['security_key_id'] = str(security_key.id)
            return redirect('users:security-key-backup-codes')
        
        return redirect('users:security-key-list')
    
    return render(request, 'users/security_key_create.html')


@login_required
def security_key_totp_setup(request):
    """Display TOTP QR code setup page."""
    qr_code_data = request.session.get('totp_qr_code')
    secret = request.session.get('totp_secret')
    key_id = request.session.get('security_key_id')
    
    if not qr_code_data or not secret:
        messages.error(request, "QR code data not found. Please register a new TOTP key.")
        return redirect('users:security-key-create')
    
    context = {
        'qr_code_data': qr_code_data,
        'secret': secret,
        'key_id': key_id,
    }
    
    # Clear session data after displaying
    if request.method == 'POST':
        request.session.pop('totp_qr_code', None)
        request.session.pop('totp_secret', None)
        request.session.pop('security_key_id', None)
        messages.success(request, "TOTP setup complete!")
        return redirect('users:security-key-list')
    
    return render(request, 'users/security_key_totp_setup.html', context)


@login_required
def security_key_backup_codes(request):
    """Display backup codes."""
    backup_codes = request.session.get('backup_codes')
    key_id = request.session.get('security_key_id')
    
    if not backup_codes:
        messages.error(request, "Backup codes not found. Please register a new backup code key.")
        return redirect('users:security-key-create')
    
    context = {
        'backup_codes': backup_codes,
        'key_id': key_id,
    }
    
    # Clear session data after displaying
    if request.method == 'POST':
        request.session.pop('backup_codes', None)
        request.session.pop('security_key_id', None)
        messages.success(request, "Backup codes saved!")
        return redirect('users:security-key-list')
    
    return render(request, 'users/security_key_backup_codes.html', context)


@login_required
def security_key_delete(request, key_id):
    """Security key delete view."""
    from .models import UserSecurityKey
    key = get_object_or_404(UserSecurityKey, id=key_id, user=request.user)
    
    # Prevent deleting the last active key if 2FA is enabled
    active_keys_count = request.user.security_keys.filter(is_active=True).count()
    if key.is_active and active_keys_count == 1 and request.user.two_factor_enabled:
        messages.error(request, "Cannot delete the last active security key while 2FA is enabled. Disable 2FA first or add another key.")
        return redirect('users:security-key-list')
    
    key_name = key.name
    key.delete()
    messages.success(request, f"Security key '{key_name}' deleted successfully.")
    
    # If no active keys remain, disable 2FA
    active_keys_count = request.user.security_keys.filter(is_active=True).count()
    if active_keys_count == 0 and request.user.two_factor_enabled:
        request.user.two_factor_enabled = False
        request.user.save(update_fields=['two_factor_enabled'])
        messages.warning(request, "2FA has been disabled because you have no active security keys.")
    
    return redirect('users:security-key-list')


@login_required
def fido2_registration_begin(request):
    """Begin FIDO2 registration - generate challenge."""
    from .webauthn_utils import generate_registration_challenge
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'error': 'Name required'}, status=400)
    
    # Store registration info in session
    request.session['fido2_key_name'] = name
    request.session['fido2_is_primary'] = request.POST.get('is_primary') == 'on'
    
    # Generate registration challenge
    user_id = str(request.user.id)
    challenge_data = generate_registration_challenge(
        user_id=user_id,
        username=request.user.username,
        display_name=request.user.display_name or request.user.username
    )
    
    # Fix RP ID for localhost - must be 'localhost' not '127.0.0.1'
    # WebAuthn requires RP ID to match the origin's effective domain
    # For both localhost and 127.0.0.1, we use 'localhost' as RP ID
    hostname = request.get_host().split(':')[0]  # Remove port if present
    if hostname in ['127.0.0.1', 'localhost']:
        challenge_data['options']['rp']['id'] = 'localhost'
        # Also ensure we log this for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'FIDO2 registration: Hostname={hostname}, Setting RP ID to localhost')
    
    # Store challenge in session for verification
    request.session['fido2_challenge'] = challenge_data['challenge']
    
    return JsonResponse({
        'success': True,
        'options': challenge_data['options']
    })


@login_required
def fido2_registration_complete(request):
    """Complete FIDO2 registration - verify and store credential."""
    from .models import UserSecurityKey
    from .webauthn_utils import verify_registration_response
    import json
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    # Get session data
    challenge = request.session.get('fido2_challenge')
    key_name = request.session.get('fido2_key_name')
    is_primary = request.session.get('fido2_is_primary', False)
    
    if not challenge or not key_name:
        return JsonResponse({'error': 'No active registration session'}, status=400)
    
    try:
        # Parse credential from request
        credential_data = json.loads(request.body)
        credential = credential_data.get('credential')
        
        if not credential:
            return JsonResponse({'error': 'Credential required'}, status=400)
        
        # Verify registration response
        user_id = str(request.user.id)
        success, credential_info = verify_registration_response(credential, challenge, user_id)
        
        if not success or not credential_info:
            return JsonResponse({'error': 'Registration verification failed'}, status=400)
        
        # If this is set as primary, unset other primary keys
        if is_primary:
            UserSecurityKey.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
        
        # Store credential in database
        security_key = UserSecurityKey.objects.create(
            user=request.user,
            key_type='fido2',
            name=key_name,
            credential_id=credential_info.get('credential_id', ''),
            public_key=credential_info.get('public_key', ''),
            secret_key=json.dumps(credential_info),  # Store full credential data as JSON
            is_primary=is_primary,
            is_active=True
        )
        
        # Clear session data
        request.session.pop('fido2_challenge', None)
        request.session.pop('fido2_key_name', None)
        request.session.pop('fido2_is_primary', None)
        
        return JsonResponse({
            'success': True,
            'message': f'FIDO2 key "{key_name}" registered successfully',
            'key_id': str(security_key.id)
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Registration failed: {str(e)}'}, status=500)


@login_required
def fido2_authentication_begin(request):
    """Begin FIDO2 authentication - generate challenge."""
    from .models import UserSecurityKey
    from .webauthn_utils import generate_authentication_challenge
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    # Get user's FIDO2 credentials
    fido2_keys = UserSecurityKey.objects.filter(
        user=request.user,
        key_type='fido2',
        is_active=True
    )
    
    if not fido2_keys.exists():
        return JsonResponse({'error': 'No FIDO2 keys registered'}, status=400)
    
    # Collect credential IDs
    credential_ids = []
    for key in fido2_keys:
        if key.credential_id:
            # Decode from base64url if needed
            credential_ids.append(key.credential_id)
    
    if not credential_ids:
        return JsonResponse({'error': 'No valid credential IDs found'}, status=400)
    
    # Generate authentication challenge
    challenge_data = generate_authentication_challenge(credential_ids)
    
    # Store challenge in session
    request.session['fido2_auth_challenge'] = challenge_data['challenge']
    
    return JsonResponse({
        'success': True,
        'options': challenge_data['options']
    })


@login_required
def fido2_authentication_complete(request):
    """Complete FIDO2 authentication - verify credential."""
    from .models import UserSecurityKey
    from .webauthn_utils import verify_authentication_response
    import json
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    # Get challenge from session
    challenge = request.session.get('fido2_auth_challenge')
    if not challenge:
        return JsonResponse({'error': 'No active authentication session'}, status=400)
    
    try:
        # Parse credential from request
        credential_data = json.loads(request.body)
        credential = credential_data.get('credential')
        
        if not credential:
            return JsonResponse({'error': 'Credential required'}, status=400)
        
        # Find the matching credential
        credential_id = credential.get('id')
        fido2_key = UserSecurityKey.objects.filter(
            user=request.user,
            key_type='fido2',
            is_active=True,
            credential_id=credential_id
        ).first()
        
        if not fido2_key:
            return JsonResponse({'error': 'Credential not found'}, status=404)
        
        # Get stored credential data
        stored_data = {}
        if fido2_key.secret_key:
            try:
                stored_data = json.loads(fido2_key.secret_key)
            except:
                stored_data = {'credential_id': fido2_key.credential_id}
        
        # Verify authentication response
        success = verify_authentication_response(credential, challenge, stored_data)
        
        if not success:
            return JsonResponse({'error': 'Authentication verification failed'}, status=400)
        
        # Update last used timestamp
        fido2_key.last_used_at = timezone.now()
        fido2_key.counter = fido2_key.counter + 1
        fido2_key.save(update_fields=['last_used_at', 'counter'])
        
        # Clear session
        request.session.pop('fido2_auth_challenge', None)
        
        return JsonResponse({
            'success': True,
            'message': 'FIDO2 authentication successful'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Authentication failed: {str(e)}'}, status=500)


@login_required
def two_factor_enable(request):
    """Enable two-factor authentication."""
    from .models import UserSecurityKey
    
    # Check if user has at least one active security key
    active_keys = UserSecurityKey.objects.filter(user=request.user, is_active=True)
    
    if not active_keys.exists():
        messages.error(request, "You must have at least one active security key to enable 2FA. Please add a security key first.")
        return redirect('users:security-key-create')
    
    if request.method == 'POST':
        request.user.two_factor_enabled = True
        request.user.save(update_fields=['two_factor_enabled'])
        messages.success(request, "Two-factor authentication has been enabled. You will need to enter a verification code each time you log in.")
        return redirect('users:profile-security')
    
    return redirect('users:profile-security')


@login_required
def two_factor_disable(request):
    """Disable two-factor authentication."""
    if request.method == 'POST':
        request.user.two_factor_enabled = False
        request.user.save(update_fields=['two_factor_enabled'])
        messages.success(request, "Two-factor authentication has been disabled.")
        return redirect('users:profile-security')
    
    return redirect('users:profile-security')


@login_required
def two_factor_verify_view(request):
    """
    Verify 2FA code for protected actions (e.g., purchases).
    Can be called via AJAX or regular POST.
    """
    from .two_factor_utils import verify_2fa_code
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        action = request.POST.get('action', 'verify')
        
        if not code:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Code is required'}, status=400)
            messages.error(request, "Verification code is required.")
            return redirect('users:profile-security')
        
        # Verify the code
        success, security_key, method = verify_2fa_code(request.user, code, purpose=action if action != 'verify' else '2fa')
        
        if success:
            # Store verification in session (valid for 5 minutes)
            from datetime import timedelta
            request.session['2fa_verified'] = True
            request.session['2fa_verified_at'] = timezone.now().isoformat()
            request.session['2fa_verified_for'] = action
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Verification successful'
                })
            
            messages.success(request, "Verification successful.")
            return redirect(request.POST.get('next', 'users:profile-security'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid verification code'
                }, status=400)
            
            messages.error(request, "Invalid verification code. Please try again.")
            return render(request, 'users/2fa_verify.html', {
                'action': action,
                'next': request.POST.get('next', 'users:profile-security')
            })
    
    # GET request - show verification form
    action = request.GET.get('action', 'verify')
    next_url = request.GET.get('next', 'users:profile-security')
    
    return render(request, 'users/2fa_verify.html', {
        'action': action,
        'next': next_url
    })


def is_2fa_verified(request, action='verify'):
    """
    Check if user has verified 2FA in the current session.
    
    Args:
        request: HTTP request object
        action: Action context to verify
    
    Returns:
        bool: True if verified, False otherwise
    """
    from datetime import timedelta
    
    if not request.user.is_authenticated:
        return False
    
    if not request.user.two_factor_enabled:
        return True  # 2FA not enabled, no verification needed
    
    verified = request.session.get('2fa_verified', False)
    verified_at_str = request.session.get('2fa_verified_at')
    verified_for = request.session.get('2fa_verified_for')
    
    if not verified or not verified_at_str:
        return False
    
    # Check if verification is expired (5 minutes)
    try:
        from datetime import datetime
        # Parse the ISO format string
        verified_at_str_clean = verified_at_str.replace('Z', '+00:00')
        verified_at = datetime.fromisoformat(verified_at_str_clean)
        # Make timezone-aware if needed
        if verified_at.tzinfo is None:
            verified_at = timezone.make_aware(verified_at)
        # Compare with current time
        time_diff = timezone.now() - verified_at
        if time_diff > timedelta(minutes=5):
            # Expired
            request.session.pop('2fa_verified', None)
            request.session.pop('2fa_verified_at', None)
            request.session.pop('2fa_verified_for', None)
            return False
    except (ValueError, TypeError, AttributeError) as e:
        # If parsing fails, consider verification invalid
        return False
    
    # Check if verification is for the correct action (or general)
    if verified_for and verified_for != action and verified_for != 'verify':
        return False
    
    return True


# =============================================================================
# SELLER DASHBOARD VIEWS
# =============================================================================

@login_required
def seller_dashboard(request):
    """
    Seller dashboard - main page for sellers to manage their business.
    """
    user = request.user
    
    # Check if user can access seller dashboard
    if not user.can_access_seller_dashboard:
        messages.error(request, "You don't have access to the seller dashboard.")
        return redirect('users:profile')
    
    # Check if seller is approved
    if user.is_seller and not user.is_seller_approved:
        messages.warning(request, "Your seller account is pending approval. You can view the dashboard but cannot list products yet.")
    
    from products.models import Product, Robot
    from orders.models import PurchaseRequest
    
    # Get seller's products
    products = Product.objects.filter(seller=user).select_related('category')
    active_products = products.filter(status='active')
    draft_products = products.filter(status='draft')
    
    # Get orders for seller's products
    orders = PurchaseRequest.objects.filter(product__seller=user).order_by('-created_at')
    pending_orders = orders.filter(status='pending')
    
    # Calculate stats
    from django.db.models import Sum, Count
    total_revenue = orders.filter(status='approved').aggregate(
        total=Sum('product__price')
    )['total'] or 0
    
    context = {
        'products': products[:10],  # Recent 10
        'active_products_count': active_products.count(),
        'draft_products_count': draft_products.count(),
        'total_products': products.count(),
        'orders': orders[:10],  # Recent 10
        'pending_orders_count': pending_orders.count(),
        'total_orders': orders.count(),
        'total_revenue': total_revenue,
        'seller_rating': user.seller_rating,
        'total_sales': user.total_sales,
        'is_approved': user.is_seller_approved,
    }
    
    return render(request, 'users/seller_dashboard.html', context)


@login_required
def seller_products(request):
    """List all products for the seller."""
    user = request.user
    
    if not user.can_access_seller_dashboard:
        messages.error(request, "You don't have access to seller features.")
        return redirect('users:profile')
    
    from products.models import Product
    
    all_products = Product.objects.filter(seller=user).select_related('category')
    products = all_products.order_by('-created_at')
    
    # Calculate stats
    active_count = all_products.filter(status='active').count()
    pending_count = all_products.filter(status='pending').count()
    paused_count = all_products.filter(status='paused').count()
    draft_count = all_products.filter(status='draft').count()
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        products = products.filter(status=status_filter)
    
    context = {
        'products': products,
        'status_filter': status_filter,
        'active_count': active_count,
        'pending_count': pending_count,
        'paused_count': paused_count,
        'draft_count': draft_count,
    }
    
    return render(request, 'users/seller_products.html', context)


@login_required
def seller_orders(request):
    """List all orders for seller's products."""
    user = request.user
    
    if not user.can_access_seller_dashboard:
        messages.error(request, "You don't have access to seller features.")
        return redirect('users:profile')
    
    from orders.models import PurchaseRequest
    
    orders = PurchaseRequest.objects.filter(product__seller=user).select_related(
        'user', 'product'
    ).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Calculate order stats
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    processing_orders = orders.filter(status__in=['approved', 'processing']).count()
    completed_orders = orders.filter(status__in=['completed', 'delivered']).count()
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'completed_orders': completed_orders,
    }
    
    return render(request, 'users/seller_orders.html', context)


@login_required
def seller_add_robot(request):
    """Allow approved sellers to add a new robot listing."""
    user = request.user
    
    # Check if user can sell products
    if not user.can_sell_products:
        if user.is_seller and not user.is_seller_approved:
            messages.error(request, "Your seller account is pending approval. You cannot list products yet.")
        else:
            messages.error(request, "You don't have permission to add products.")
        return redirect('users:seller-dashboard')
    
    from products.forms import CombinedRobotForm
    
    if request.method == 'POST':
        form = CombinedRobotForm(request.POST, request.FILES)
        if form.is_valid():
            product, robot = form.save(seller=user)
            messages.success(request, f"Robot '{product.title}' has been submitted for review. You'll be notified once it's approved.")
            return redirect('users:seller-products')
    else:
        form = CombinedRobotForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'users/seller_add_robot.html', context)


@login_required
def seller_edit_robot(request, product_id):
    """Allow sellers to edit their robot listings."""
    user = request.user
    
    if not user.can_access_seller_dashboard:
        messages.error(request, "You don't have access to seller features.")
        return redirect('users:profile')
    
    from products.models import Product, Robot
    from products.forms import CombinedRobotForm
    
    product = get_object_or_404(Product, id=product_id, seller=user)
    
    try:
        robot = product.robot
    except Robot.DoesNotExist:
        messages.error(request, "Robot details not found for this product.")
        return redirect('users:seller-products')
    
    if request.method == 'POST':
        form = CombinedRobotForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            
            # Update product
            product.title = data['title']
            product.description = data['description']
            product.short_description = data.get('short_description', '')
            product.category = data['category']
            product.price = data['price']
            product.stock_quantity = data['stock_quantity']
            
            # If product was active, set to pending for re-review
            if product.status == 'active':
                product.status = 'pending'
                messages.info(request, "Your changes have been submitted for review.")
            
            product.save()
            
            # Update robot
            robot.robot_type = data['robot_type']
            robot.model_number = data.get('model_number', '')
            robot.manufacturer = data['manufacturer']
            robot.weight_kg = data.get('weight_kg')
            robot.max_speed_kmh = data.get('max_speed_kmh')
            robot.max_payload_kg = data.get('max_payload_kg')
            robot.requires_verification = data.get('requires_verification', False)
            robot.is_companion = data.get('is_companion', False)
            robot.classification_tag = data.get('classification_tag', 'none')
            robot.required_clearance_priority = data.get('required_clearance_priority', 0)
            robot.required_license = data['required_license']
            robot.save()
            
            messages.success(request, f"Robot '{product.title}' has been updated.")
            return redirect('users:seller-products')
    else:
        # Pre-populate form with existing data
        initial_data = {
            'title': product.title,
            'description': product.description,
            'short_description': product.short_description,
            'category': product.category,
            'price': product.price,
            'stock_quantity': product.stock_quantity,
            'robot_type': robot.robot_type,
            'model_number': robot.model_number,
            'manufacturer': robot.manufacturer,
            'weight_kg': robot.weight_kg,
            'max_speed_kmh': robot.max_speed_kmh,
            'max_payload_kg': robot.max_payload_kg,
            'required_license': robot.required_license,
        }
        
        # Determine access level from robot settings
        if robot.is_companion:
            initial_data['access_level'] = 'age_restricted'
        elif robot.required_clearance_priority >= 10:
            initial_data['access_level'] = 'licensed'
        elif robot.requires_verification:
            initial_data['access_level'] = 'verified'
        else:
            initial_data['access_level'] = 'public'
        
        form = CombinedRobotForm(initial=initial_data)
    
    context = {
        'form': form,
        'product': product,
        'robot': robot,
        'is_edit': True,
    }
    
    return render(request, 'users/seller_add_robot.html', context)


@login_required
def seller_delete_robot(request, product_id):
    """Allow sellers to delete their robot listings."""
    user = request.user
    
    if not user.can_access_seller_dashboard:
        messages.error(request, "You don't have access to seller features.")
        return redirect('users:profile')
    
    from products.models import Product
    
    product = get_object_or_404(Product, id=product_id, seller=user)
    
    if request.method == 'POST':
        title = product.title
        product.delete()
        messages.success(request, f"Robot '{title}' has been deleted.")
        return redirect('users:seller-products')
    
    context = {
        'product': product,
    }
    
    return render(request, 'users/seller_delete_robot.html', context)


@login_required
def apply_to_become_seller(request):
    """Allow a buyer to apply to become a seller."""
    user = request.user
    
    if user.is_seller:
        if user.is_seller_approved:
            messages.info(request, "You are already an approved seller.")
        else:
            messages.info(request, "Your seller application is pending approval.")
        return redirect('users:seller-dashboard')
    
    if request.method == 'POST':
        # Update user role to seller (pending approval)
        user.role = 'seller'
        user.is_seller_approved = False
        user.save(update_fields=['role', 'is_seller_approved'])
        
        messages.success(request, "Your seller application has been submitted! An admin will review it shortly.")
        return redirect('users:profile')
    
    return render(request, 'users/apply_seller.html')


# =============================================================================
# STAFF DASHBOARD VIEWS
# =============================================================================

@login_required
def staff_dashboard(request):
    """
    Staff dashboard - main page for staff members to manage their tasks.
    """
    user = request.user
    
    # Check if user can access staff dashboard
    if not user.can_access_staff_dashboard:
        messages.error(request, "You don't have access to the staff dashboard.")
        return redirect('users:profile')
    
    from verification.models import VerificationRequest, ExportLicense
    from support.models import SupportTicket
    from products.models import Product
    from orders.models import PurchaseRequest
    
    # Pending verification requests
    pending_verifications = VerificationRequest.objects.filter(
        status__in=['pending', 'under_review']
    ).count()
    
    # Pending license applications
    pending_licenses = ExportLicense.objects.filter(
        status__in=['pending', 'under_review']
    ).count()
    
    # Pending product approvals
    pending_products = Product.objects.filter(status='pending').count()
    
    # Open support tickets
    try:
        open_tickets = SupportTicket.objects.filter(status__in=['open', 'in_progress']).count()
    except:
        open_tickets = 0
    
    # Pending seller applications
    pending_sellers = User.objects.filter(role='seller', is_seller_approved=False).count()
    
    # Pending purchase requests
    pending_purchases = PurchaseRequest.objects.filter(status__in=['pending', 'under_review']).count()
    
    context = {
        'pending_verifications': pending_verifications,
        'pending_licenses': pending_licenses,
        'pending_products': pending_products,
        'open_tickets': open_tickets,
        'pending_sellers': pending_sellers,
        'pending_purchases': pending_purchases,
    }
    
    return render(request, 'users/staff_dashboard.html', context)


@login_required
def staff_pending_sellers(request):
    """List pending seller applications for staff to review."""
    user = request.user
    
    if not user.can_access_staff_dashboard:
        messages.error(request, "You don't have access to staff features.")
        return redirect('users:profile')
    
    pending_sellers = User.objects.filter(
        role='seller', 
        is_seller_approved=False
    ).order_by('-date_joined')
    
    context = {
        'pending_sellers': pending_sellers,
    }
    
    return render(request, 'users/staff_pending_sellers.html', context)


@login_required
def staff_approve_seller(request, user_id):
    """Approve a seller application."""
    user = request.user
    
    if not user.can_approve_sellers:
        messages.error(request, "You don't have permission to approve sellers.")
        return redirect('users:staff-dashboard')
    
    seller = get_object_or_404(User, id=user_id, role='seller')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            seller.is_seller_approved = True
            seller.is_verified = True
            seller.save(update_fields=['is_seller_approved', 'is_verified'])
            messages.success(request, f"Seller {seller.username} has been approved!")
        elif action == 'reject':
            seller.role = 'buyer'
            seller.is_seller_approved = False
            seller.save(update_fields=['role', 'is_seller_approved'])
            messages.success(request, f"Seller application for {seller.username} has been rejected.")
        
        return redirect('users:staff-pending-sellers')
    
    context = {
        'seller': seller,
    }
    
    return render(request, 'users/staff_approve_seller.html', context)


@login_required  
def staff_pending_products(request):
    """List pending products for staff to review."""
    user = request.user
    
    if not user.can_access_staff_dashboard:
        messages.error(request, "You don't have access to staff features.")
        return redirect('users:profile')
    
    from products.models import Product
    
    pending_products = Product.objects.filter(status='pending').select_related(
        'seller', 'category'
    ).order_by('-created_at')
    
    context = {
        'pending_products': pending_products,
    }
    
    return render(request, 'users/staff_pending_products.html', context)


@login_required
def staff_review_product(request, product_id):
    """Review and approve/reject a product."""
    user = request.user
    
    if not user.can_approve_products:
        messages.error(request, "You don't have permission to review products.")
        return redirect('users:staff-dashboard')
    
    from products.models import Product, Robot
    
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is military-grade and user has permission
    try:
        robot = product.robot
        is_military = robot.is_restricted or robot.robot_type == 'military_autonomous'
        if is_military and not user.can_manage_military_products:
            messages.error(request, "You don't have permission to review military-grade products. This requires Moderator level access or higher.")
            return redirect('users:staff-pending-products')
    except Robot.DoesNotExist:
        robot = None
        is_military = False
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            product.status = 'active'
            product.published_at = timezone.now()
            product.save(update_fields=['status', 'published_at'])
            messages.success(request, f"Product '{product.title}' has been approved and is now live!")
        elif action == 'reject':
            product.status = 'banned'
            product.save(update_fields=['status'])
            messages.success(request, f"Product '{product.title}' has been rejected.")
        elif action == 'request_changes':
            product.status = 'draft'
            product.save(update_fields=['status'])
            messages.success(request, f"Product '{product.title}' has been sent back to the seller for changes.")
        
        return redirect('users:staff-pending-products')
    
    context = {
        'product': product,
        'robot': robot,
        'is_military': is_military,
        'can_manage_military': user.can_manage_military_products,
    }
    
    return render(request, 'users/staff_review_product.html', context)


@login_required
def staff_all_sellers(request):
    """List all sellers (approved and pending) for staff management."""
    user = request.user
    
    if not user.can_access_staff_dashboard:
        messages.error(request, "You don't have access to staff features.")
        return redirect('users:profile')
    
    # Get filter parameter
    status_filter = request.GET.get('status', 'all')
    
    if status_filter == 'approved':
        sellers = User.objects.filter(role='seller', is_seller_approved=True).order_by('-date_joined')
    elif status_filter == 'pending':
        sellers = User.objects.filter(role='seller', is_seller_approved=False).order_by('-date_joined')
    else:
        sellers = User.objects.filter(role='seller').order_by('-date_joined')
    
    context = {
        'sellers': sellers,
        'status_filter': status_filter,
        'total_approved': User.objects.filter(role='seller', is_seller_approved=True).count(),
        'total_pending': User.objects.filter(role='seller', is_seller_approved=False).count(),
    }
    
    return render(request, 'users/staff_all_sellers.html', context)


@login_required
def staff_revoke_seller(request, user_id):
    """Revoke seller status from an approved seller."""
    user = request.user
    
    if not user.can_approve_sellers:
        messages.error(request, "You don't have permission to manage sellers.")
        return redirect('users:staff-dashboard')
    
    seller = get_object_or_404(User, id=user_id, role='seller')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        # Revoke seller status
        seller.role = 'buyer'
        seller.is_seller_approved = False
        seller.save(update_fields=['role', 'is_seller_approved'])
        
        messages.success(request, f"Seller status for {seller.username} has been revoked.")
        return redirect('users:staff-all-sellers')
    
    context = {
        'seller': seller,
    }
    
    return render(request, 'users/staff_revoke_seller.html', context)


@login_required
def staff_all_products(request):
    """List all products for staff management."""
    user = request.user
    
    if not user.can_access_staff_dashboard:
        messages.error(request, "You don't have access to staff features.")
        return redirect('users:profile')
    
    from products.models import Product
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '')
    
    products = Product.objects.select_related('seller', 'category').order_by('-created_at')
    
    if status_filter != 'all':
        products = products.filter(status=status_filter)
    
    if search_query:
        products = products.filter(title__icontains=search_query)
    
    # Get counts for each status
    total_active = Product.objects.filter(status='active').count()
    total_pending = Product.objects.filter(status='pending').count()
    total_rejected = Product.objects.filter(status='rejected').count()
    total_draft = Product.objects.filter(status='draft').count()
    
    context = {
        'products': products,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_active': total_active,
        'total_pending': total_pending,
        'total_rejected': total_rejected,
        'total_draft': total_draft,
    }
    
    return render(request, 'users/staff_all_products.html', context)


@login_required
def staff_delete_product(request, product_id):
    """Delete a product (staff/admin only)."""
    user = request.user
    
    if not user.can_approve_products:
        messages.error(request, "You don't have permission to delete products.")
        return redirect('users:staff-dashboard')
    
    from products.models import Product
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_title = product.title
        seller_name = product.seller.username
        product.delete()
        messages.success(request, f"Product '{product_title}' by {seller_name} has been deleted.")
        return redirect('users:staff-all-products')
    
    context = {
        'product': product,
    }
    
    return render(request, 'users/staff_delete_product.html', context)


@login_required
def staff_all_users(request):
    """List all users for staff management."""
    user = request.user
    
    # Only admins (access_level >= 90) can manage users
    if not user.is_superuser and getattr(user, 'access_level', 0) < 90:
        messages.error(request, "You don't have permission to manage users.")
        return redirect('users:staff-dashboard')
    
    # Get filter parameters
    role_filter = request.GET.get('role', 'all')
    search_query = request.GET.get('q', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    if role_filter != 'all':
        users = users.filter(role=role_filter)
    
    if search_query:
        users = users.filter(username__icontains=search_query) | users.filter(email__icontains=search_query)
    
    context = {
        'users_list': users,
        'role_filter': role_filter,
        'search_query': search_query,
        'total_users': User.objects.count(),
        'total_sellers': User.objects.filter(role='seller').count(),
        'total_buyers': User.objects.filter(role='buyer').count(),
        'total_staff': User.objects.filter(is_staff=True).count(),
    }
    
    return render(request, 'users/staff_all_users.html', context)


@login_required
def staff_change_product_status(request, product_id):
    """Staff function to change product status (activate, pause, ban, etc.)."""
    user = request.user
    
    if not user.is_staff and not user.is_superuser and getattr(user, 'access_level', 0) < 60:
        messages.error(request, "Access denied. Staff privileges required.")
        return redirect('home')
    
    if not user.can_approve_products:
        messages.error(request, "You don't have permission to manage product status.")
        return redirect('users:staff-dashboard')
    
    from products.models import Product
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = ['active', 'paused', 'pending', 'banned', 'discontinued', 'out_of_stock']
        
        if new_status not in valid_statuses:
            messages.error(request, "Invalid status selected.")
            return redirect('users:staff-all-products')
        
        old_status = product.status
        product.status = new_status
        product.save()
        
        status_labels = {
            'active': 'Active',
            'paused': 'Paused',
            'pending': 'Pending Review',
            'banned': 'Banned',
            'discontinued': 'Discontinued',
            'out_of_stock': 'Out of Stock'
        }
        
        messages.success(request, f"Product '{product.title}' status changed from {status_labels.get(old_status, old_status)} to {status_labels.get(new_status, new_status)}.")
        return redirect('users:staff-all-products')
    
    context = {
        'product': product,
        'status_choices': [
            ('active', 'Active', '✅', 'Product is visible and available for purchase'),
            ('paused', 'Paused', '⏸️', 'Product is temporarily hidden from listings'),
            ('pending', 'Pending Review', '⏳', 'Product awaiting staff review'),
            ('banned', 'Banned', '🚫', 'Product banned for policy violation'),
            ('discontinued', 'Discontinued', '📦', 'Product no longer available'),
            ('out_of_stock', 'Out of Stock', '❌', 'Product currently out of stock'),
        ],
    }
    
    return render(request, 'users/staff_change_product_status.html', context)

