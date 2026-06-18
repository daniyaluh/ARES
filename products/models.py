from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone
import uuid


class Category(models.Model):
    """
    Product categories with support for hierarchical structure.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For icon class names
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    # Hierarchical structure
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    
    # Display order
    order = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        db_table = 'products_category'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['is_featured', 'order']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def full_path(self):
        """Returns full category path including parents."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class Product(models.Model):
    """
    Main product model for the ARES marketplace.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
        ('banned', 'Banned'),
    ]
    
    SHIPPING_TYPES = [
        ('digital', 'Digital Delivery'),
        ('physical', 'Physical Shipping'),
        ('both', 'Digital & Physical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products'
    )
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    tags = models.ManyToManyField('ProductTag', blank=True, related_name='products')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Original price for showing discounts"
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    track_inventory = models.BooleanField(default=True)
    allow_backorders = models.BooleanField(default=False)
    
    # Shipping
    shipping_type = models.CharField(max_length=20, choices=SHIPPING_TYPES, default='digital')
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    weight_unit = models.CharField(max_length=10, default='g')  # g, kg, oz, lb
    
    # Digital Product
    is_digital = models.BooleanField(default=True)
    digital_file = models.FileField(upload_to='digital_products/', blank=True, null=True)
    download_limit = models.PositiveIntegerField(default=5)
    download_expiry_days = models.PositiveIntegerField(default=30)
    
    # Status and Visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    visibility = models.BooleanField(default=True)
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    order_count = models.PositiveIntegerField(default=0)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.PositiveIntegerField(default=0)
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
        db_table = 'products_product'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'visibility']),
            models.Index(fields=['category']),
            models.Index(fields=['seller']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_featured', '-rating_average']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        return self.track_inventory and self.stock_quantity <= self.low_stock_threshold
    
    @property
    def discount_percentage(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0


class Robot(models.Model):
    """
    Specialized Robot model for the ARES marketplace.
    Represents autonomous systems from consumer drones to military-grade hardware.
    """
    
    ROBOT_TYPES = [
        ('consumer_drone', 'Consumer Drone'),
        ('commercial_drone', 'Commercial Drone'),
        ('industrial_robot', 'Industrial Robot'),
        ('service_robot', 'Service Robot'),
        ('military_autonomous', 'Military Autonomous System'),
        ('research_platform', 'Research Platform'),
        ('medical_robot', 'Medical Robot'),
        ('agricultural_robot', 'Agricultural Robot'),
        ('companion_humanoid', 'Companion Humanoid'),
    ]
    
    CLASSIFICATION_TAGS = [
        ('none', 'None'),
        ('restricted', 'Restricted'),  # Military grade only
        ('classified', 'Classified'),  # High clearance required (25+)
        ('companion', 'Companion'),    # 18+ companion robots
        ('controlled', 'Controlled'),  # Export controlled
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='robot',
        help_text="Link to base product"
    )
    
    # Robot Classification
    robot_type = models.CharField(max_length=30, choices=ROBOT_TYPES)
    model_number = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=200)
    year_manufactured = models.PositiveIntegerField(null=True, blank=True)
    
    # Physical Specifications
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    dimensions_length = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="cm")
    dimensions_width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="cm")
    dimensions_height = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="cm")
    
    # Capabilities
    max_speed_kmh = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    max_altitude_m = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    max_payload_kg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    operating_temperature_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="°C")
    operating_temperature_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="°C")
    
    # Certifications
    certifications = models.JSONField(default=list, blank=True, help_text="List of certification IDs")
    compliance_standards = models.JSONField(default=list, blank=True, help_text="ISO, CE, FCC, etc.")
    
    # Metadata
    serial_number_format = models.CharField(max_length=50, blank=True, help_text="Format pattern for serial numbers")
    requires_verification = models.BooleanField(default=False, help_text="Requires Trust & Verification")
    is_restricted = models.BooleanField(default=False, help_text="Restricted hardware requiring clearance (military grade)")
    
    # Classification Tags
    is_companion = models.BooleanField(default=False, help_text="Companion/humanoid robot (18+ age verification)")
    classification_tag = models.CharField(
        max_length=20,
        choices=CLASSIFICATION_TAGS,
        default='none',
        help_text="Display classification tag"
    )
    required_clearance_priority = models.PositiveIntegerField(
        default=0,
        help_text="Minimum clearance priority level required (0=none, 25+=classified)"
    )
    
    # License Requirements
    LICENSE_REQUIREMENT_CHOICES = [
        ('none', 'No License Required'),
        ('individual', 'Individual Export License'),
        ('commercial', 'Commercial Export License'),
        ('government', 'Government Export License'),
        ('defense_contractor', 'Defense Contractor License'),
        ('research', 'Research & Development License'),
        ('reseller', 'Authorized Reseller License'),
        ('companion_18plus', 'Companion Robot License (18+)'),
    ]
    required_license = models.CharField(
        max_length=30,
        choices=LICENSE_REQUIREMENT_CHOICES,
        default='none',
        help_text="Type of license required to purchase this robot"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_robot'
        verbose_name = 'robot'
        verbose_name_plural = 'robots'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['robot_type']),
            models.Index(fields=['manufacturer']),
            models.Index(fields=['requires_verification', 'is_restricted']),
            models.Index(fields=['is_companion', 'classification_tag']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.manufacturer} {self.model_number or self.product.title}"
    
    @property
    def display_tag(self):
        """
        Returns the appropriate classification tag for display.
        Priority: Companion > Restricted (Military) > Classified > Controlled > None
        """
        if self.is_companion or self.robot_type == 'companion_humanoid':
            return 'companion'
        if self.is_restricted and self.robot_type == 'military_autonomous':
            return 'restricted'
        if self.required_clearance_priority >= 25:
            return 'classified'
        if self.classification_tag != 'none':
            return self.classification_tag
        return 'none'
    
    @property
    def display_tag_info(self):
        """
        Returns tag display info (label, color classes) for templates.
        """
        tag = self.display_tag
        tag_info = {
            'companion': {
                'label': 'COMPANION',
                'bg_class': 'bg-pink-500/20',
                'text_class': 'text-pink-400',
                'border_class': 'border-pink-500/50',
                'icon': '♥',
            },
            'restricted': {
                'label': 'HMAAN Needed',
                'bg_class': 'bg-red-500/20',
                'text_class': 'text-red-400',
                'border_class': 'border-red-500/50',
                'icon': '',
            },
            'classified': {
                'label': 'CLASSIFIED',
                'bg_class': 'bg-amber-500/20',
                'text_class': 'text-amber-400',
                'border_class': 'border-amber-500/50',
                'icon': '🔒',
            },
            'controlled': {
                'label': 'CONTROLLED',
                'bg_class': 'bg-orange-500/20',
                'text_class': 'text-orange-400',
                'border_class': 'border-orange-500/50',
                'icon': '⚠',
            },
            'none': {
                'label': '',
                'bg_class': '',
                'text_class': '',
                'border_class': '',
                'icon': '',
            },
        }
        return tag_info.get(tag, tag_info['none'])
    
    @property
    def requires_license(self):
        """Check if this robot requires a license to purchase."""
        return self.required_license != 'none'
    
    @property
    def license_requirement_info(self):
        """Get display info for the required license."""
        if not self.requires_license:
            return None
        
        license_info = {
            'individual': {
                'label': 'Individual Export License Required',
                'short_label': 'EXPORT LICENSE',
                'bg_class': 'bg-blue-500/20',
                'text_class': 'text-blue-400',
                'description': 'You need an approved Individual Export License to purchase this product.',
            },
            'commercial': {
                'label': 'Commercial Export License Required',
                'short_label': 'COMMERCIAL LICENSE',
                'bg_class': 'bg-blue-500/20',
                'text_class': 'text-blue-400',
                'description': 'You need an approved Commercial Export License to purchase this product.',
            },
            'government': {
                'label': 'Government Export License Required',
                'short_label': 'GOV LICENSE',
                'bg_class': 'bg-purple-500/20',
                'text_class': 'text-purple-400',
                'description': 'Government authorization required to purchase this product.',
            },
            'defense_contractor': {
                'label': 'Defense Contractor License Required',
                'short_label': 'DEF. CONTRACTOR',
                'bg_class': 'bg-red-500/20',
                'text_class': 'text-red-400',
                'description': 'You must be an authorized defense contractor to purchase this product.',
            },
            'research': {
                'label': 'Research License Required',
                'short_label': 'RESEARCH LICENSE',
                'bg_class': 'bg-cyan-500/20',
                'text_class': 'text-cyan-400',
                'description': 'You need an approved Research & Development License to purchase this product.',
            },
            'reseller': {
                'label': 'Reseller License Required',
                'short_label': 'RESELLER LICENSE',
                'bg_class': 'bg-green-500/20',
                'text_class': 'text-green-400',
                'description': 'You must be an authorized reseller to purchase this product.',
            },
            'companion_18plus': {
                'label': 'Companion Robot License (18+) Required',
                'short_label': '18+ LICENSE',
                'bg_class': 'bg-pink-500/20',
                'text_class': 'text-pink-400',
                'description': 'You must be 18+ and have an approved Companion Robot License to purchase this product.',
            },
        }
        return license_info.get(self.required_license, None)
    
    def user_has_valid_license(self, user):
        """
        Check if a user has a valid license for this robot.
        
        Logic:
        - If robot.required_license is 'none', no specific license check is needed here.
          (The general export license check happens via usage_restriction.requires_export_license)
        - If robot.required_license is set to a specific type, user needs THAT specific license.
        """
        if not self.requires_license:
            return True
        
        if not user or not user.is_authenticated:
            return False
        
        # Import here to avoid circular import
        from verification.models import ExportLicense
        
        # Check if user has a valid license of the required type
        valid_license = ExportLicense.objects.filter(
            user=user,
            license_type=self.required_license,
            status='approved',
            valid_from__lte=timezone.now().date(),
            valid_until__gte=timezone.now().date()
        ).first()
        
        if valid_license:
            # Check if this specific robot is covered
            if valid_license.allowed_product_ids:
                # If specific products are listed, check if this robot's product is in the list
                return str(self.product.id) in valid_license.allowed_product_ids or str(self.id) in valid_license.allowed_product_ids
            # Empty list means all products of this license type are covered
            return True
        
        return False
    
    def user_has_any_valid_export_license(self, user):
        """
        Check if a user has ANY valid export license.
        Used when usage_restriction.requires_export_license=True but no specific license type is required.
        """
        if not user or not user.is_authenticated:
            return False
        
        # Import here to avoid circular import
        from verification.models import ExportLicense
        
        # Check if user has any valid approved export license
        return ExportLicense.objects.filter(
            user=user,
            status='approved',
            valid_from__lte=timezone.now().date(),
            valid_until__gte=timezone.now().date()
        ).exists()


class RobotSpecification(models.Model):
    """
    Detailed technical specifications for robots.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    robot = models.OneToOneField(Robot, on_delete=models.CASCADE, related_name='specifications')
    
    # Processing & Computing
    cpu_model = models.CharField(max_length=100, blank=True)
    cpu_cores = models.PositiveIntegerField(null=True, blank=True)
    ram_gb = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    storage_gb = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    gpu_model = models.CharField(max_length=100, blank=True)
    
    # Sensors
    camera_resolution = models.CharField(max_length=50, blank=True, help_text="e.g., '4K', '1080p'")
    camera_count = models.PositiveIntegerField(default=1)
    lidar_enabled = models.BooleanField(default=False)
    radar_enabled = models.BooleanField(default=False)
    gps_enabled = models.BooleanField(default=True)
    imu_enabled = models.BooleanField(default=True)
    sensor_list = models.JSONField(default=list, blank=True, help_text="List of all sensors")
    
    # Communication
    wifi_standard = models.CharField(max_length=20, blank=True, help_text="WiFi 6, 5G, etc.")
    bluetooth_version = models.CharField(max_length=20, blank=True)
    cellular_support = models.BooleanField(default=False)
    communication_protocols = models.JSONField(default=list, blank=True)
    
    # Actuators & Motors
    motor_count = models.PositiveIntegerField(null=True, blank=True)
    motor_type = models.CharField(max_length=100, blank=True)
    servo_count = models.PositiveIntegerField(null=True, blank=True)
    
    # Software
    operating_system = models.CharField(max_length=100, blank=True)
    sdk_available = models.BooleanField(default=False)
    api_documentation_url = models.URLField(blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    
    # Additional Specs
    additional_specs = models.JSONField(default=dict, blank=True, help_text="Flexible field for other specs")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_robot_specification'
        verbose_name = 'robot specification'
        verbose_name_plural = 'robot specifications'
        indexes = [
            models.Index(fields=['robot']),
        ]
    
    def __str__(self):
        return f"Specifications for {self.robot}"


class AISystemDetails(models.Model):
    """
    AI and Machine Learning system details for autonomous robots.
    """
    
    AI_TYPES = [
        ('reinforcement_learning', 'Reinforcement Learning'),
        ('supervised_learning', 'Supervised Learning'),
        ('unsupervised_learning', 'Unsupervised Learning'),
        ('computer_vision', 'Computer Vision'),
        ('nlp', 'Natural Language Processing'),
        ('sensor_fusion', 'Sensor Fusion'),
        ('path_planning', 'Path Planning'),
        ('object_detection', 'Object Detection'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    robot = models.OneToOneField(Robot, on_delete=models.CASCADE, related_name='ai_system')
    
    # AI Capabilities
    ai_types = models.JSONField(default=list, blank=True, help_text="List of AI_TYPE choices")
    has_autonomous_navigation = models.BooleanField(default=False)
    has_object_recognition = models.BooleanField(default=False)
    has_speech_recognition = models.BooleanField(default=False)
    has_decision_making = models.BooleanField(default=False)
    
    # Model Information
    model_name = models.CharField(max_length=200, blank=True)
    model_version = models.CharField(max_length=50, blank=True)
    model_framework = models.CharField(max_length=100, blank=True, help_text="TensorFlow, PyTorch, etc.")
    training_data_size = models.CharField(max_length=100, blank=True, help_text="e.g., '1M images'")
    
    # Performance Metrics
    inference_speed_ms = models.PositiveIntegerField(null=True, blank=True, help_text="Average inference time")
    accuracy_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    precision_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    recall_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Learning Capabilities
    supports_online_learning = models.BooleanField(default=False)
    supports_federated_learning = models.BooleanField(default=False)
    can_retrain = models.BooleanField(default=False)
    
    # Edge Computing
    edge_inference = models.BooleanField(default=True)
    cloud_inference = models.BooleanField(default=False)
    hybrid_inference = models.BooleanField(default=False)
    
    # Safety & Ethics
    has_explainability = models.BooleanField(default=False, help_text="AI explainability features")
    bias_mitigation = models.BooleanField(default=False)
    safety_constraints = models.JSONField(default=list, blank=True)
    
    # Metadata
    ai_documentation_url = models.URLField(blank=True)
    research_paper_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_ai_system_details'
        verbose_name = 'AI system details'
        verbose_name_plural = 'AI system details'
        indexes = [
            models.Index(fields=['robot']),
            models.Index(fields=['has_autonomous_navigation']),
        ]
    
    def __str__(self):
        return f"AI System for {self.robot}"


class PowerSystem(models.Model):
    """
    Power and energy system specifications for robots.
    """
    
    BATTERY_TYPES = [
        ('lithium_ion', 'Lithium-Ion'),
        ('lithium_polymer', 'Lithium-Polymer'),
        ('nickel_metal_hydride', 'Nickel Metal Hydride'),
        ('lead_acid', 'Lead-Acid'),
        ('fuel_cell', 'Fuel Cell'),
        ('solar', 'Solar'),
        ('wired', 'Wired Power'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    robot = models.OneToOneField(Robot, on_delete=models.CASCADE, related_name='power_system')
    
    # Battery Information
    battery_type = models.CharField(max_length=30, choices=BATTERY_TYPES, blank=True)
    battery_capacity_mah = models.PositiveIntegerField(null=True, blank=True, help_text="mAh")
    battery_voltage_v = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Volts")
    battery_cells = models.PositiveIntegerField(null=True, blank=True)
    is_removable = models.BooleanField(default=True)
    
    # Runtime & Charging
    operating_time_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Typical operating time")
    max_operating_time_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum operating time")
    charging_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    charging_method = models.CharField(max_length=100, blank=True, help_text="USB-C, Wireless, etc.")
    
    # Power Consumption
    idle_power_w = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Watts")
    operating_power_w = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    peak_power_w = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    energy_efficiency_rating = models.CharField(max_length=10, blank=True, help_text="A+, A, B, etc.")
    
    # Power Management
    has_power_saving_mode = models.BooleanField(default=False)
    has_fast_charging = models.BooleanField(default=False)
    supports_wireless_charging = models.BooleanField(default=False)
    supports_solar_charging = models.BooleanField(default=False)
    
    # Additional Power Sources
    backup_battery = models.BooleanField(default=False)
    generator_compatible = models.BooleanField(default=False)
    external_power_input = models.CharField(max_length=50, blank=True, help_text="Voltage/Current requirements")
    
    # Safety
    has_overcharge_protection = models.BooleanField(default=True)
    has_short_circuit_protection = models.BooleanField(default=True)
    certification_ul = models.BooleanField(default=False, help_text="UL certification")
    certification_ce = models.BooleanField(default=False, help_text="CE certification")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_power_system'
        verbose_name = 'power system'
        verbose_name_plural = 'power systems'
        indexes = [
            models.Index(fields=['robot']),
            models.Index(fields=['battery_type']),
        ]
    
    def __str__(self):
        return f"Power System for {self.robot}"


class UsageRestriction(models.Model):
    """
    Usage restrictions, compliance, and legal requirements for robots.
    Critical for Trust & Verification engine.
    """
    
    RESTRICTION_LEVELS = [
        ('none', 'No Restrictions'),
        ('age_restricted', 'Age Restricted'),
        ('license_required', 'License Required'),
        ('clearance_required', 'Clearance Required'),
        ('military_only', 'Military Only'),
        ('export_controlled', 'Export Controlled'),
        ('banned', 'Banned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    robot = models.OneToOneField(Robot, on_delete=models.CASCADE, related_name='usage_restriction')
    
    # Restriction Level
    restriction_level = models.CharField(max_length=30, choices=RESTRICTION_LEVELS, default='none')
    requires_verification = models.BooleanField(default=False, help_text="Requires Trust & Verification approval")
    minimum_age = models.PositiveIntegerField(null=True, blank=True)
    
    # Geographic Restrictions
    allowed_countries = models.JSONField(default=list, blank=True, help_text="ISO country codes")
    restricted_countries = models.JSONField(default=list, blank=True)
    embargoed_countries = models.JSONField(default=list, blank=True)
    
    # Export Control
    export_control_classification = models.CharField(max_length=100, blank=True, help_text="ITAR, EAR, etc.")
    requires_export_license = models.BooleanField(default=False)
    dual_use = models.BooleanField(default=False, help_text="Dual-use technology")
    
    # Usage Limitations
    commercial_use_allowed = models.BooleanField(default=True)
    personal_use_allowed = models.BooleanField(default=True)
    research_use_allowed = models.BooleanField(default=True)
    military_use_allowed = models.BooleanField(default=False)
    
    # Compliance & Certifications
    fcc_id = models.CharField(max_length=100, blank=True)
    ce_marking = models.BooleanField(default=False)
    fda_approved = models.BooleanField(default=False)
    aviation_authority_approved = models.BooleanField(default=False, help_text="FAA, EASA, etc.")
    
    # Legal Requirements
    requires_insurance = models.BooleanField(default=False)
    requires_registration = models.BooleanField(default=False)
    requires_permit = models.BooleanField(default=False)
    legal_notices = models.TextField(blank=True)
    terms_of_use_url = models.URLField(blank=True)
    
    # Safety Restrictions
    restricted_airspace = models.BooleanField(default=False)
    restricted_altitude_m = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    requires_safety_training = models.BooleanField(default=False)
    
    # Metadata
    last_compliance_check = models.DateTimeField(null=True, blank=True)
    compliance_officer_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_usage_restriction'
        verbose_name = 'usage restriction'
        verbose_name_plural = 'usage restrictions'
        indexes = [
            models.Index(fields=['robot']),
            models.Index(fields=['restriction_level', 'requires_verification']),
            models.Index(fields=['requires_export_license']),
        ]
    
    def __str__(self):
        return f"Restrictions for {self.robot} - {self.restriction_level}"


class ProductGallery(models.Model):
    """
    Product gallery with images, videos, and media files.
    Renamed from ProductImage to match specification.
    """
    
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('3d_model', '3D Model'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default='image')
    image = models.ImageField(upload_to='products/gallery/', blank=True, null=True)
    video_url = models.URLField(blank=True, help_text="URL for video content")
    file = models.FileField(upload_to='products/gallery/files/', blank=True, null=True)
    
    # Image/Media Details
    alt_text = models.CharField(max_length=200, blank=True)
    caption = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    
    # Media Metadata
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="Size in bytes")
    mime_type = models.CharField(max_length=100, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_product_gallery'
        ordering = ['order', '-is_primary']
        verbose_name = 'product gallery item'
        verbose_name_plural = 'product gallery'
        indexes = [
            models.Index(fields=['product', 'order']),
            models.Index(fields=['is_primary']),
            models.Index(fields=['media_type']),
        ]
    
    def __str__(self):
        return f"{self.media_type} for {self.product.title}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary and self.media_type == 'image':
            ProductGallery.objects.filter(
                product=self.product,
                is_primary=True,
                media_type='image'
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """
    Product variants (e.g., different sizes, quantities, or options).
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    
    # Variant Information
    name = models.CharField(max_length=100)  # e.g., "10 units", "Premium", "Extended"
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    
    # Digital
    digital_file = models.FileField(upload_to='digital_products/variants/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_product_variant'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        return f"{self.product.title} - {self.name}"


class ProductTag(models.Model):
    """
    Tags for product categorization and search.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    description = models.TextField(blank=True)
    
    # Visual
    color = models.CharField(max_length=7, default='#bef264', help_text="Hex color code")
    icon = models.CharField(max_length=50, blank=True)
    
    # Metadata
    is_featured = models.BooleanField(default=False)
    usage_count = models.PositiveIntegerField(default=0, help_text="Number of products using this tag")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_product_tag'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_featured', 'usage_count']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductReview(models.Model):
    """
    Customer reviews and ratings for products.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='product_reviews'
    )
    # order = models.ForeignKey(
    #     'orders.Order',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='reviews'
    # )
    # TODO: Uncomment when orders app is created
    
    # Review Content
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=100, blank=True)
    comment = models.TextField(blank=True)
    
    # Moderation
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Seller Response
    seller_response = models.TextField(blank=True)
    seller_response_at = models.DateTimeField(null=True, blank=True)
    
    # Helpfulness
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_product_review'
        ordering = ['-created_at']
        # unique_together = ['product', 'user', 'order']  # One review per order
        # TODO: Uncomment when orders app is created
        indexes = [
            models.Index(fields=['product', 'is_approved', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['rating', '-created_at']),
        ]
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.title}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product rating average
        self._update_product_rating()
    
    def _update_product_rating(self):
        """Recalculate and update product's average rating."""
        reviews = ProductReview.objects.filter(
            product=self.product,
            is_approved=True
        )
        count = reviews.count()
        if count > 0:
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.product.rating_average = round(avg, 2)
            self.product.rating_count = count
            self.product.save(update_fields=['rating_average', 'rating_count'])


class ProductFavorite(models.Model):
    """
    User's favorite/wishlist products.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    
    # User Notes
    notes = models.TextField(blank=True, help_text="Personal notes about this product")
    priority = models.PositiveSmallIntegerField(default=0, help_text="0-10 priority level")
    reminder_date = models.DateTimeField(null=True, blank=True, help_text="Reminder to purchase")
    
    # Privacy
    is_public = models.BooleanField(default=False, help_text="Show in public wishlist")
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_product_favorite'
        unique_together = ['user', 'product']
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['product']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


class ProductView(models.Model):
    """
    Tracks product views for analytics.
    """
    
    VIEW_TYPES = [
        ('listing', 'Listing Page'),
        ('detail', 'Detail Page'),
        ('search', 'Search Result'),
        ('recommendation', 'Recommendation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_views'
    )
    
    # View Details
    view_type = models.CharField(max_length=20, choices=VIEW_TYPES, default='detail')
    duration_seconds = models.PositiveIntegerField(default=0, help_text="Time spent viewing")
    
    # Session info for anonymous users
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'products_product_view'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['view_type', '-created_at']),
            models.Index(fields=['session_key', '-created_at']),
        ]
    
    def __str__(self):
        viewer = self.user.username if self.user else 'Anonymous'
        return f"{viewer} viewed {self.product.title}"
