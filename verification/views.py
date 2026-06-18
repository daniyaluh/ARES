"""
Views for the Verification Engine.
Includes views that check clearance before allowing access to military-grade robots.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator

from products.models import Robot, Product, Category
from .models import (
    VerificationRequest,
    ClearanceLevel,
    IdentityDocument,
    Certification,
    MilitaryAffiliation,
    VerificationLog
)
from .utils import can_access_robot, is_military_grade_robot, requires_verification, get_user_clearance
from .decorators import require_robot_access, require_military_clearance
from .mixins import RobotAccessMixin, MilitaryClearanceMixin, FilterRestrictedProductsMixin
from .security import (
    clearance_required,
    military_clearance_required,
    top_secret_clearance_required,
    restricted_access_required,
)


# ============================================================================
# Product/Robot Views with Verification Checks
# ============================================================================

@require_robot_access
def robot_detail_view(request, robot_id):
    """
    View to display robot details.
    Access is controlled by the @require_robot_access decorator.
    """
    from products.models import Robot
    
    robot = get_object_or_404(
        Robot.objects.select_related('product', 'usage_restriction', 'specifications', 'ai_system', 'power_system'),
        id=robot_id
    )
    
    can_access, reason = can_access_robot(request.user, robot)
    
    context = {
        'robot': robot,
        'product': robot.product,
        'can_access': can_access,
        'is_military_grade': is_military_grade_robot(robot),
        'requires_verification': requires_verification(robot),
        'user_clearance': get_user_clearance(request.user),
    }
    
    return render(request, 'verification/robot_detail.html', context)


@require_military_clearance
def military_robots_list_view(request):
    """
    View to list all military-grade robots.
    Requires military clearance.
    """
    # Get military category and its subcategories
    military_category = Category.objects.filter(
        slug='military-grade',
        parent__isnull=True
    ).first()
    
    if military_category:
        # Get all military subcategory IDs
        subcategory_ids = list(military_category.subcategories.filter(is_active=True).values_list('id', flat=True))
        all_military_ids = [military_category.id] + subcategory_ids
        
        # Filter robots by military categories OR military robot type
        robots = Robot.objects.filter(
            Q(product__category_id__in=all_military_ids) |
            Q(robot_type='military_autonomous')
        ).select_related('product', 'usage_restriction', 'product__category').order_by('-product__created_at')
    else:
        # Fallback: only show military_autonomous type
        robots = Robot.objects.filter(
            robot_type='military_autonomous'
        ).select_related('product', 'usage_restriction', 'product__category').order_by('-product__created_at')
    
    paginator = Paginator(robots, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'robots': page_obj,
        'is_military_section': True,
        'user_clearance': get_user_clearance(request.user),
    }
    
    return render(request, 'verification/military_robots_list.html', context)


class RobotListView(FilterRestrictedProductsMixin, ListView):
    """
    List view for robots with automatic filtering of restricted products.
    """
    model = Robot
    template_name = 'verification/robot_list.html'
    context_object_name = 'robots'
    paginate_by = 24  # Show 24 per page (4x6 grid)
    
    def get_queryset(self):
        # Start with base queryset from mixin (handles permission filtering)
        queryset = super().get_queryset()
        
        # Add necessary relations
        queryset = queryset.select_related(
            'product', 'usage_restriction', 'product__category', 'product__category__parent'
        ).prefetch_related('product__gallery').order_by('-product__created_at')
        
        # Filter by category if provided
        category_id = self.request.GET.get('category')
        if category_id:
            # Include both direct category matches and subcategories
            try:
                category = Category.objects.get(id=category_id)
                # Get all subcategory IDs recursively
                subcategory_ids = list(category.subcategories.filter(is_active=True).values_list('id', flat=True))
                # Include the category itself
                all_category_ids = [category.id] + list(subcategory_ids)
                queryset = queryset.filter(product__category_id__in=all_category_ids)
            except Category.DoesNotExist:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_clearance'] = get_user_clearance(self.request.user)
        context['is_military_section'] = False
        
        # Get all main categories with subcategories for filtering
        main_categories = Category.objects.filter(
            parent__isnull=True, 
            is_active=True
        ).prefetch_related('subcategories').order_by('order')
        context['main_categories'] = main_categories
        
        # Get current category if filtering
        category_id = self.request.GET.get('category')
        if category_id:
            try:
                current_category = Category.objects.select_related('parent').get(id=category_id)
                context['current_category'] = current_category
            except Category.DoesNotExist:
                pass
        
        return context


class RobotDetailView(RobotAccessMixin, DetailView):
    """
    Detail view for robots with access control.
    """
    model = Robot
    template_name = 'verification/robot_detail.html'
    context_object_name = 'robot'
    pk_url_kwarg = 'robot_id'
    
    def get_queryset(self):
        return Robot.objects.select_related(
            'product', 'usage_restriction', 'specifications',
            'ai_system', 'power_system'
        ).prefetch_related('product__gallery', 'product__reviews')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        robot = self.get_object()
        
        # Check actual access (mixin already verified but we need the result for template)
        can_access, reason = can_access_robot(self.request.user, robot)
        
        # Get all related data
        specifications = getattr(robot, 'specifications', None)
        ai_system = getattr(robot, 'ai_system', None)
        power_system = getattr(robot, 'power_system', None)
        usage_restriction = getattr(robot, 'usage_restriction', None)
        gallery = robot.product.gallery.all().order_by('order', 'is_primary') if hasattr(robot.product, 'gallery') else []
        reviews = robot.product.reviews.filter(is_approved=True).order_by('-is_featured', '-created_at') if hasattr(robot.product, 'reviews') else []
        
        # License check
        has_valid_license = robot.user_has_valid_license(self.request.user)
        license_info = robot.license_requirement_info
        
        context.update({
            'product': robot.product,
            'can_access': can_access,
            'access_reason': reason,
            'is_military_grade': is_military_grade_robot(robot),
            'requires_verification': requires_verification(robot),
            'user_clearance': get_user_clearance(self.request.user),
            'specifications': specifications,
            'ai_system': ai_system,
            'power_system': power_system,
            'usage_restriction': usage_restriction,
            'gallery': gallery,
            'reviews': reviews,
            # License info
            'requires_license': robot.requires_license,
            'has_valid_license': has_valid_license,
            'license_info': license_info,
            'required_license_type': robot.required_license,
        })
        
        return context


@method_decorator(military_clearance_required(), name='dispatch')
class MilitaryRobotsListView(ListView):
    """
    List view for military-grade robots.
    Requires military clearance using @military_clearance_required decorator.
    """
    model = Robot
    template_name = 'verification/military_robots_list.html'
    context_object_name = 'robots'
    paginate_by = 20
    
    def get_queryset(self):
        # Get military category and its subcategories
        military_category = Category.objects.filter(
            slug='military-grade',
            parent__isnull=True
        ).first()
        
        if military_category:
            # Get all military subcategory IDs
            subcategory_ids = list(military_category.subcategories.filter(is_active=True).values_list('id', flat=True))
            all_military_ids = [military_category.id] + subcategory_ids
            
            # Filter robots by military categories OR military robot type
            return Robot.objects.filter(
                Q(product__category_id__in=all_military_ids) |
                Q(robot_type='military_autonomous')
            ).select_related('product', 'usage_restriction', 'product__category').order_by('-product__created_at')
        else:
            # Fallback: only show military_autonomous type
            return Robot.objects.filter(
                robot_type='military_autonomous'
            ).select_related('product', 'usage_restriction', 'product__category').order_by('-product__created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_military_section'] = True
        context['user_clearance'] = get_user_clearance(self.request.user)
        return context


# ============================================================================
# Verification Request Views
# ============================================================================

@login_required
def verification_request_create(request):
    """
    Create a new verification request with identity document and military affiliation.
    """
    from .forms import VerificationRequestForm, IdentityDocumentForm, MilitaryAffiliationForm
    
    if request.method == 'POST':
        form = VerificationRequestForm(request.POST, user=request.user)
        id_form = IdentityDocumentForm(request.POST, request.FILES)
        military_form = MilitaryAffiliationForm(request.POST)
        
        # Validate required forms
        if form.is_valid() and id_form.is_valid():
            # Create verification request
            verification_request = form.save(commit=False)
            verification_request.user = request.user
            verification_request.save()
            
            # Create identity document
            identity_document = id_form.save(commit=False)
            identity_document.verification_request = verification_request
            identity_document.save()
            
            # Create military affiliation (optional - only if user provided branch data)
            # Check if branch is provided in POST data
            branch = request.POST.get('branch', '').strip()
            if branch:
                # If branch is provided, validate the form
                if military_form.is_valid():
                    military_affiliation = military_form.save(commit=False)
                    military_affiliation.verification_request = verification_request
                    military_affiliation.save()
                else:
                    # If form is invalid, still continue but log it
                    pass  # Optional field, don't block submission
            
            # Create log entry
            VerificationLog.objects.create(
                verification_request=verification_request,
                user=request.user,
                action_type='request_submitted',
                description=f"Verification request submitted for {verification_request.requested_clearance}",
                performed_by=request.user,
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(
                request,
                "Verification request submitted successfully. You will be notified once it's reviewed."
            )
            return redirect('verification:request-detail', request_id=verification_request.id)
    else:
        form = VerificationRequestForm(user=request.user)
        id_form = IdentityDocumentForm()
        military_form = MilitaryAffiliationForm()
    
    clearance_levels = ClearanceLevel.objects.filter(is_active=True).order_by('priority')
    
    context = {
        'form': form,
        'id_form': id_form,
        'military_form': military_form,
        'clearance_levels': clearance_levels,
    }
    
    return render(request, 'verification/request_create.html', context)


@login_required
def verification_request_detail(request, request_id):
    """
    View details of a verification request.
    """
    verification_request = get_object_or_404(
        VerificationRequest.objects.select_related('requested_clearance', 'current_clearance', 'reviewed_by'),
        id=request_id,
        user=request.user
    )
    
    context = {
        'verification_request': verification_request,
        'identity_documents': verification_request.identity_documents.all(),
        'certifications': verification_request.certifications.all(),
        'military_affiliation': getattr(verification_request, 'military_affiliation', None),
        'logs': verification_request.logs.all()[:10],
        'user_clearance': get_user_clearance(request.user),
    }
    
    return render(request, 'verification/request_detail.html', context)


@login_required
def verification_request_list(request):
    """
    List all verification requests for the current user.
    """
    requests = VerificationRequest.objects.filter(
        user=request.user
    ).select_related('requested_clearance', 'current_clearance').order_by('-submitted_at')
    
    paginator = Paginator(requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'verification_requests': page_obj,
        'user_clearance': get_user_clearance(request.user),
    }
    
    return render(request, 'verification/request_list.html', context)


# ============================================================================
# Admin/Review Views (for staff)
# ============================================================================

@login_required
def verification_review_list(request):
    """
    List all pending verification requests for staff review.
    """
    # Allow staff, superusers, and users with access_level >= 60
    if not (request.user.is_staff or request.user.is_superuser or getattr(request.user, 'access_level', 0) >= 60):
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    requests = VerificationRequest.objects.filter(
        status__in=['pending', 'under_review']
    ).select_related('user', 'requested_clearance').order_by('-submitted_at')
    
    paginator = Paginator(requests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'verification_requests': page_obj,
    }
    
    return render(request, 'verification/review_list.html', context)


@login_required
def verification_review_detail(request, request_id):
    """
    Review a specific verification request (staff only).
    """
    # Allow staff, superusers, and users with access_level >= 60
    if not (request.user.is_staff or request.user.is_superuser or getattr(request.user, 'access_level', 0) >= 60):
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    verification_request = get_object_or_404(
        VerificationRequest.objects.select_related(
            'user', 'requested_clearance', 'current_clearance', 'reviewed_by'
        ),
        id=request_id
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        clearance_id = request.POST.get('clearance_level')
        notes = request.POST.get('notes', '')
        
        if action == 'approve' and clearance_id:
            try:
                clearance = ClearanceLevel.objects.get(id=clearance_id)
                verification_request.approve(request.user, clearance, notes)
                
                VerificationLog.objects.create(
                    verification_request=verification_request,
                    user=verification_request.user,
                    action_type='approved',
                    description=f"Verification approved with {clearance.name} clearance",
                    performed_by=request.user,
                    ip_address=request.META.get('REMOTE_ADDR'),
                )
                
                messages.success(request, "Verification request approved.")
                return redirect('verification:review-list')
            except ClearanceLevel.DoesNotExist:
                messages.error(request, "Invalid clearance level.")
        
        elif action == 'reject':
            reason = request.POST.get('rejection_reason', '')
            verification_request.reject(request.user, reason)
            
            VerificationLog.objects.create(
                verification_request=verification_request,
                user=verification_request.user,
                action_type='rejected',
                description=f"Verification rejected: {reason}",
                performed_by=request.user,
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            messages.success(request, "Verification request rejected.")
            return redirect('verification:review-list')
    
    clearance_levels = ClearanceLevel.objects.filter(is_active=True).order_by('-priority')
    
    context = {
        'verification_request': verification_request,
        'clearance_levels': clearance_levels,
        'identity_documents': verification_request.identity_documents.all(),
        'certifications': verification_request.certifications.all(),
        'military_affiliation': getattr(verification_request, 'military_affiliation', None),
        'logs': verification_request.logs.all(),
    }
    
    return render(request, 'verification/review_detail.html', context)


# Additional Verification Views
@login_required
def verification_request_update(request, request_id):
    """Update verification request."""
    verification_request = get_object_or_404(VerificationRequest, id=request_id, user=request.user)
    
    if verification_request.status != 'pending':
        messages.error(request, "Cannot update request that is not pending.")
        return redirect('verification:request-detail', request_id=request_id)
    
    if request.method == 'POST':
        verification_request.reason = request.POST.get('reason', verification_request.reason)
        verification_request.save()
        messages.success(request, "Verification request updated.")
        return redirect('verification:request-detail', request_id=request_id)
    
    return render(request, 'verification/request_edit.html', {'verification_request': verification_request})


@login_required
def verification_request_cancel(request, request_id):
    """Cancel/Withdraw verification request."""
    verification_request = get_object_or_404(
        VerificationRequest.objects.select_related('user'),
        id=request_id,
        user=request.user
    )
    
    # Can only withdraw if pending or under review
    if verification_request.status not in ['pending', 'under_review']:
        messages.error(request, "Only pending or under review requests can be withdrawn.")
        return redirect('verification:request-detail', request_id=request_id)
    
    if request.method == 'POST':
        verification_request.status = 'withdrawn'
        verification_request.save()
        
        VerificationLog.objects.create(
            verification_request=verification_request,
            user=request.user,
            action_type='withdrawn',
            description="Verification request withdrawn by user",
            performed_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        messages.success(request, "Verification request withdrawn successfully.")
        return redirect('verification:request-list')
    
    return render(request, 'verification/request_cancel.html', {'verification_request': verification_request})


@login_required
def verification_request_withdraw(request, request_id):
    """Withdraw verification request (alias for cancel)."""
    return verification_request_cancel(request, request_id)


@login_required
def verification_request_my_list(request):
    """My verification requests."""
    requests = VerificationRequest.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'verification/request_my_list.html', {'verification_requests': requests})


# Identity Documents
@login_required
def identity_document_list(request, request_id):
    """List identity documents for a verification request."""
    verification_request = get_object_or_404(VerificationRequest, id=request_id, user=request.user)
    documents = verification_request.identity_documents.all()
    return render(request, 'verification/identity_document_list.html', {
        'verification_request': verification_request,
        'documents': documents
    })


@login_required
def identity_document_create(request, request_id):
    """Create identity document."""
    verification_request = get_object_or_404(VerificationRequest, id=request_id, user=request.user)
    
    if request.method == 'POST' and request.FILES.get('front_image'):
        IdentityDocument.objects.create(
            verification_request=verification_request,
            document_type=request.POST.get('document_type', ''),
            document_number=request.POST.get('document_number', ''),
            front_image=request.FILES['front_image']
        )
        messages.success(request, "Document uploaded successfully.")
        return redirect('verification:identity-document-list', request_id=request_id)
    
    return render(request, 'verification/identity_document_create.html', {'verification_request': verification_request})


def identity_document_detail(request, document_id):
    """Identity document detail."""
    document = get_object_or_404(IdentityDocument, id=document_id)
    return render(request, 'verification/identity_document_detail.html', {'document': document})


@login_required
def identity_document_update(request, document_id):
    """Update identity document."""
    document = get_object_or_404(IdentityDocument, id=document_id, verification_request__user=request.user)
    
    if request.method == 'POST':
        document.document_number = request.POST.get('document_number', document.document_number)
        document.save()
        messages.success(request, "Document updated successfully.")
        return redirect('verification:identity-document-list', request_id=document.verification_request.id)
    
    return render(request, 'verification/identity_document_edit.html', {'document': document})


@login_required
def identity_document_delete(request, document_id):
    """Delete identity document."""
    document = get_object_or_404(IdentityDocument, id=document_id, verification_request__user=request.user)
    
    if request.method == 'POST':
        request_id = document.verification_request.id
        document.delete()
        messages.success(request, "Document deleted successfully.")
        return redirect('verification:identity-document-list', request_id=request_id)
    
    return render(request, 'verification/identity_document_delete.html', {'document': document})


# Certifications
@login_required
def certification_list(request, request_id):
    """List certifications for a verification request."""
    verification_request = get_object_or_404(VerificationRequest, id=request_id, user=request.user)
    certifications = verification_request.certifications.all()
    return render(request, 'verification/certification_list.html', {
        'verification_request': verification_request,
        'certifications': certifications
    })


@login_required
def certification_create(request, request_id):
    """Create certification."""
    verification_request = get_object_or_404(VerificationRequest, id=request_id, user=request.user)
    
    if request.method == 'POST':
        Certification.objects.create(
            verification_request=verification_request,
            certification_type=request.POST.get('certification_type', ''),
            certification_number=request.POST.get('certification_number', ''),
            issuing_organization=request.POST.get('issuing_organization', '')
        )
        messages.success(request, "Certification added successfully.")
        return redirect('verification:certification-list', request_id=request_id)
    
    return render(request, 'verification/certification_create.html', {'verification_request': verification_request})


def certification_detail(request, cert_id):
    """Certification detail."""
    cert = get_object_or_404(Certification, id=cert_id)
    return render(request, 'verification/certification_detail.html', {'cert': cert})


@login_required
def certification_update(request, cert_id):
    """Update certification."""
    cert = get_object_or_404(Certification, id=cert_id, verification_request__user=request.user)
    
    if request.method == 'POST':
        cert.certification_number = request.POST.get('certification_number', cert.certification_number)
        cert.save()
        messages.success(request, "Certification updated successfully.")
        return redirect('verification:certification-list', request_id=cert.verification_request.id)
    
    return render(request, 'verification/certification_edit.html', {'cert': cert})


@login_required
def certification_delete(request, cert_id):
    """Delete certification."""
    cert = get_object_or_404(Certification, id=cert_id, verification_request__user=request.user)
    
    if request.method == 'POST':
        request_id = cert.verification_request.id
        cert.delete()
        messages.success(request, "Certification deleted successfully.")
        return redirect('verification:certification-list', request_id=request_id)
    
    return render(request, 'verification/certification_delete.html', {'cert': cert})


# Military Affiliation
@login_required
def military_affiliation_detail(request, request_id):
    """Military affiliation detail."""
    verification_request = get_object_or_404(VerificationRequest, id=request_id, user=request.user)
    affiliation = getattr(verification_request, 'military_affiliation', None)
    return render(request, 'verification/military_affiliation_detail.html', {
        'verification_request': verification_request,
        'affiliation': affiliation
    })


@login_required
def military_affiliation_update(request, request_id):
    """Update military affiliation."""
    verification_request = get_object_or_404(VerificationRequest, id=request_id, user=request.user)
    
    if request.method == 'POST':
        affiliation, created = MilitaryAffiliation.objects.get_or_create(verification_request=verification_request)
        affiliation.branch = request.POST.get('branch', affiliation.branch)
        affiliation.save()
        messages.success(request, "Military affiliation updated.")
        return redirect('verification:military-affiliation-detail', request_id=request_id)
    
    affiliation = getattr(verification_request, 'military_affiliation', None)
    return render(request, 'verification/military_affiliation_edit.html', {
        'verification_request': verification_request,
        'affiliation': affiliation
    })


# Clearance Levels
def clearance_level_list(request):
    """List clearance levels."""
    levels = ClearanceLevel.objects.filter(is_active=True).order_by('-priority')
    return render(request, 'verification/clearance_level_list.html', {'levels': levels})


def clearance_level_detail(request, level_id):
    """Clearance level detail."""
    level = get_object_or_404(ClearanceLevel, id=level_id)
    return render(request, 'verification/clearance_level_detail.html', {'level': level})


# My Clearance
@login_required
def my_clearance_status(request):
    """My clearance status."""
    from .utils import get_user_clearance
    user_clearance = get_user_clearance(request.user)
    approved_request = VerificationRequest.objects.filter(
        user=request.user,
        status='approved',
        current_clearance__isnull=False
    ).first()
    
    return render(request, 'verification/my_clearance.html', {
        'user_clearance': user_clearance,
        'approved_request': approved_request
    })


@login_required
def clearance_renew(request):
    """Renew clearance."""
    messages.info(request, "Clearance renewal functionality coming soon.")
    return redirect('verification:my-clearance')


# Review Actions
@login_required
def verification_review_approve(request, request_id):
    """Approve verification request."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    verification_request = get_object_or_404(VerificationRequest, id=request_id)
    clearance_id = request.POST.get('clearance_level')
    
    if clearance_id:
        clearance = get_object_or_404(ClearanceLevel, id=clearance_id)
        verification_request.approve(request.user, clearance)
        messages.success(request, "Verification request approved.")
    
    return redirect('verification:review-detail', request_id=request_id)


@login_required
def verification_review_reject(request, request_id):
    """Reject verification request."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    verification_request = get_object_or_404(VerificationRequest, id=request_id)
    reason = request.POST.get('reason', '')
    verification_request.reject(request.user, reason)
    messages.success(request, "Verification request rejected.")
    return redirect('verification:review-list')


@login_required
def verification_review_assign_clearance(request, request_id):
    """Assign clearance to verification request."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    verification_request = get_object_or_404(VerificationRequest, id=request_id)
    clearance_id = request.POST.get('clearance_level')
    
    if clearance_id:
        clearance = get_object_or_404(ClearanceLevel, id=clearance_id)
        verification_request.approve(request.user, clearance)
        messages.success(request, "Clearance assigned.")
    
    return redirect('verification:review-detail', request_id=request_id)


# Verification Logs
@login_required
def verification_log_list(request):
    """List verification logs."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    logs = VerificationLog.objects.all().order_by('-created_at')[:100]
    return render(request, 'verification/verification_log_list.html', {'logs': logs})


def verification_log_detail(request, log_id):
    """Verification log detail."""
    log = get_object_or_404(VerificationLog, id=log_id)
    return render(request, 'verification/verification_log_detail.html', {'log': log})


@login_required
def verification_request_logs(request, request_id):
    """Logs for a verification request."""
    verification_request = get_object_or_404(VerificationRequest, id=request_id)
    logs = verification_request.logs.all().order_by('-created_at')
    return render(request, 'verification/verification_request_logs.html', {
        'verification_request': verification_request,
        'logs': logs
    })


# ============================================================================
# Export License Views
# ============================================================================

from .models import ExportLicense


@login_required
def export_license_list(request):
    """List user's export licenses."""
    licenses = ExportLicense.objects.filter(user=request.user).order_by('-created_at')
    
    # Get counts for different statuses
    pending_count = licenses.filter(status__in=['pending', 'under_review', 'additional_info_required']).count()
    approved_count = licenses.filter(status='approved').count()
    
    # Check for valid licenses
    valid_licenses = [l for l in licenses if l.is_valid]
    
    context = {
        'licenses': licenses,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'valid_licenses': valid_licenses,
        'has_valid_license': len(valid_licenses) > 0,
    }
    return render(request, 'verification/license_list.html', context)


@login_required
def export_license_apply(request):
    """Apply for a new export license."""
    if request.method == 'POST':
        # Create a new license application
        license = ExportLicense(
            user=request.user,
            license_type=request.POST.get('license_type', 'individual'),
            company_name=request.POST.get('company_name', ''),
            company_registration_number=request.POST.get('company_registration_number', ''),
            business_type=request.POST.get('business_type', ''),
            country=request.POST.get('country', ''),
            address=request.POST.get('address', ''),
            contact_phone=request.POST.get('contact_phone', ''),
            contact_email=request.POST.get('contact_email', request.user.email),
            purpose=request.POST.get('purpose', ''),
            justification=request.POST.get('justification', ''),
            product_categories=request.POST.get('product_categories', ''),
            end_use_statement=request.POST.get('end_use_statement', ''),
        )
        
        # Handle file uploads
        if request.FILES.get('supporting_document_1'):
            license.supporting_document_1 = request.FILES['supporting_document_1']
        if request.FILES.get('supporting_document_2'):
            license.supporting_document_2 = request.FILES['supporting_document_2']
        if request.FILES.get('supporting_document_3'):
            license.supporting_document_3 = request.FILES['supporting_document_3']
        
        # Check if submitting or saving as draft
        if request.POST.get('action') == 'submit':
            license.status = 'pending'
            license.submitted_at = timezone.now()
            license.save()
            messages.success(request, 'Your export license application has been submitted for review.')
        else:
            license.status = 'draft'
            license.save()
            messages.info(request, 'Your license application has been saved as a draft.')
        
        return redirect('verification:license-detail', license_id=license.id)
    
    # GET request - show application form
    context = {
        'license_types': ExportLicense.LICENSE_TYPES,
        'user_email': request.user.email,
    }
    return render(request, 'verification/license_apply.html', context)


@login_required
def export_license_detail(request, license_id):
    """View export license details."""
    license = get_object_or_404(ExportLicense, id=license_id, user=request.user)
    
    context = {
        'license': license,
        'is_valid': license.is_valid,
        'is_expired': license.is_expired,
        'days_until_expiry': license.days_until_expiry,
    }
    return render(request, 'verification/license_detail.html', context)


@login_required
def export_license_update(request, license_id):
    """Update a draft or additional-info-required license."""
    license = get_object_or_404(ExportLicense, id=license_id, user=request.user)
    
    # Only allow editing of drafts or when additional info is required
    if license.status not in ['draft', 'additional_info_required']:
        messages.error(request, 'This license application cannot be edited.')
        return redirect('verification:license-detail', license_id=license.id)
    
    if request.method == 'POST':
        # Update license fields
        license.license_type = request.POST.get('license_type', license.license_type)
        license.company_name = request.POST.get('company_name', license.company_name)
        license.company_registration_number = request.POST.get('company_registration_number', license.company_registration_number)
        license.business_type = request.POST.get('business_type', license.business_type)
        license.country = request.POST.get('country', license.country)
        license.address = request.POST.get('address', license.address)
        license.contact_phone = request.POST.get('contact_phone', license.contact_phone)
        license.contact_email = request.POST.get('contact_email', license.contact_email)
        license.purpose = request.POST.get('purpose', license.purpose)
        license.justification = request.POST.get('justification', license.justification)
        license.product_categories = request.POST.get('product_categories', license.product_categories)
        license.end_use_statement = request.POST.get('end_use_statement', license.end_use_statement)
        
        # Handle file uploads
        if request.FILES.get('supporting_document_1'):
            license.supporting_document_1 = request.FILES['supporting_document_1']
        if request.FILES.get('supporting_document_2'):
            license.supporting_document_2 = request.FILES['supporting_document_2']
        if request.FILES.get('supporting_document_3'):
            license.supporting_document_3 = request.FILES['supporting_document_3']
        
        # Check if submitting or saving as draft
        if request.POST.get('action') == 'submit':
            license.status = 'pending'
            license.submitted_at = timezone.now()
            license.save()
            messages.success(request, 'Your export license application has been resubmitted for review.')
        else:
            license.save()
            messages.info(request, 'Your license application has been updated.')
        
        return redirect('verification:license-detail', license_id=license.id)
    
    # GET request - show edit form
    context = {
        'license': license,
        'license_types': ExportLicense.LICENSE_TYPES,
        'is_edit': True,
    }
    return render(request, 'verification/license_apply.html', context)


@login_required
def export_license_submit(request, license_id):
    """Submit a draft license for review."""
    license = get_object_or_404(ExportLicense, id=license_id, user=request.user)
    
    if license.status == 'draft':
        license.submit()
        messages.success(request, 'Your export license application has been submitted for review.')
    else:
        messages.warning(request, 'This license has already been submitted.')
    
    return redirect('verification:license-detail', license_id=license.id)


@login_required
def export_license_withdraw(request, license_id):
    """Withdraw a pending license application."""
    license = get_object_or_404(ExportLicense, id=license_id, user=request.user)
    
    if license.status in ['pending', 'under_review', 'additional_info_required']:
        license.status = 'draft'
        license.submitted_at = None
        license.save(update_fields=['status', 'submitted_at'])
        messages.info(request, 'Your license application has been withdrawn and saved as a draft.')
    else:
        messages.warning(request, 'This license cannot be withdrawn.')
    
    return redirect('verification:license-detail', license_id=license.id)


@login_required
def staff_pending_licenses(request):
    """Staff view to see all pending license applications."""
    user = request.user
    
    # Check staff access
    if not user.is_staff and not user.is_superuser and getattr(user, 'access_level', 0) < 60:
        messages.error(request, "Access denied. Staff privileges required.")
        return redirect('home')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'pending')
    license_type_filter = request.GET.get('license_type', 'all')
    search_query = request.GET.get('q', '')
    
    # Base queryset - all licenses (not just current user's)
    licenses = ExportLicense.objects.select_related('user').order_by('-created_at')
    
    # Apply status filter
    if status_filter == 'pending':
        licenses = licenses.filter(status__in=['pending', 'under_review'])
    elif status_filter != 'all':
        licenses = licenses.filter(status=status_filter)
    
    # Apply license type filter
    if license_type_filter != 'all':
        licenses = licenses.filter(license_type=license_type_filter)
    
    # Apply search
    if search_query:
        licenses = licenses.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(company_name__icontains=search_query)
        )
    
    # Get counts for stats
    total_pending = ExportLicense.objects.filter(status__in=['pending', 'under_review']).count()
    total_approved = ExportLicense.objects.filter(status='approved').count()
    total_rejected = ExportLicense.objects.filter(status='rejected').count()
    
    context = {
        'licenses': licenses,
        'status_filter': status_filter,
        'license_type_filter': license_type_filter,
        'search_query': search_query,
        'total_pending': total_pending,
        'total_approved': total_approved,
        'total_rejected': total_rejected,
    }
    
    return render(request, 'verification/staff_pending_licenses.html', context)


@login_required
def staff_review_license(request, license_id):
    """Staff view to review and approve/reject a license application."""
    user = request.user
    
    # Check staff access
    if not user.is_staff and not user.is_superuser and getattr(user, 'access_level', 0) < 60:
        messages.error(request, "Access denied. Staff privileges required.")
        return redirect('home')
    
    license = get_object_or_404(ExportLicense, id=license_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            license.status = 'approved'
            license.reviewed_by = user
            license.reviewed_at = timezone.now()
            license.reviewer_notes = notes
            # Set expiry date (1 year from now by default)
            license.valid_from = timezone.now()
            license.valid_until = timezone.now() + timezone.timedelta(days=365)
            license.save()
            messages.success(request, f"License application for {license.user.username} has been approved.")
        
        elif action == 'reject':
            license.status = 'rejected'
            license.reviewed_by = user
            license.reviewed_at = timezone.now()
            license.reviewer_notes = notes
            license.save()
            messages.success(request, f"License application for {license.user.username} has been rejected.")
        
        elif action == 'request_info':
            license.status = 'additional_info_required'
            license.reviewer_notes = notes
            license.save()
            messages.info(request, f"Additional information requested from {license.user.username}.")
        
        return redirect('verification:staff-pending-licenses')
    
    context = {
        'license': license,
    }
    
    return render(request, 'verification/staff_review_license.html', context)
