from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    ClearanceLevel,
    VerificationRequest,
    IdentityDocument,
    Certification,
    MilitaryAffiliation,
    VerificationLog,
    ExportLicense
)


class IdentityDocumentInline(admin.StackedInline):
    """Inline admin for identity documents."""
    model = IdentityDocument
    extra = 0
    fields = ('document_type', 'document_number', 'issuing_country', 'issuing_authority',
              'issue_date', 'expiry_date', 'front_image', 'front_image_preview', 
              'back_image', 'back_image_preview', 'is_verified', 'verification_notes')
    readonly_fields = ('created_at', 'front_image_preview', 'back_image_preview')
    
    def front_image_preview(self, obj):
        """Display front image preview."""
        if obj.front_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border: 1px solid #ddd; border-radius: 4px;" />',
                obj.front_image.url
            )
        return "No image uploaded"
    front_image_preview.short_description = 'Front Image Preview'
    
    def back_image_preview(self, obj):
        """Display back image preview."""
        if obj.back_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border: 1px solid #ddd; border-radius: 4px;" />',
                obj.back_image.url
            )
        return "No image uploaded"
    back_image_preview.short_description = 'Back Image Preview'


class CertificationInline(admin.TabularInline):
    """Inline admin for certifications."""
    model = Certification
    extra = 0
    fields = ('certification_type', 'certification_number', 'issuing_organization', 'is_verified', 'expiry_date')
    readonly_fields = ('expiry_date',)


class MilitaryAffiliationInline(admin.StackedInline):
    """Inline admin for military affiliation."""
    model = MilitaryAffiliation
    can_delete = False
    fields = ('branch', 'rank', 'rank_title', 'unit', 'service_number', 
              'is_active_duty', 'is_veteran', 'is_reservist', 'is_contractor',
              'service_start_date', 'service_end_date', 'is_verified')


class VerificationLogInline(admin.TabularInline):
    """Inline admin for verification logs."""
    model = VerificationLog
    extra = 0
    can_delete = False
    readonly_fields = ('action_type', 'description', 'performed_by', 'created_at')
    fields = ('action_type', 'description', 'performed_by', 'created_at')


@admin.register(ClearanceLevel)
class ClearanceLevelAdmin(admin.ModelAdmin):
    """Admin for clearance levels."""
    list_display = ('name', 'code', 'priority', 'can_access_restricted', 'can_access_military', 
                    'can_access_export_controlled', 'is_active', 'validity_months')
    list_filter = ('is_active', 'can_access_restricted', 'can_access_military', 'can_access_export_controlled')
    search_fields = ('name', 'code', 'description')
    ordering = ('-priority', 'name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Access Permissions', {
            'fields': ('can_access_restricted', 'can_access_military', 'can_access_export_controlled',
                      'minimum_clearance_required')
        }),
        ('Validity', {
            'fields': ('validity_months', 'requires_renewal', 'requires_background_check')
        }),
        ('Status', {
            'fields': ('is_active', 'priority')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    """Admin for verification requests."""
    list_display = ('user', 'requested_clearance', 'status', 'current_clearance', 'submitted_at', 
                    'reviewed_at', 'reviewed_by', 'is_approved', 'is_expired')
    list_filter = ('status', 'requested_clearance', 'current_clearance', 'submitted_at', 'reviewed_at')
    search_fields = ('user__email', 'user__username', 'reason', 'review_notes', 'rejection_reason')
    raw_id_fields = ('user', 'reviewed_by', 'requested_clearance', 'current_clearance')
    readonly_fields = ('submitted_at', 'reviewed_at', 'created_at', 'updated_at', 'is_approved', 'is_expired')
    date_hierarchy = 'submitted_at'
    ordering = ('-submitted_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Request Details', {
            'fields': ('requested_clearance', 'reason', 'intended_use')
        }),
        ('Status', {
            'fields': ('status', 'current_clearance')
        }),
        ('Review Process', {
            'fields': ('reviewed_by', 'review_notes', 'rejection_reason', 'reviewed_at')
        }),
        ('Dates', {
            'fields': ('submitted_at', 'expires_at', 'created_at', 'updated_at')
        }),
        ('Properties', {
            'fields': ('is_approved', 'is_expired'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [IdentityDocumentInline, CertificationInline, MilitaryAffiliationInline, VerificationLogInline]
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Bulk approve verification requests."""
        from .models import ClearanceLevel
        
        # Get default clearance level (or use requested)
        default_clearance = ClearanceLevel.objects.filter(code='secret', is_active=True).first()
        
        if not default_clearance:
            self.message_user(request, "No default clearance level found. Please set one.", level='error')
            return
        
        count = 0
        for verification_request in queryset.filter(status='pending'):
            verification_request.approve(request.user, default_clearance, 'Bulk approved by admin')
            count += 1
        
        self.message_user(request, f"{count} verification requests approved.")
    approve_requests.short_description = "Approve selected verification requests"
    
    def reject_requests(self, request, queryset):
        """Bulk reject verification requests."""
        count = 0
        for verification_request in queryset.filter(status__in=['pending', 'under_review']):
            verification_request.reject(request.user, 'Bulk rejected by admin')
            count += 1
        
        self.message_user(request, f"{count} verification requests rejected.")
    reject_requests.short_description = "Reject selected verification requests"


@admin.register(IdentityDocument)
class IdentityDocumentAdmin(admin.ModelAdmin):
    """Admin for identity documents."""
    list_display = ('verification_request', 'document_type', 'document_number', 'issuing_country', 
                    'is_verified', 'verified_by', 'created_at')
    list_filter = ('document_type', 'is_verified', 'issuing_country', 'created_at')
    search_fields = ('verification_request__user__email', 'document_number', 'issuing_country')
    raw_id_fields = ('verification_request', 'verified_by')
    readonly_fields = ('created_at', 'updated_at', 'front_image_preview', 'back_image_preview')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Verification Request', {
            'fields': ('verification_request',)
        }),
        ('Document Information', {
            'fields': ('document_type', 'document_number', 'issuing_country', 'issuing_authority',
                      'issue_date', 'expiry_date')
        }),
        ('Document Images', {
            'fields': ('front_image', 'front_image_preview', 'back_image', 'back_image_preview'),
            'description': 'Uploaded ID card images for verification'
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verification_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def front_image_preview(self, obj):
        """Display front image preview."""
        if obj.front_image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px;" />',
                obj.front_image.url
            )
        return "No image uploaded"
    front_image_preview.short_description = 'Front Image Preview'
    
    def back_image_preview(self, obj):
        """Display back image preview."""
        if obj.back_image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px;" />',
                obj.back_image.url
            )
        return "No image uploaded"
    back_image_preview.short_description = 'Back Image Preview'


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    """Admin for certifications."""
    list_display = ('verification_request', 'certification_type', 'certification_number', 
                    'issuing_organization', 'is_verified', 'is_expired', 'expiry_date')
    list_filter = ('certification_type', 'is_verified', 'issue_date', 'expiry_date')
    search_fields = ('verification_request__user__email', 'certification_number', 'issuing_organization')
    raw_id_fields = ('verification_request', 'verified_by')
    readonly_fields = ('created_at', 'updated_at', 'is_expired')
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Verification Request', {
            'fields': ('verification_request',)
        }),
        ('Certification Details', {
            'fields': ('certification_type', 'certification_number', 'issuing_organization',
                      'issue_date', 'expiry_date', 'certificate_file')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verification_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_expired'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MilitaryAffiliation)
class MilitaryAffiliationAdmin(admin.ModelAdmin):
    """Admin for military affiliations."""
    list_display = ('verification_request', 'branch', 'rank', 'rank_title', 'unit', 
                    'is_active_duty', 'is_veteran', 'is_verified', 'verified_by')
    list_filter = ('branch', 'rank', 'is_active_duty', 'is_veteran', 'is_reservist', 
                   'is_contractor', 'is_verified')
    search_fields = ('verification_request__user__email', 'unit', 'service_number', 'rank_title')
    raw_id_fields = ('verification_request', 'verified_by')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Verification Request', {
            'fields': ('verification_request',)
        }),
        ('Military Information', {
            'fields': ('branch', 'rank', 'rank_title', 'unit', 'service_number')
        }),
        ('Status', {
            'fields': ('is_active_duty', 'is_veteran', 'is_reservist', 'is_contractor')
        }),
        ('Service Dates', {
            'fields': ('service_start_date', 'service_end_date')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verification_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    """Admin for verification logs."""
    list_display = ('verification_request', 'user', 'action_type', 'performed_by', 
                    'ip_address', 'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('user__email', 'user__username', 'description', 'performed_by__email')
    raw_id_fields = ('verification_request', 'user', 'performed_by')
    readonly_fields = ('verification_request', 'user', 'action_type', 'description', 
                      'performed_by', 'ip_address', 'user_agent', 'metadata', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Request & User', {
            'fields': ('verification_request', 'user')
        }),
        ('Action Details', {
            'fields': ('action_type', 'description', 'performed_by')
        }),
        ('Context', {
            'fields': ('ip_address', 'user_agent', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        """Logs are created automatically, not manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Logs are read-only."""
        return False


@admin.register(ExportLicense)
class ExportLicenseAdmin(admin.ModelAdmin):
    """Admin for export licenses - manage license applications and approvals."""
    list_display = ('license_number_display', 'user', 'license_type', 'company_name', 'country',
                    'status', 'status_badge', 'valid_until', 'is_valid_display', 'submitted_at')
    list_filter = ('status', 'license_type', 'country', 'submitted_at', 'approved_at')
    search_fields = ('license_number', 'user__email', 'user__username', 'company_name', 
                     'company_registration_number', 'country', 'purpose')
    raw_id_fields = ('user', 'reviewed_by')
    readonly_fields = ('id', 'license_number', 'submitted_at', 'approved_at', 'reviewed_at',
                       'created_at', 'updated_at', 'is_valid_display', 'days_until_expiry_display',
                       'document_preview_1', 'document_preview_2', 'document_preview_3')
    date_hierarchy = 'submitted_at'
    ordering = ('-submitted_at',)
    
    fieldsets = (
        ('License Information', {
            'fields': ('id', 'license_number', 'license_type', 'status'),
            'description': '📋 Export License Application Details'
        }),
        ('Applicant Information', {
            'fields': ('user', 'company_name', 'company_registration_number', 'business_type',
                      'country', 'address', 'contact_phone', 'contact_email')
        }),
        ('Purpose & Justification', {
            'fields': ('purpose', 'justification', 'product_categories', 'end_use_statement')
        }),
        ('Supporting Documents', {
            'fields': ('supporting_document_1', 'document_preview_1',
                      'supporting_document_2', 'document_preview_2',
                      'supporting_document_3', 'document_preview_3'),
            'classes': ('collapse',)
        }),
        ('Review & Decision', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes', 'rejection_reason',
                      'additional_info_request'),
            'classes': ('collapse',)
        }),
        ('Validity & Limits', {
            'fields': ('approved_at', 'valid_from', 'valid_until', 'is_valid_display',
                      'days_until_expiry_display', 'max_purchase_value', 'remaining_purchase_value'),
        }),
        ('Restrictions', {
            'fields': ('allowed_product_ids', 'restricted_countries'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_licenses', 'reject_licenses', 'request_additional_info_action', 
               'suspend_licenses', 'revoke_licenses']
    
    def license_number_display(self, obj):
        """Display license number or application ID."""
        if obj.license_number:
            return format_html('<code style="color: #22c55e; font-weight: bold;">{}</code>', 
                             obj.license_number)
        return format_html('<span style="color: #94a3b8;">Pending #{}</span>', 
                          str(obj.id)[:8])
    license_number_display.short_description = 'License #'
    license_number_display.admin_order_field = 'license_number'
    
    def status_badge(self, obj):
        """Display colored status badge."""
        colors = {
            'draft': '#6b7280',
            'pending': '#eab308',
            'under_review': '#3b82f6',
            'additional_info_required': '#f97316',
            'approved': '#22c55e',
            'rejected': '#ef4444',
            'suspended': '#f97316',
            'revoked': '#dc2626',
            'expired': '#9ca3af',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}20; color: {}; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color, color, obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    
    def is_valid_display(self, obj):
        """Display validity status."""
        if obj.is_valid:
            return format_html('<span style="color: #22c55e;">✓ Valid</span>')
        elif obj.status == 'approved' and obj.is_expired:
            return format_html('<span style="color: #ef4444;">✗ Expired</span>')
        elif obj.status == 'approved':
            return format_html('<span style="color: #f97316;">⚠ Issue</span>')
        return format_html('<span style="color: #6b7280;">—</span>')
    is_valid_display.short_description = 'Valid'
    
    def days_until_expiry_display(self, obj):
        """Display days until expiry."""
        days = obj.days_until_expiry
        if days is None:
            return '—'
        if days < 0:
            return format_html('<span style="color: #ef4444;">Expired {} days ago</span>', abs(days))
        if days <= 30:
            return format_html('<span style="color: #f97316;">{} days</span>', days)
        return format_html('<span style="color: #22c55e;">{} days</span>', days)
    days_until_expiry_display.short_description = 'Days Until Expiry'
    
    def document_preview_1(self, obj):
        """Preview first supporting document."""
        if obj.supporting_document_1:
            return format_html('<a href="{}" target="_blank">📄 View Document 1</a>', 
                             obj.supporting_document_1.url)
        return "No document"
    document_preview_1.short_description = 'Document 1'
    
    def document_preview_2(self, obj):
        """Preview second supporting document."""
        if obj.supporting_document_2:
            return format_html('<a href="{}" target="_blank">📄 View Document 2</a>', 
                             obj.supporting_document_2.url)
        return "No document"
    document_preview_2.short_description = 'Document 2'
    
    def document_preview_3(self, obj):
        """Preview third supporting document."""
        if obj.supporting_document_3:
            return format_html('<a href="{}" target="_blank">📄 View Document 3</a>', 
                             obj.supporting_document_3.url)
        return "No document"
    document_preview_3.short_description = 'Document 3'
    
    def approve_licenses(self, request, queryset):
        """Bulk approve license applications."""
        count = 0
        for license in queryset.filter(status__in=['pending', 'under_review']):
            license.approve(request.user, valid_months=12, notes='Approved by admin')
            count += 1
        self.message_user(request, f"✓ {count} license(s) approved successfully.")
    approve_licenses.short_description = "✓ Approve selected licenses (12 months validity)"
    
    def reject_licenses(self, request, queryset):
        """Bulk reject license applications."""
        count = 0
        for license in queryset.filter(status__in=['pending', 'under_review', 'additional_info_required']):
            license.reject(request.user, 'Rejected by admin - application not approved')
            count += 1
        self.message_user(request, f"✗ {count} license(s) rejected.")
    reject_licenses.short_description = "✗ Reject selected licenses"
    
    def request_additional_info_action(self, request, queryset):
        """Request additional info from applicants."""
        count = 0
        for license in queryset.filter(status__in=['pending', 'under_review']):
            license.request_additional_info(request.user, 'Please provide additional documentation.')
            count += 1
        self.message_user(request, f"⚠ Additional info requested for {count} license(s).")
    request_additional_info_action.short_description = "⚠ Request additional info"
    
    def suspend_licenses(self, request, queryset):
        """Suspend approved licenses."""
        count = 0
        for license in queryset.filter(status='approved'):
            license.suspend(request.user, 'Suspended by admin for review')
            count += 1
        self.message_user(request, f"⏸ {count} license(s) suspended.")
    suspend_licenses.short_description = "⏸ Suspend selected licenses"
    
    def revoke_licenses(self, request, queryset):
        """Revoke licenses permanently."""
        count = 0
        for license in queryset.filter(status__in=['approved', 'suspended']):
            license.revoke(request.user, 'Revoked by admin')
            count += 1
        self.message_user(request, f"🚫 {count} license(s) revoked.")
    revoke_licenses.short_description = "🚫 Revoke selected licenses"
