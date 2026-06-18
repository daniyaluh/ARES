"""
Forms for the Products app - Robot/Product creation and management.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Robot, Category, ProductTag


class ProductForm(forms.ModelForm):
    """Form for creating/editing base Product."""
    
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'short_description',
            'category', 'price', 'compare_at_price',
            'stock_quantity', 'shipping_type',
            'is_digital', 'digital_file',
            'status', 'is_featured',
            'meta_title', 'meta_description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'placeholder': 'Enter robot name/title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'rows': 6,
                'placeholder': 'Detailed description of the robot...'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'rows': 2,
                'placeholder': 'Brief description for listings'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'compare_at_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'Original price (optional)',
                'step': '0.01',
                'min': '0'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'min': '0'
            }),
            'shipping_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'SEO title (optional)'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'rows': 2,
                'placeholder': 'SEO description (optional)'
            }),
        }


class RobotForm(forms.ModelForm):
    """Form for creating/editing Robot details."""
    
    class Meta:
        model = Robot
        fields = [
            'robot_type', 'model_number', 'manufacturer', 'year_manufactured',
            'weight_kg', 'dimensions_length', 'dimensions_width', 'dimensions_height',
            'max_speed_kmh', 'max_altitude_m', 'max_payload_kg',
            'operating_temperature_min', 'operating_temperature_max',
            'requires_verification', 'is_restricted', 'is_companion',
            'classification_tag', 'required_clearance_priority', 'required_license',
        ]
        widgets = {
            'robot_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime'
            }),
            'model_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'e.g., MK-IV-2025'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'Manufacturer name'
            }),
            'year_manufactured': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': '2025',
                'min': '1990',
                'max': '2030'
            }),
            'weight_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'Weight in kg',
                'step': '0.01'
            }),
            'dimensions_length': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'Length (cm)',
                'step': '0.1'
            }),
            'dimensions_width': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'Width (cm)',
                'step': '0.1'
            }),
            'dimensions_height': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'Height (cm)',
                'step': '0.1'
            }),
            'max_speed_kmh': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'Max speed (km/h)',
                'step': '0.1'
            }),
            'max_altitude_m': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'Max altitude (m)',
                'step': '0.1'
            }),
            'max_payload_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'Max payload (kg)',
                'step': '0.01'
            }),
            'operating_temperature_min': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'Min temp (°C)'
            }),
            'operating_temperature_max': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': 'Max temp (°C)'
            }),
            'classification_tag': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime'
            }),
            'required_clearance_priority': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
                'placeholder': '0 = public, 25+ = classified',
                'min': '0',
                'max': '100'
            }),
            'required_license': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime'
            }),
        }
    
    def clean_required_clearance_priority(self):
        """Validate clearance priority based on seller permissions."""
        priority = self.cleaned_data.get('required_clearance_priority', 0)
        # Sellers can only set clearance levels up to their own clearance
        # This will be enforced in the view based on seller's verification level
        return priority


class CombinedRobotForm(forms.Form):
    """
    Combined form for creating a Robot with its associated Product.
    This simplifies the seller experience.
    """
    
    # Product fields
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
            'placeholder': 'Robot name/title'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
            'rows': 6,
            'placeholder': 'Detailed description of the robot, its capabilities, and features...'
        })
    )
    short_description = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
            'rows': 2,
            'placeholder': 'Brief description for listings (optional)'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime'
        })
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        })
    )
    stock_quantity = forms.IntegerField(
        min_value=0,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
            'min': '0'
        })
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-cyber-lime/20 file:text-cyber-lime hover:file:bg-cyber-lime/30',
            'accept': 'image/*'
        })
    )
    
    # Robot fields
    robot_type = forms.ChoiceField(
        choices=Robot.ROBOT_TYPES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime'
        })
    )
    model_number = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
            'placeholder': 'e.g., MK-IV-2025'
        })
    )
    manufacturer = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
            'placeholder': 'Manufacturer name'
        })
    )
    
    # Specifications
    weight_kg = forms.DecimalField(
        required=False,
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
            'placeholder': 'Weight (kg)',
            'step': '0.01'
        })
    )
    max_speed_kmh = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
            'placeholder': 'Max speed (km/h)',
            'step': '0.1'
        })
    )
    max_payload_kg = forms.DecimalField(
        required=False,
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
            'placeholder': 'Payload capacity (kg)',
            'step': '0.01'
        })
    )
    
    # Access Control - Based on seller's verification level
    ACCESS_LEVEL_CHOICES = [
        ('public', 'Public - Anyone can view/purchase'),
        ('age_restricted', 'Age Restricted (18+) - Companion robots'),
        ('verified', 'Verified Users Only - Requires account verification'),
        ('licensed', 'Licensed Buyers - Requires export license'),
    ]
    
    access_level = forms.ChoiceField(
        choices=ACCESS_LEVEL_CHOICES,
        initial='public',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime'
        }),
        help_text='Set who can view and purchase this robot'
    )
    
    required_license = forms.ChoiceField(
        choices=Robot.LICENSE_REQUIREMENT_CHOICES,
        initial='none',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        access_level = cleaned_data.get('access_level')
        
        # Auto-set flags based on access level
        if access_level == 'age_restricted':
            cleaned_data['is_companion'] = True
            cleaned_data['classification_tag'] = 'companion'
            cleaned_data['requires_verification'] = True
            cleaned_data['required_clearance_priority'] = 0
        elif access_level == 'verified':
            cleaned_data['is_companion'] = False
            cleaned_data['classification_tag'] = 'none'
            cleaned_data['requires_verification'] = True
            cleaned_data['required_clearance_priority'] = 0
        elif access_level == 'licensed':
            cleaned_data['is_companion'] = False
            cleaned_data['classification_tag'] = 'controlled'
            cleaned_data['requires_verification'] = True
            cleaned_data['required_clearance_priority'] = 10
        else:  # public
            cleaned_data['is_companion'] = False
            cleaned_data['classification_tag'] = 'none'
            cleaned_data['requires_verification'] = False
            cleaned_data['required_clearance_priority'] = 0
        
        return cleaned_data
    
    def save(self, seller):
        """Create Product and Robot objects."""
        from django.utils.text import slugify
        
        data = self.cleaned_data
        
        # Create Product
        product = Product.objects.create(
            seller=seller,
            title=data['title'],
            description=data['description'],
            short_description=data.get('short_description', ''),
            category=data['category'],
            price=data['price'],
            stock_quantity=data['stock_quantity'],
            status='pending',  # All new products need approval
            shipping_type='physical',
        )
        
        # Handle image upload
        if data.get('image'):
            # We'll handle this via ProductImage model or directly on product
            pass
        
        # Create Robot
        robot = Robot.objects.create(
            product=product,
            robot_type=data['robot_type'],
            model_number=data.get('model_number', ''),
            manufacturer=data['manufacturer'],
            weight_kg=data.get('weight_kg'),
            max_speed_kmh=data.get('max_speed_kmh'),
            max_payload_kg=data.get('max_payload_kg'),
            requires_verification=data.get('requires_verification', False),
            is_companion=data.get('is_companion', False),
            classification_tag=data.get('classification_tag', 'none'),
            required_clearance_priority=data.get('required_clearance_priority', 0),
            required_license=data['required_license'],
            is_restricted=False,  # Only admin/staff can set this for military
        )
        
        return product, robot


class StaffProductReviewForm(forms.Form):
    """Form for staff to review and approve/reject products."""
    
    ACTION_CHOICES = [
        ('approve', 'Approve - Make product active'),
        ('reject', 'Reject - Ban product'),
        ('request_changes', 'Request Changes - Send back to seller'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'text-cyber-lime focus:ring-cyber-lime'
        })
    )
    
    review_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white font-mono focus:border-cyber-lime',
            'rows': 4,
            'placeholder': 'Notes for the seller (required if requesting changes or rejecting)'
        })
    )
    
    # Staff can upgrade access level for verified sellers
    upgrade_to_military = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-5 h-5 rounded border-slate-600 bg-slate-800 text-cyber-lime focus:ring-cyber-lime'
        }),
        help_text='Allow this product to be classified as military-grade (restricted)'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        notes = cleaned_data.get('review_notes')
        
        if action in ['reject', 'request_changes'] and not notes:
            raise ValidationError({
                'review_notes': 'Please provide notes explaining why the product was rejected or needs changes.'
            })
        
        return cleaned_data
