"""
User models for ARES platform.
"""
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Manager for CustomUser model."""
    
    def create_user(self, email, username, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for ARES platform.
    Uses email as the unique identifier.
    """
    
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Administrator'),
        ('support', 'Support Staff'),
        ('moderator', 'Moderator'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Authentication fields
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    
    # Personal information
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    
    # Role and permissions
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    role_instance = models.ForeignKey(
        'Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text="Detailed role with permissions"
    )
    
    # Status flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_seller_approved = models.BooleanField(default=False)
    
    # Security
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    pgp_public_key = models.TextField(blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_active = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Financial
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    
    # Seller information
    seller_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_sales = models.PositiveIntegerField(default=0)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Django auth system fields
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='user_set',
        related_query_name='user',
    )
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users_custom_user'
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email'], name='users_custo_email_bcd0b7_idx'),
            models.Index(fields=['username'], name='users_custo_usernam_e890ab_idx'),
            models.Index(fields=['role'], name='users_custo_role_08264f_idx'),
            models.Index(fields=['is_active', 'is_verified'], name='users_custo_is_acti_ab471b_idx'),
            models.Index(fields=['-date_joined'], name='users_custo_date_jo_284f61_idx'),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def get_full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.username
    
    # =========================================================================
    # Role-Based Properties and Methods
    # =========================================================================
    
    # Access Level Hierarchy (higher = more access):
    # 1. Buyer (default) - Can browse and purchase
    # 2. Seller (approved) - Can list products for sale
    # 3. Support Staff - Can review sellers, moderate content
    # 4. Moderator - Can review products, manage verifications
    # 5. Admin - Full access except system settings
    # 6. Super Admin - Full system access
    
    @property
    def access_level(self):
        """
        Returns numeric access level for permission checks.
        Higher number = more privileges.
        """
        if self.is_superuser:
            return 100
        elif self.role == 'admin':
            return 90
        elif self.role == 'moderator':
            return 70
        elif self.role == 'support':
            return 60
        elif self.role == 'seller' and self.is_seller_approved:
            return 40
        elif self.role == 'seller':
            return 30
        else:  # buyer
            return 10
    
    @property
    def is_buyer(self):
        """Check if user is a buyer (regular user)."""
        return self.role == 'buyer'
    
    @property
    def is_seller(self):
        """Check if user is a seller."""
        return self.role == 'seller'
    
    @property
    def is_approved_seller(self):
        """Check if user is an approved seller who can list products."""
        return self.role == 'seller' and self.is_seller_approved
    
    @property
    def is_support_staff(self):
        """Check if user is support staff or higher."""
        return self.role in ['support', 'moderator', 'admin'] or self.is_staff or self.is_superuser
    
    @property
    def is_moderator(self):
        """Check if user is a moderator or higher."""
        return self.role in ['moderator', 'admin'] or self.is_superuser
    
    @property
    def is_admin_user(self):
        """Check if user is an admin."""
        return self.role == 'admin' or self.is_superuser
    
    # =========================================================================
    # Permission Properties - What actions can this user perform?
    # =========================================================================
    
    @property
    def can_sell_products(self):
        """Check if user can list products for sale."""
        return self.is_approved_seller or self.is_superuser
    
    @property
    def can_moderate_content(self):
        """Check if user can moderate content (approve/reject products, reviews)."""
        return self.access_level >= 60  # Support and above
    
    @property
    def can_approve_sellers(self):
        """Check if user can approve seller applications."""
        return self.access_level >= 60  # Support and above
    
    @property
    def can_approve_products(self):
        """Check if user can approve product listings."""
        return self.access_level >= 60  # Support and above
    
    @property
    def can_review_verifications(self):
        """Check if user can review verification requests."""
        return self.access_level >= 60  # Support and above
    
    @property
    def can_manage_military_products(self):
        """Check if user can manage military-grade products (higher clearance)."""
        return self.access_level >= 70  # Moderator and above
    
    @property
    def can_manage_users(self):
        """Check if user can manage other users."""
        return self.access_level >= 90  # Admin and above
    
    @property
    def can_access_admin_panel(self):
        """Check if user can access Django admin panel."""
        return self.is_staff or self.is_superuser
    
    @property
    def can_delete_content(self):
        """Check if user can permanently delete content."""
        return self.access_level >= 70  # Moderator and above
    
    # =========================================================================
    # Dashboard Access Properties
    # =========================================================================
    
    @property
    def can_access_seller_dashboard(self):
        """Check if user can access the seller dashboard."""
        return self.is_seller or self.is_admin_user
    
    @property
    def can_access_staff_dashboard(self):
        """Check if user can access the staff dashboard."""
        return self.access_level >= 60  # Support and above
    
    @property
    def dashboard_url(self):
        """Get the appropriate dashboard URL for this user's role."""
        if self.is_superuser or self.is_admin_user:
            return '/admin/'
        elif self.access_level >= 60:
            return '/users/staff/dashboard/'
        elif self.is_seller:
            return '/users/seller/dashboard/'
        else:
            return '/users/profile/'
    
    def get_role_display_badge(self):
        """Get display info for role badge in UI."""
        role_badges = {
            'buyer': {'label': 'Buyer', 'color': 'blue', 'icon': 'user'},
            'seller': {'label': 'Seller', 'color': 'green', 'icon': 'store'},
            'support': {'label': 'Staff', 'color': 'purple', 'icon': 'headset'},
            'moderator': {'label': 'Moderator', 'color': 'orange', 'icon': 'shield'},
            'admin': {'label': 'Admin', 'color': 'red', 'icon': 'crown'},
        }
        badge = role_badges.get(self.role, {'label': 'User', 'color': 'gray', 'icon': 'user'})
        if self.is_seller and not self.is_seller_approved:
            badge['label'] = 'Pending Seller'
            badge['color'] = 'yellow'
        return badge


class Role(models.Model):
    """
    User roles with permissions.
    """
    
    ROLE_CODES = [
        ('guest', 'Guest'),
        ('client', 'Client'),
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('moderator', 'Moderator'),
        ('support', 'Support Staff'),
        ('account_manager', 'Account Manager'),
        ('compliance', 'Compliance Officer'),
        ('military_auditor', 'Military Auditor'),
        ('system_admin', 'System Administrator'),
        ('super_admin', 'Super Administrator'),
        ('api_user', 'API User'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=30, choices=ROLE_CODES, unique=True)
    description = models.TextField(blank=True)
    
    # Basic permissions
    can_view_products = models.BooleanField(default=True)
    can_purchase = models.BooleanField(default=False)
    can_sell = models.BooleanField(default=False)
    can_moderate = models.BooleanField(default=False)
    can_audit = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_access_admin = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_system_role = models.BooleanField(
        default=False,
        help_text="System roles cannot be deleted"
    )
    priority = models.PositiveIntegerField(
        default=0,
        help_text="Higher priority roles override lower ones"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_role'
        verbose_name = 'role'
        verbose_name_plural = 'roles'
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['code'], name='users_role_code_7e9d84_idx'),
            models.Index(fields=['is_active'], name='users_role_is_acti_ed939d_idx'),
        ]
    
    def __str__(self):
        return self.name


class Profile(models.Model):
    """
    Extended user profile information.
    """
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Professional information
    company_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_handle = models.CharField(max_length=50, blank=True)
    github_username = models.CharField(max_length=50, blank=True)
    
    # Preferences
    timezone = models.CharField(max_length=50, default='UTC')
    preferred_language = models.CharField(max_length=10, default='en')
    detected_country = models.CharField(max_length=100, blank=True, help_text="Auto-detected from IP")
    detected_country_code = models.CharField(max_length=5, blank=True)
    detected_city = models.CharField(max_length=100, blank=True)
    theme_preference = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='dark'
    )
    
    # Verification status
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Timestamps
    last_profile_update = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_profile'
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
        indexes = [
            models.Index(fields=['user'], name='users_profi_user_id_783607_idx'),
            models.Index(fields=['company_name'], name='users_profi_company_ecb4ee_idx'),
        ]
    
    def __str__(self):
        return f"Profile for {self.user.username}"


class PermissionMatrix(models.Model):
    """
    Detailed permission matrix for roles.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    
    # Product permissions
    can_view_all_products = models.BooleanField(default=False)
    can_view_restricted_products = models.BooleanField(default=False)
    can_create_products = models.BooleanField(default=False)
    can_edit_own_products = models.BooleanField(default=False)
    can_edit_all_products = models.BooleanField(default=False)
    can_delete_products = models.BooleanField(default=False)
    
    # Order permissions
    can_view_own_orders = models.BooleanField(default=True)
    can_view_all_orders = models.BooleanField(default=False)
    can_create_orders = models.BooleanField(default=True)
    can_cancel_orders = models.BooleanField(default=False)
    can_approve_orders = models.BooleanField(default=False)
    
    # User management permissions
    can_view_users = models.BooleanField(default=False)
    can_edit_users = models.BooleanField(default=False)
    can_delete_users = models.BooleanField(default=False)
    can_verify_users = models.BooleanField(default=False)
    
    # Verification permissions
    can_submit_verification = models.BooleanField(default=True)
    can_review_verification = models.BooleanField(default=False)
    can_approve_verification = models.BooleanField(default=False)
    
    # Support permissions
    can_create_tickets = models.BooleanField(default=True)
    can_view_all_tickets = models.BooleanField(default=False)
    can_resolve_tickets = models.BooleanField(default=False)
    
    # Analytics and system permissions
    can_view_analytics = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    can_access_logs = models.BooleanField(default=False)
    can_manage_roles = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_permission_matrix'
        verbose_name = 'permission matrix'
        verbose_name_plural = 'permission matrices'
        unique_together = [['role']]
        indexes = [
            models.Index(fields=['role'], name='users_permi_role_id_3d1b16_idx'),
        ]
    
    def __str__(self):
        return f"Permissions for {self.role.name}"


class NotificationPreference(models.Model):
    """
    User notification preferences and settings.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Email notifications
    email_order_updates = models.BooleanField(default=True)
    email_messages = models.BooleanField(default=True)
    email_promotions = models.BooleanField(default=False)
    email_security_alerts = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=False)
    email_verification_updates = models.BooleanField(default=True)
    
    # On-site notifications
    site_order_updates = models.BooleanField(default=True)
    site_messages = models.BooleanField(default=True)
    site_promotions = models.BooleanField(default=True)
    site_verification_updates = models.BooleanField(default=True)
    
    # Seller notifications
    email_new_orders = models.BooleanField(default=True)
    email_reviews = models.BooleanField(default=True)
    email_low_stock = models.BooleanField(default=True)
    email_disputes = models.BooleanField(default=True)
    
    # Push notifications
    push_enabled = models.BooleanField(default=False)
    push_order_updates = models.BooleanField(default=True)
    push_messages = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_notification_preference'
        verbose_name = 'notification preference'
        verbose_name_plural = 'notification preferences'
        indexes = [
            models.Index(fields=['user'], name='users_notif_user_id_89ae99_idx'),
        ]
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"


class UserNotificationSettings(models.Model):
    """
    Legacy notification settings (kept for backward compatibility).
    """
    
    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    
    # Email notifications
    email_order_updates = models.BooleanField(default=True)
    email_messages = models.BooleanField(default=True)
    email_promotions = models.BooleanField(default=False)
    email_security_alerts = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=False)
    
    # On-site notifications
    site_order_updates = models.BooleanField(default=True)
    site_messages = models.BooleanField(default=True)
    site_promotions = models.BooleanField(default=True)
    
    # Seller notifications
    email_new_orders = models.BooleanField(default=True)
    email_reviews = models.BooleanField(default=True)
    email_low_stock = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'notification settings'
        verbose_name_plural = 'notification settings'
    
    def __str__(self):
        return f"Notification settings for {self.user.username}"


class AddressBook(models.Model):
    """
    User address book for shipping and billing addresses.
    """
    
    ADDRESS_TYPE_CHOICES = [
        ('shipping', 'Shipping Address'),
        ('billing', 'Billing Address'),
        ('both', 'Shipping & Billing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='address_book'
    )
    
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES,
        default='shipping'
    )
    label = models.CharField(max_length=50, blank=True)
    recipient_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    street_address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_address_book'
        verbose_name = 'address book entry'
        verbose_name_plural = 'address book entries'
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'address_type'], name='users_addre_user_id_adaa2e_idx'),
            models.Index(fields=['is_default'], name='users_addre_is_defa_cda90c_idx'),
        ]
    
    def __str__(self):
        return f"{self.recipient_name} - {self.city}, {self.country}"
    
    def save(self, *args, **kwargs):
        """Ensure only one default address per type per user."""
        if self.is_default:
            AddressBook.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class LoginAudit(models.Model):
    """
    Audit log for user login attempts.
    """
    
    STATUS_CHOICES = [
        ('success', 'Successful'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
        ('locked', 'Account Locked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='login_audits',
        null=True,
        blank=True
    )
    email = models.EmailField(
        max_length=254,
        help_text="Email used in login attempt"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Location and device information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    device_fingerprint = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    isp = models.CharField(max_length=200, blank=True)
    
    # Security assessment
    is_suspicious = models.BooleanField(default=False)
    risk_score = models.PositiveIntegerField(
        default=0,
        help_text="0-100 risk assessment"
    )
    failure_reason = models.CharField(max_length=200, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_login_audit'
        verbose_name = 'login audit'
        verbose_name_plural = 'login audits'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='users_login_user_id_3a29c7_idx'),
            models.Index(fields=['email', '-created_at'], name='users_login_email_dbb4f3_idx'),
            models.Index(fields=['ip_address', '-created_at'], name='users_login_ip_addr_3e3738_idx'),
            models.Index(fields=['status', '-created_at'], name='users_login_status_509292_idx'),
            models.Index(fields=['is_suspicious'], name='users_login_is_susp_ec5c6a_idx'),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.status} - {self.created_at}"


class UserSecurityKey(models.Model):
    """
    Security keys for two-factor authentication.
    """
    
    KEY_TYPE_CHOICES = [
        ('fido2', 'FIDO2/WebAuthn'),
        ('totp', 'TOTP (Time-based)'),
        ('backup', 'Backup Code'),
        ('sms', 'SMS Code'),
        ('email', 'Email Code'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='security_keys'
    )
    
    key_type = models.CharField(max_length=20, choices=KEY_TYPE_CHOICES)
    name = models.CharField(
        max_length=100,
        help_text="User-friendly name for the key"
    )
    
    # FIDO2 specific fields
    credential_id = models.CharField(
        max_length=500,
        blank=True,
        help_text="FIDO2 credential ID"
    )
    public_key = models.TextField(blank=True)
    secret_key = models.CharField(
        max_length=500,
        blank=True,
        help_text="Encrypted secret"
    )
    counter = models.PositiveIntegerField(
        default=0,
        help_text="FIDO2 signature counter"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    last_used_at = models.DateTimeField(null=True, blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_security_key'
        verbose_name = 'security key'
        verbose_name_plural = 'security keys'
        ordering = ['-is_primary', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active'], name='users_secur_user_id_a1f27d_idx'),
            models.Index(fields=['key_type'], name='users_secur_key_typ_b94e3c_idx'),
            models.Index(fields=['credential_id'], name='users_secur_credent_dc561f_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_key_type_display()}) for {self.user.username}"


class UserSession(models.Model):
    """
    User session tracking.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'users_user_session'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', '-last_activity'], name='users_user__user_id_0c2a29_idx'),
            models.Index(fields=['session_key'], name='users_user__session_c6bca5_idx'),
            models.Index(fields=['ip_address', '-created_at'], name='users_user__ip_addr_00e19b_idx'),
            models.Index(fields=['is_active', 'expires_at'], name='users_user__is_acti_949926_idx'),
        ]
    
    def __str__(self):
        return f"Session for {self.user.username} - {self.ip_address}"


class UserActivityLog(models.Model):
    """
    User activity logging.
    """
    
    ACTIVITY_TYPE_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('email_change', 'Email Change'),
        ('profile_update', 'Profile Update'),
        ('2fa_enable', '2FA Enabled'),
        ('2fa_disable', '2FA Disabled'),
        ('order_placed', 'Order Placed'),
        ('withdrawal', 'Withdrawal Request'),
        ('deposit', 'Deposit'),
        ('suspicious', 'Suspicious Activity'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_user_activity_log'
        verbose_name = 'activity log'
        verbose_name_plural = 'activity logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='users_user__user_id_6cdf41_idx'),
            models.Index(fields=['activity_type', '-created_at'], name='users_user__activit_d21d2e_idx'),
            models.Index(fields=['ip_address', '-created_at'], name='users_user__ip_addr_9182cf_idx'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.created_at}"


class Notification(models.Model):
    """
    User notifications for important events.
    """
    NOTIFICATION_TYPES = [
        ('product_added', 'New Product Added'),
        ('robot_added', 'New Robot Added'),
        ('verification_approved', 'Verification Approved'),
        ('verification_rejected', 'Verification Rejected'),
        ('verification_updated', 'Verification Status Updated'),
        ('license_approved', 'Export License Approved'),
        ('license_rejected', 'Export License Rejected'),
        ('license_info_required', 'Additional Info Required'),
        ('license_suspended', 'Export License Suspended'),
        ('license_expiring', 'Export License Expiring Soon'),
        ('purchase_request_approved', 'Purchase Request Approved'),
        ('purchase_request_rejected', 'Purchase Request Rejected'),
        ('order_status_changed', 'Order Status Changed'),
        ('message_received', 'New Message Received'),
        ('system_alert', 'System Alert'),
        # Invoice notifications
        ('invoice_issued', 'Invoice Issued'),
        ('invoice_sent', 'Invoice Sent'),
        ('invoice_paid', 'Invoice Payment Received'),
        ('invoice_overdue', 'Invoice Overdue'),
        ('invoice_cancelled', 'Invoice Cancelled'),
        ('general', 'General Notification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Notification Content
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related Objects (optional, for linking to specific items)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    verification_request = models.ForeignKey(
        'verification.VerificationRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_notification'
        verbose_name = 'notification'
        verbose_name_plural = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

