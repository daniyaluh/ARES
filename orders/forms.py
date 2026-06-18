"""
Forms for Orders app.
"""
from django import forms
from .models import PurchaseRequest


class PurchaseRequestForm(forms.ModelForm):
    """Form for creating/updating purchase requests."""
    
    class Meta:
        model = PurchaseRequest
        fields = [
            'quantity',
            'company_name',
            'contact_name',
            'contact_phone',
            'contact_email',
            'shipping_address',
            'shipping_city',
            'shipping_state',
            'shipping_postal_code',
            'shipping_country',
            'purpose',
            'intended_use',
            'urgency',
            'notes',
            'supporting_documents',
        ]
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'min': '1',
                'max': '100',
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'placeholder': 'Company or Organization Name',
            }),
            'contact_name': forms.TextInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'placeholder': 'Primary Contact Name',
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'placeholder': '+1 (555) 123-4567',
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'placeholder': 'contact@company.com',
            }),
            'shipping_address': forms.Textarea(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'rows': 3,
                'placeholder': 'Street Address, Building, Suite, etc.',
            }),
            'shipping_city': forms.TextInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'placeholder': 'City',
            }),
            'shipping_state': forms.TextInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'placeholder': 'State/Province',
            }),
            'shipping_postal_code': forms.TextInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'placeholder': 'Postal/ZIP Code',
            }),
            'shipping_country': forms.TextInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'placeholder': 'Country',
            }),
            'purpose': forms.Select(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
            }),
            'intended_use': forms.Textarea(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'rows': 4,
                'placeholder': 'Please describe how you intend to use this robot...',
            }),
            'urgency': forms.Select(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
                'rows': 3,
                'placeholder': 'Any additional notes, special requirements, or questions...',
            }),
            'supporting_documents': forms.FileInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-cyber-lime/20 file:text-cyber-lime',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill contact email with user email
        if self.user and not self.initial.get('contact_email'):
            self.initial['contact_email'] = self.user.email
        
        # Make certain fields required
        self.fields['contact_name'].required = True
        self.fields['contact_phone'].required = True
        self.fields['shipping_address'].required = True
        self.fields['shipping_city'].required = True
        self.fields['shipping_country'].required = True
        self.fields['intended_use'].required = True
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        if quantity > 100:
            raise forms.ValidationError("Maximum quantity is 100. For larger orders, please contact us directly.")
        return quantity


class PurchaseRequestReviewForm(forms.Form):
    """Form for staff/admin to review purchase requests."""
    ACTION_CHOICES = [
        ('approve', 'Approve Request'),
        ('reject', 'Reject Request'),
        ('under_review', 'Mark Under Review'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
        })
    )
    review_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
            'rows': 3,
            'placeholder': 'Add notes for this review decision...',
        })
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white font-mono focus:border-cyber-lime focus:ring-1 focus:ring-cyber-lime',
            'rows': 3,
            'placeholder': 'If rejecting, please provide a reason...',
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if action == 'reject' and not rejection_reason:
            raise forms.ValidationError("Rejection reason is required when rejecting a request.")
        
        return cleaned_data
