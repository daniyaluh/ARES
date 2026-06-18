from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    Profile,
    Role,
    PermissionMatrix,
    LoginAudit,
    UserSecurityKey,
    AddressBook,
    NotificationPreference,
    UserSession,
    UserActivityLog,
    Notification
)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fields = (
        ('company_name', 'job_title'),
        ('industry', 'website'),
        ('preferred_language', 'timezone'),
        ('detected_country', 'detected_city'),
        ('email_verified', 'phone_verified'),
        'last_profile_update',
    )
    readonly_fields = ('detected_country', 'detected_city', 'last_profile_update')


class AddressBookInline(admin.TabularInline):
    model = AddressBook
    extra = 0
    fields = ('label', 'address_type', 'recipient_name', 'city', 'country', 'is_default')


class NotificationPreferenceInline(admin.StackedInline):
    model = NotificationPreference
    can_delete = False


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'role', 'role_instance', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_verified', 'is_seller_approved', 'is_staff', 'role_instance')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'first_name', 'last_name', 'display_name', 'avatar', 'bio', 'phone_number')}),
        ('Role & Status', {'fields': ('role', 'role_instance', 'is_active', 'is_verified', 'is_seller_approved')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Security', {'fields': ('two_factor_enabled', 'pgp_public_key', 'failed_login_attempts', 'locked_until')}),
        ('Financial', {'fields': ('balance',)}),
        ('Seller Info', {'fields': ('seller_rating', 'total_sales')}),
        ('Important Dates', {'fields': ('last_login', 'last_active', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'is_active', 'is_verified'),
        }),
    )
    
    inlines = [ProfileInline, AddressBookInline, NotificationPreferenceInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'job_title', 'industry', 'detected_country', 'preferred_language', 'email_verified', 'phone_verified')
    list_filter = ('industry', 'detected_country', 'preferred_language', 'email_verified', 'phone_verified')
    search_fields = ('user__email', 'user__username', 'company_name', 'job_title', 'detected_country', 'detected_city')
    raw_id_fields = ('user',)
    readonly_fields = ('detected_country', 'detected_country_code', 'detected_city', 'last_profile_update', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': ('company_name', 'job_title', 'industry', 'website')
        }),
        ('Location (Auto-detected)', {
            'fields': ('detected_country', 'detected_country_code', 'detected_city', 'timezone'),
            'description': 'Location is automatically detected from user IP address'
        }),
        ('Preferences', {
            'fields': ('preferred_language',)
        }),
        ('Verification Status', {
            'fields': ('email_verified', 'phone_verified')
        }),
        ('Timestamps', {
            'fields': ('last_profile_update', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'priority', 'is_active', 'is_system_role', 'created_at')
    list_filter = ('is_active', 'is_system_role', 'code')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('is_system_role',) if not admin.site.is_registered(Role) else ()


@admin.register(PermissionMatrix)
class PermissionMatrixAdmin(admin.ModelAdmin):
    list_display = ('role', 'can_view_all_products', 'can_create_products', 'can_approve_orders', 'can_edit_users')
    list_filter = ('can_view_all_products', 'can_create_products', 'can_approve_orders', 'can_edit_users')
    search_fields = ('role__name',)
    raw_id_fields = ('role',)


@admin.register(LoginAudit)
class LoginAuditAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'status', 'ip_address', 'country', 'is_suspicious', 'created_at')
    list_filter = ('status', 'is_suspicious', 'country', 'created_at')
    search_fields = ('email', 'user__email', 'user__username', 'ip_address')
    readonly_fields = ('user', 'email', 'status', 'ip_address', 'user_agent', 'device_fingerprint', 'country', 'city', 'isp', 'is_suspicious', 'risk_score', 'failure_reason', 'session_id', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(UserSecurityKey)
class UserSecurityKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'key_type', 'is_active', 'is_primary', 'last_used_at', 'created_at')
    list_filter = ('key_type', 'is_active', 'is_primary')
    search_fields = ('user__email', 'user__username', 'name', 'credential_id')
    raw_id_fields = ('user',)
    readonly_fields = ('credential_id', 'counter', 'last_used_at', 'created_at')


@admin.register(AddressBook)
class AddressBookAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'address_type', 'city', 'country', 'is_default', 'is_active')
    list_filter = ('address_type', 'country', 'is_default', 'is_active')
    search_fields = ('user__email', 'user__username', 'city', 'postal_code', 'street_address')
    raw_id_fields = ('user',)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_order_updates', 'push_enabled', 'created_at')
    list_filter = ('email_order_updates', 'push_enabled', 'email_security_alerts')
    search_fields = ('user__email', 'user__username')
    raw_id_fields = ('user',)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'device_type', 'country', 'is_active', 'created_at', 'last_activity')
    list_filter = ('is_active', 'device_type', 'country')
    search_fields = ('user__email', 'user__username', 'ip_address', 'session_key')
    readonly_fields = ('session_key', 'ip_address', 'user_agent', 'created_at', 'last_activity', 'expires_at')
    date_hierarchy = 'created_at'


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email', 'user__username', 'description')
    readonly_fields = ('user', 'activity_type', 'description', 'ip_address', 'user_agent', 'metadata', 'created_at')
    date_hierarchy = 'created_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'user__username', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')
    raw_id_fields = ('user', 'product', 'verification_request')
    date_hierarchy = 'created_at'
