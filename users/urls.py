"""
URL patterns for Users app.
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('login/2fa/', views.login_2fa_view, name='login-2fa'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('password-reset/', views.password_reset_view, name='password-reset'),
    path('password-reset-confirm/<str:token>/', views.password_reset_confirm_view, name='password-reset-confirm'),
    
    # User Profile
    path('profile/', views.profile_detail, name='profile'),
    path('profile/edit/', views.profile_update, name='profile-edit'),
    path('profile/settings/', views.profile_settings, name='profile-settings'),
    path('profile/security/', views.profile_security, name='profile-security'),
    
    # User Management (List/Detail)
    path('', views.user_list, name='user-list'),
    path('<uuid:user_id>/', views.user_detail, name='user-detail'),
    path('<uuid:user_id>/edit/', views.user_update, name='user-edit'),
    path('<uuid:user_id>/delete/', views.user_delete, name='user-delete'),
    
    # Address Book
    path('addresses/', views.address_list, name='address-list'),
    path('addresses/create/', views.address_create, name='address-create'),
    path('addresses/<uuid:address_id>/', views.address_detail, name='address-detail'),
    path('addresses/<uuid:address_id>/edit/', views.address_update, name='address-edit'),
    path('addresses/<uuid:address_id>/delete/', views.address_delete, name='address-delete'),
    path('addresses/<uuid:address_id>/set-default/', views.address_set_default, name='address-set-default'),
    
    # Roles & Permissions
    path('roles/', views.role_list, name='role-list'),
    path('roles/<uuid:role_id>/', views.role_detail, name='role-detail'),
    path('roles/<uuid:role_id>/permissions/', views.role_permissions, name='role-permissions'),
    
    # User Activity & Sessions
    path('sessions/', views.session_list, name='session-list'),
    path('sessions/<uuid:session_id>/revoke/', views.session_revoke, name='session-revoke'),
    path('activity/', views.activity_log_list, name='activity-list'),
    path('activity/<uuid:log_id>/', views.activity_log_detail, name='activity-detail'),
    
    # Notification Preferences
    path('notification-preferences/', views.notification_preferences, name='notification-preferences'),
    path('notification-preferences/update/', views.notification_preferences_update, name='notification-preferences-update'),
    
    # Notifications
    path('notifications/', views.notification_list, name='notification-list'),
    path('notifications/<uuid:notification_id>/read/', views.notification_mark_read, name='notification-mark-read'),
    path('notifications/mark-all-read/', views.notification_mark_all_read, name='notification-mark-all-read'),
    
    # Security
    path('security-keys/', views.security_key_list, name='security-key-list'),
    path('security-keys/create/', views.security_key_create, name='security-key-create'),
    path('security-keys/totp-setup/', views.security_key_totp_setup, name='security-key-totp-setup'),
    path('security-keys/backup-codes/', views.security_key_backup_codes, name='security-key-backup-codes'),
    path('security-keys/<uuid:key_id>/delete/', views.security_key_delete, name='security-key-delete'),
    
    # FIDO2/WebAuthn
    path('fido2/register/begin/', views.fido2_registration_begin, name='fido2-register-begin'),
    path('fido2/register/complete/', views.fido2_registration_complete, name='fido2-register-complete'),
    path('fido2/auth/begin/', views.fido2_authentication_begin, name='fido2-auth-begin'),
    path('fido2/auth/complete/', views.fido2_authentication_complete, name='fido2-auth-complete'),
    
    # Two-Factor Authentication
    path('2fa/enable/', views.two_factor_enable, name='2fa-enable'),
    path('2fa/disable/', views.two_factor_disable, name='2fa-disable'),
    path('2fa/verify/', views.two_factor_verify_view, name='2fa-verify'),
    
    # Seller Dashboard
    path('seller/dashboard/', views.seller_dashboard, name='seller-dashboard'),
    path('seller/products/', views.seller_products, name='seller-products'),
    path('seller/products/add/', views.seller_add_robot, name='seller-add-robot'),
    path('seller/products/<uuid:product_id>/edit/', views.seller_edit_robot, name='seller-edit-robot'),
    path('seller/products/<uuid:product_id>/delete/', views.seller_delete_robot, name='seller-delete-robot'),
    path('seller/orders/', views.seller_orders, name='seller-orders'),
    path('seller/apply/', views.apply_to_become_seller, name='apply-seller'),
    
    # Staff Dashboard
    path('staff/dashboard/', views.staff_dashboard, name='staff-dashboard'),
    path('staff/pending-sellers/', views.staff_pending_sellers, name='staff-pending-sellers'),
    path('staff/approve-seller/<uuid:user_id>/', views.staff_approve_seller, name='staff-approve-seller'),
    path('staff/all-sellers/', views.staff_all_sellers, name='staff-all-sellers'),
    path('staff/revoke-seller/<uuid:user_id>/', views.staff_revoke_seller, name='staff-revoke-seller'),
    path('staff/pending-products/', views.staff_pending_products, name='staff-pending-products'),
    path('staff/review-product/<uuid:product_id>/', views.staff_review_product, name='staff-review-product'),
    path('staff/all-products/', views.staff_all_products, name='staff-all-products'),
    path('staff/delete-product/<uuid:product_id>/', views.staff_delete_product, name='staff-delete-product'),
    path('staff/change-product-status/<uuid:product_id>/', views.staff_change_product_status, name='staff-change-product-status'),
    path('staff/all-users/', views.staff_all_users, name='staff-all-users'),
]

