"""
Forms for the Verification Engine.
"""
from django import forms
from .models import VerificationRequest, IdentityDocument, Certification, MilitaryAffiliation, ClearanceLevel


class VerificationRequestForm(forms.ModelForm):
    """
    Form for creating a verification request.
    Note: ID card uploads are handled separately via IdentityDocumentForm.
    """
    class Meta:
        model = VerificationRequest
        fields = ['requested_clearance', 'reason', 'intended_use']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'intended_use': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'requested_clearance': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'requested_clearance': 'Requested Clearance Level',
            'reason': 'Reason for Request',
            'intended_use': 'Intended Use of Restricted Products',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter clearance levels based on user's current clearance
        if user:
            # Get user's current clearance
            from .utils import get_user_clearance
            current_clearance = get_user_clearance(user)
            
            if current_clearance:
                # Only show clearance levels higher than current
                self.fields['requested_clearance'].queryset = ClearanceLevel.objects.filter(
                    priority__gt=current_clearance.priority,
                    is_active=True
                ).order_by('priority')
            else:
                # Show all active clearance levels
                self.fields['requested_clearance'].queryset = ClearanceLevel.objects.filter(
                    is_active=True
                ).order_by('priority')


class IdentityDocumentForm(forms.ModelForm):
    """
    Form for uploading identity documents.
    """
    class Meta:
        model = IdentityDocument
        fields = ['document_type', 'document_number', 'issuing_country', 'issuing_authority', 
                  'issue_date', 'expiry_date', 'front_image', 'back_image']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'issuing_country': forms.TextInput(attrs={'class': 'form-control'}),
            'issuing_authority': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'front_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'required': True}),
            'back_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'document_type': 'Document Type',
            'document_number': 'Document Number',
            'issuing_country': 'Issuing Country',
            'issuing_authority': 'Issuing Authority',
            'issue_date': 'Issue Date',
            'expiry_date': 'Expiry Date',
            'front_image': 'ID Card Front Image',
            'back_image': 'ID Card Back Image',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['issuing_country'].required = True
        self.fields['document_type'].required = True
        self.fields['document_number'].required = True
        self.fields['front_image'].required = True


class CertificationForm(forms.ModelForm):
    """
    Form for uploading certifications.
    """
    class Meta:
        model = Certification
        fields = ['certification_type', 'certification_number', 'issuing_organization',
                  'issue_date', 'expiry_date', 'certificate_file']
        widgets = {
            'certification_type': forms.Select(attrs={'class': 'form-control'}),
            'certification_number': forms.TextInput(attrs={'class': 'form-control'}),
            'issuing_organization': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'certificate_file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class MilitaryAffiliationForm(forms.ModelForm):
    """
    Form for military affiliation information.
    """
    class Meta:
        model = MilitaryAffiliation
        fields = ['branch', 'rank', 'rank_title', 'unit', 'service_number',
                  'is_active_duty', 'is_veteran', 'is_reservist', 'is_contractor',
                  'service_start_date', 'service_end_date']
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'rank': forms.Select(attrs={'class': 'form-control'}),
            'rank_title': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'service_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active_duty': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_veteran': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_reservist': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_contractor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'service_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'service_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'branch': 'Branch',
            'rank': 'Rank',
            'rank_title': 'Rank Title',
            'unit': 'Unit',
            'service_number': 'Service Number',
            'is_active_duty': 'Active Duty',
            'is_veteran': 'Veteran',
            'is_reservist': 'Reservist',
            'is_contractor': 'Contractor',
            'service_start_date': 'Service Start Date',
            'service_end_date': 'Service End Date',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional since military affiliation is optional
        for field in self.fields:
            self.fields[field].required = False

