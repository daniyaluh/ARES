from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class ClearanceLevel(models.Model):
    """
    Security clearance levels for accessing restricted/military-grade robots.
    """
    
    CLEARANCE_LEVELS = [
        ('none', 'No Clearance'),
        ('public', 'Public Trust'),
        ('age_restricted', 'Age Restricted (18+)'),
        ('confidential', 'Confidential'),
        ('secret', 'Secret'),
        ('top_secret', 'Top Secret'),
        ('military', 'Military Clearance'),
        ('government', 'Government Clearance'),
        ('contractor', 'Defense Contractor'),
        ('research', 'Research & Advanced Robotics'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=30, unique=True, choices=CLEARANCE_LEVELS)
    description = models.TextField(blank=True)
    
    # Access Permissions
    can_access_restricted = models.BooleanField(default=False)
    can_access_military = models.BooleanField(default=False)
    can_access_export_controlled = models.BooleanField(default=False)
    minimum_clearance_required = models.CharField(
        max_length=30,
        choices=CLEARANCE_LEVELS,
        default='none',
        help_text="Minimum clearance level required to access this level"
    )
    
    # Validity
    validity_months = models.PositiveIntegerField(default=12, help_text="Clearance validity period in months")
    requires_renewal = models.BooleanField(default=True)
    requires_background_check = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0, help_text="Higher priority = higher clearance")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'verification_clearance_level'
        verbose_name = 'clearance level'
        verbose_name_plural = 'clearance levels'
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'priority']),
        ]
    
    def __str__(self):
        return self.name


class VerificationRequest(models.Model):
    """
    User requests for verification to access restricted products.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification_requests'
    )
    
    # Request Details
    requested_clearance = models.ForeignKey(
        ClearanceLevel,
        on_delete=models.SET_NULL,
        null=True,
        related_name='verification_requests',
        help_text="Requested clearance level"
    )
    reason = models.TextField(help_text="Reason for requesting verification")
    intended_use = models.TextField(help_text="Intended use of restricted products")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_clearance = models.ForeignKey(
        ClearanceLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_clearances',
        help_text="Currently assigned clearance level"
    )
    
    # Review Process
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_verifications'
    )
    review_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Dates
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'verification_verification_request'
        verbose_name = 'verification request'
        verbose_name_plural = 'verification requests'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', '-submitted_at']),
            models.Index(fields=['requested_clearance']),
            models.Index(fields=['current_clearance']),
        ]
    
    def __str__(self):
        return f"Verification Request for {self.user.username} - {self.status}"
    
    @property
    def is_approved(self):
        return self.status == 'approved' and self.current_clearance is not None
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def approve(self, reviewer, clearance_level, notes=''):
        """Approve the verification request."""
        old_status = self.status
        self.status = 'approved'
        self.current_clearance = clearance_level
        self.reviewed_by = reviewer
        self.review_notes = notes
        self.reviewed_at = timezone.now()
        
        if clearance_level.validity_months:
            self.expires_at = timezone.now() + timezone.timedelta(days=clearance_level.validity_months * 30)
        
        # Automatically verify the user when their verification request is approved
        if not self.user.is_verified:
            self.user.is_verified = True
            self.user.save(update_fields=['is_verified'])
        
        # Store original status for signal before saving
        self._original_status = old_status
        self.save(update_fields=['status', 'current_clearance', 'reviewed_by', 'review_notes', 'reviewed_at', 'expires_at'])
    
    def reject(self, reviewer, reason):
        """Reject the verification request."""
        old_status = self.status
        self.status = 'rejected'
        self.reviewed_by = reviewer
        self.rejection_reason = reason
        self.reviewed_at = timezone.now()
        # Store original status for signal before saving
        self._original_status = old_status
        self.save(update_fields=['status', 'reviewed_by', 'rejection_reason', 'reviewed_at'])


class IdentityDocument(models.Model):
    """
    Identity documents submitted for verification.
    """
    
    DOCUMENT_TYPES = [
        ('passport', 'Passport'),
        ('drivers_license', "Driver's License"),
        ('national_id', 'National ID'),
        ('military_id', 'Military ID'),
        ('government_id', 'Government ID'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification_request = models.ForeignKey(
        VerificationRequest,
        on_delete=models.CASCADE,
        related_name='identity_documents'
    )
    
    # Document Information
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=100)
    issuing_country = models.CharField(max_length=100)
    issuing_authority = models.CharField(max_length=200, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Files (encrypted in production)
    front_image = models.ImageField(upload_to='verification/documents/', blank=True, null=True)
    back_image = models.ImageField(upload_to='verification/documents/', blank=True, null=True)
    
    # Verification Status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verification_notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'verification_identity_document'
        verbose_name = 'identity document'
        verbose_name_plural = 'identity documents'
        indexes = [
            models.Index(fields=['verification_request']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.document_type} - {self.document_number}"


class Certification(models.Model):
    """
    Professional certifications and licenses for verification.
    """
    
    CERTIFICATION_TYPES = [
        ('pilot_license', 'Pilot License'),
        ('drone_license', 'Drone Operator License'),
        ('security_clearance', 'Security Clearance'),
        ('export_license', 'Export License'),
        ('professional', 'Professional Certification'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification_request = models.ForeignKey(
        VerificationRequest,
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    
    # Certification Details
    certification_type = models.CharField(max_length=30, choices=CERTIFICATION_TYPES)
    certification_number = models.CharField(max_length=100)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Files
    certificate_file = models.FileField(upload_to='verification/certificates/', blank=True, null=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_certifications'
    )
    verification_notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'verification_certification'
        verbose_name = 'certification'
        verbose_name_plural = 'certifications'
        indexes = [
            models.Index(fields=['verification_request']),
            models.Index(fields=['certification_type', 'is_verified']),
        ]
    
    def __str__(self):
        return f"{self.certification_type} - {self.certification_number}"
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False


class MilitaryAffiliation(models.Model):
    """
    Military affiliation information for verification.
    """
    
    BRANCH_CHOICES = [
        ('army', 'Army'),
        ('navy', 'Navy'),
        ('air_force', 'Air Force'),
        ('marines', 'Marines'),
        ('coast_guard', 'Coast Guard'),
        ('reserves', 'Reserves'),
        ('national_guard', 'National Guard'),
        ('veteran', 'Veteran'),
        ('civilian_contractor', 'Civilian Contractor'),
        ('other', 'Other'),
    ]
    
    RANK_CHOICES = [
        ('enlisted', 'Enlisted'),
        ('officer', 'Officer'),
        ('warrant_officer', 'Warrant Officer'),
        ('civilian', 'Civilian'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification_request = models.OneToOneField(
        VerificationRequest,
        on_delete=models.CASCADE,
        related_name='military_affiliation'
    )
    
    # Military Information
    branch = models.CharField(max_length=30, choices=BRANCH_CHOICES, blank=True)
    rank = models.CharField(max_length=30, choices=RANK_CHOICES, blank=True)
    rank_title = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=200, blank=True)
    service_number = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active_duty = models.BooleanField(default=False)
    is_veteran = models.BooleanField(default=False)
    is_reservist = models.BooleanField(default=False)
    is_contractor = models.BooleanField(default=False)
    
    # Dates
    service_start_date = models.DateField(null=True, blank=True)
    service_end_date = models.DateField(null=True, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_military_affiliations'
    )
    verification_notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'verification_military_affiliation'
        verbose_name = 'military affiliation'
        verbose_name_plural = 'military affiliations'
        indexes = [
            models.Index(fields=['verification_request']),
            models.Index(fields=['branch', 'is_verified']),
        ]
    
    def __str__(self):
        return f"{self.branch} - {self.rank_title or self.rank}"


class VerificationLog(models.Model):
    """
    Audit log for all verification-related activities.
    """
    
    ACTION_TYPES = [
        ('request_submitted', 'Request Submitted'),
        ('document_uploaded', 'Document Uploaded'),
        ('review_started', 'Review Started'),
        ('review_completed', 'Review Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('withdrawn', 'Withdrawn'),
        ('clearance_assigned', 'Clearance Assigned'),
        ('clearance_revoked', 'Clearance Revoked'),
        ('expired', 'Expired'),
        ('renewed', 'Renewed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification_request = models.ForeignKey(
        VerificationRequest,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification_logs'
    )
    
    # Action Details
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.TextField(blank=True)
    
    # Actor
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_verification_actions'
    )
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'verification_verification_log'
        verbose_name = 'verification log'
        verbose_name_plural = 'verification logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['verification_request', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.action_type} - {self.user.username} at {self.created_at}"


class ExportLicense(models.Model):
    """
    Export License for purchasing export-controlled military-grade robots.
    Users must apply for and receive an approved license before purchasing
    export-controlled products.
    """
    
    LICENSE_TYPES = [
        ('individual', 'Individual Export License'),
        ('commercial', 'Commercial Export License'),
        ('government', 'Government Export License'),
        ('defense_contractor', 'Defense Contractor License'),
        ('research', 'Research & Development License'),
        ('reseller', 'Authorized Reseller License'),
        ('companion_18plus', 'Companion Robot License (18+)'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('additional_info_required', 'Additional Info Required'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='export_licenses'
    )
    
    # License Details
    license_type = models.CharField(max_length=30, choices=LICENSE_TYPES)
    license_number = models.CharField(max_length=50, blank=True, unique=True, null=True,
                                      help_text="Auto-generated upon approval")
    
    # Applicant Information
    company_name = models.CharField(max_length=200, blank=True,
                                    help_text="Required for commercial/government licenses")
    company_registration_number = models.CharField(max_length=100, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, help_text="Country of operation/residence")
    address = models.TextField(help_text="Full registered address")
    contact_phone = models.CharField(max_length=30)
    contact_email = models.EmailField()
    
    # Purpose & Justification
    purpose = models.TextField(help_text="Intended use of export-controlled products")
    justification = models.TextField(help_text="Why you need access to export-controlled items")
    product_categories = models.TextField(blank=True,
                                          help_text="Specific product categories or types needed")
    end_use_statement = models.TextField(blank=True,
                                         help_text="Statement of end-use for the products")
    
    # Supporting Documents
    supporting_document_1 = models.FileField(upload_to='licenses/documents/', blank=True, null=True,
                                             help_text="Business registration, ID, or other proof")
    supporting_document_2 = models.FileField(upload_to='licenses/documents/', blank=True, null=True)
    supporting_document_3 = models.FileField(upload_to='licenses/documents/', blank=True, null=True)
    
    # Status & Review
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_licenses'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, help_text="Internal notes from reviewer")
    rejection_reason = models.TextField(blank=True)
    additional_info_request = models.TextField(blank=True,
                                               help_text="Details of additional info required")
    
    # Validity
    approved_at = models.DateTimeField(null=True, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    
    # Limits & Restrictions
    max_purchase_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                             help_text="Maximum total value of purchases allowed")
    remaining_purchase_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                                   help_text="Remaining purchase value")
    allowed_product_ids = models.JSONField(default=list, blank=True,
                                           help_text="Specific product IDs this license covers (empty = all)")
    restricted_countries = models.JSONField(default=list, blank=True,
                                            help_text="Countries where products cannot be shipped")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'verification_export_license'
        verbose_name = 'export license'
        verbose_name_plural = 'export licenses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', '-submitted_at']),
            models.Index(fields=['license_number']),
            models.Index(fields=['valid_until']),
        ]
    
    def __str__(self):
        if self.license_number:
            return f"License #{self.license_number} - {self.user.username}"
        return f"License Application ({self.get_license_type_display()}) - {self.user.username}"
    
    @property
    def is_valid(self):
        """Check if the license is currently valid."""
        if self.status != 'approved':
            return False
        if not self.valid_from or not self.valid_until:
            return False
        today = timezone.now().date()
        return self.valid_from <= today <= self.valid_until
    
    @property
    def is_expired(self):
        """Check if the license has expired."""
        if not self.valid_until:
            return False
        return timezone.now().date() > self.valid_until
    
    @property
    def days_until_expiry(self):
        """Get days until license expires."""
        if not self.valid_until:
            return None
        delta = self.valid_until - timezone.now().date()
        return delta.days
    
    @property
    def has_remaining_value(self):
        """Check if there's remaining purchase value."""
        if self.remaining_purchase_value is None:
            return True  # No limit set
        return self.remaining_purchase_value > 0
    
    def generate_license_number(self):
        """Generate a unique license number."""
        import random
        import string
        prefix = {
            'individual': 'IND',
            'commercial': 'COM',
            'government': 'GOV',
            'defense_contractor': 'DEF',
            'research': 'RES',
            'reseller': 'RSL',
        }.get(self.license_type, 'LIC')
        year = timezone.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}-{year}-{random_part}"
    
    def submit(self):
        """Submit the license for review."""
        if self.status == 'draft':
            self.status = 'pending'
            self.submitted_at = timezone.now()
            self.save(update_fields=['status', 'submitted_at'])
    
    def approve(self, reviewer, valid_months=12, max_value=None, notes=''):
        """Approve the license application."""
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.approved_at = timezone.now()
        self.review_notes = notes
        self.valid_from = timezone.now().date()
        self.valid_until = timezone.now().date() + timezone.timedelta(days=valid_months * 30)
        
        if not self.license_number:
            self.license_number = self.generate_license_number()
        
        if max_value:
            self.max_purchase_value = max_value
            self.remaining_purchase_value = max_value
        
        self.save()
        
        # Send notification to user
        self._send_notification(
            'license_approved',
            'Export License Approved',
            f'Your {self.get_license_type_display()} application has been approved! '
            f'License #{self.license_number} is valid until {self.valid_until.strftime("%B %d, %Y")}.'
        )
    
    def reject(self, reviewer, reason):
        """Reject the license application."""
        self.status = 'rejected'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'rejection_reason'])
        
        # Send notification to user
        self._send_notification(
            'license_rejected',
            'Export License Application Rejected',
            f'Your {self.get_license_type_display()} application has been rejected. Reason: {reason}'
        )
    
    def suspend(self, reviewer, reason):
        """Suspend an approved license."""
        if self.status == 'approved':
            self.status = 'suspended'
            self.reviewed_by = reviewer
            self.reviewed_at = timezone.now()
            self.review_notes = f"Suspended: {reason}"
            self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'review_notes'])
            
            # Send notification to user
            self._send_notification(
                'license_suspended',
                'Export License Suspended',
                f'Your {self.get_license_type_display()} (#{self.license_number}) has been suspended. Reason: {reason}'
            )
    
    def revoke(self, reviewer, reason):
        """Revoke an approved license."""
        if self.status in ['approved', 'suspended']:
            self.status = 'revoked'
            self.reviewed_by = reviewer
            self.reviewed_at = timezone.now()
            self.review_notes = f"Revoked: {reason}"
            self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'review_notes'])
            
            # Send notification to user
            self._send_notification(
                'license_suspended',  # Use suspended type for revoked as well
                'Export License Revoked',
                f'Your {self.get_license_type_display()} (#{self.license_number}) has been revoked. Reason: {reason}'
            )
    
    def request_additional_info(self, reviewer, request_details):
        """Request additional information from applicant."""
        self.status = 'additional_info_required'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.additional_info_request = request_details
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'additional_info_request'])
        
        # Send notification to user
        self._send_notification(
            'license_info_required',
            'Additional Information Required',
            f'Your {self.get_license_type_display()} application requires additional information: {request_details}'
        )
    
    def _send_notification(self, notification_type, title, message):
        """Helper method to send notification to the license applicant."""
        from users.models import Notification
        Notification.objects.create(
            user=self.user,
            notification_type=notification_type,
            title=title,
            message=message
        )
