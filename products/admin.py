from django.contrib import admin
from .models import (
    Category,
    Product,
    Robot,
    RobotSpecification,
    AISystemDetails,
    PowerSystem,
    UsageRestriction,
    ProductGallery,
    ProductVariant,
    ProductTag,
    ProductReview,
    ProductFavorite,
    ProductView
)


class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    fields = ('media_type', 'image', 'alt_text', 'order', 'is_primary', 'is_active')


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class RobotSpecificationInline(admin.StackedInline):
    model = RobotSpecification
    can_delete = False


class AISystemDetailsInline(admin.StackedInline):
    model = AISystemDetails
    can_delete = False


class PowerSystemInline(admin.StackedInline):
    model = PowerSystem
    can_delete = False


class UsageRestrictionInline(admin.StackedInline):
    model = UsageRestriction
    can_delete = False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'price', 'status', 'stock_quantity', 'rating_average', 'created_at')
    list_filter = ('status', 'category', 'is_digital', 'is_featured', 'is_bestseller')
    search_fields = ('title', 'description', 'seller__username', 'seller__email')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at', 'updated_at', 'published_at', 'view_count', 'order_count', 'rating_average', 'rating_count')
    
    fieldsets = (
        (None, {'fields': ('id', 'seller', 'title', 'slug', 'description', 'short_description')}),
        ('Categorization', {'fields': ('category', 'tags')}),
        ('Pricing', {'fields': ('price', 'compare_at_price', 'currency')}),
        ('Inventory', {'fields': ('stock_quantity', 'low_stock_threshold', 'track_inventory', 'allow_backorders')}),
        ('Shipping', {'fields': ('shipping_type', 'weight', 'weight_unit')}),
        ('Digital Product', {'fields': ('is_digital', 'digital_file', 'download_limit', 'download_expiry_days')}),
        ('Status', {'fields': ('status', 'visibility', 'is_featured', 'is_bestseller')}),
        ('Statistics', {'fields': ('view_count', 'order_count', 'rating_average', 'rating_count')}),
        ('SEO', {'fields': ('meta_title', 'meta_description')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'published_at'), 'classes': ('collapse',)}),
    )
    
    inlines = [ProductGalleryInline, ProductVariantInline]
    filter_horizontal = ('tags',)


@admin.register(Robot)
class RobotAdmin(admin.ModelAdmin):
    list_display = ('product', 'manufacturer', 'model_number', 'robot_type', 'requires_verification', 'is_restricted', 'is_companion', 'classification_tag', 'required_license', 'created_at')
    list_filter = ('robot_type', 'requires_verification', 'is_restricted', 'is_companion', 'classification_tag', 'required_license', 'manufacturer')
    search_fields = ('product__title', 'manufacturer', 'model_number', 'product__seller__username')
    raw_id_fields = ('product',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [RobotSpecificationInline, AISystemDetailsInline, PowerSystemInline, UsageRestrictionInline]
    
    fieldsets = (
        (None, {'fields': ('id', 'product', 'robot_type', 'model_number', 'manufacturer', 'year_manufactured')}),
        ('Physical Specs', {'fields': ('weight_kg', 'dimensions_length', 'dimensions_width', 'dimensions_height')}),
        ('Capabilities', {'fields': ('max_speed_kmh', 'max_altitude_m', 'max_payload_kg', 'operating_temperature_min', 'operating_temperature_max')}),
        ('Certifications', {'fields': ('certifications', 'compliance_standards', 'serial_number_format')}),
        ('Access & Classification', {
            'fields': ('requires_verification', 'is_restricted', 'is_companion', 'classification_tag', 'required_clearance_priority'),
            'description': '⚠️ Check "Is restricted" for Military Grade robots. Check "Is companion" for Age Restricted (18+) robots.'
        }),
        ('License Requirements', {
            'fields': ('required_license',),
            'description': '📋 Select the license type required to purchase this robot. Users must have an approved license of this type.'
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(RobotSpecification)
class RobotSpecificationAdmin(admin.ModelAdmin):
    list_display = ('robot', 'cpu_model', 'ram_gb', 'camera_resolution', 'operating_system')
    search_fields = ('robot__product__title', 'cpu_model', 'operating_system')
    raw_id_fields = ('robot',)


@admin.register(AISystemDetails)
class AISystemDetailsAdmin(admin.ModelAdmin):
    list_display = ('robot', 'has_autonomous_navigation', 'has_object_recognition', 'model_framework', 'accuracy_percentage')
    list_filter = ('has_autonomous_navigation', 'has_object_recognition', 'model_framework', 'edge_inference')
    search_fields = ('robot__product__title', 'model_name', 'model_framework')
    raw_id_fields = ('robot',)


@admin.register(PowerSystem)
class PowerSystemAdmin(admin.ModelAdmin):
    list_display = ('robot', 'battery_type', 'battery_capacity_mah', 'operating_time_minutes', 'charging_time_minutes')
    list_filter = ('battery_type', 'has_fast_charging', 'supports_wireless_charging')
    search_fields = ('robot__product__title',)
    raw_id_fields = ('robot',)


@admin.register(UsageRestriction)
class UsageRestrictionAdmin(admin.ModelAdmin):
    list_display = ('robot', 'restriction_level', 'requires_verification', 'minimum_age', 'requires_export_license', 'military_use_allowed')
    list_filter = ('restriction_level', 'requires_verification', 'requires_export_license', 'military_use_allowed', 'commercial_use_allowed')
    search_fields = ('robot__product__title', 'export_control_classification')
    raw_id_fields = ('robot',)


@admin.register(ProductGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = ('product', 'media_type', 'is_primary', 'order', 'is_active', 'created_at')
    list_filter = ('media_type', 'is_primary', 'is_active')
    search_fields = ('product__title', 'alt_text', 'caption')
    raw_id_fields = ('product',)


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', 'is_featured', 'usage_count', 'is_active', 'created_at')
    list_filter = ('is_featured', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_verified_purchase', 'is_approved', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'is_featured')
    search_fields = ('product__title', 'user__username', 'comment', 'title')
    raw_id_fields = ('product', 'user')  # 'order' commented until orders app is created
    readonly_fields = ('helpful_count', 'not_helpful_count')


@admin.register(ProductFavorite)
class ProductFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'priority', 'is_public', 'reminder_date', 'created_at')
    list_filter = ('priority', 'is_public')
    search_fields = ('user__username', 'product__title', 'notes', 'tags')
    raw_id_fields = ('user', 'product')


@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'view_type', 'duration_seconds', 'ip_address', 'created_at')
    list_filter = ('view_type', 'created_at')
    search_fields = ('product__title', 'user__username', 'ip_address', 'session_key')
    raw_id_fields = ('product', 'user')
    readonly_fields = ('product', 'user', 'session_key', 'ip_address', 'user_agent', 'referrer', 'created_at')
