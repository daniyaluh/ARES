"""
Examples of using the security decorators and middleware.
This file demonstrates proper usage patterns.
"""

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from verification.security import (
    clearance_required,
    military_clearance_required,
    top_secret_clearance_required,
    restricted_access_required,
    can_access_military_robots,
    can_access_export_controlled,
    class_clearance_required,
)
from django.utils.decorators import method_decorator


# ============================================================================
# Example 1: Function-based view with TOP_SECRET clearance
# ============================================================================

@top_secret_clearance_required()
def classified_robot_specs(request, robot_id):
    """
    View that requires TOP_SECRET clearance.
    """
    # Only users with TOP_SECRET or higher clearance can access
    return render(request, 'robots/classified_specs.html', {
        'robot_id': robot_id
    })


# ============================================================================
# Example 2: Function-based view with custom clearance level
# ============================================================================

@clearance_required(level='secret')
def sensitive_order_details(request, order_id):
    """
    View that requires SECRET clearance.
    """
    return render(request, 'orders/sensitive_details.html', {
        'order_id': order_id
    })


# ============================================================================
# Example 3: API endpoint with JSON response
# ============================================================================

@clearance_required(level='military', api_response=True)
def military_robots_api(request):
    """
    API endpoint that returns JSON instead of redirecting.
    """
    from django.http import JsonResponse
    # Your API logic here
    return JsonResponse({'robots': []})


# ============================================================================
# Example 4: Class-based view with clearance requirement
# ============================================================================

@method_decorator(clearance_required(level='top_secret'), name='dispatch')
class ClassifiedDocumentsView(ListView):
    """
    Class-based view requiring TOP_SECRET clearance.
    """
    model = None  # Your model here
    template_name = 'documents/classified_list.html'
    
    def get_queryset(self):
        # Only users with TOP_SECRET clearance reach here
        return super().get_queryset()


# ============================================================================
# Example 5: Using the class decorator
# ============================================================================

@class_clearance_required(level='military')
class MilitaryRobotsView(ListView):
    """
    Alternative way to add clearance to class-based views.
    """
    model = None
    template_name = 'robots/military_list.html'


# ============================================================================
# Example 6: Permission-based decorator
# ============================================================================

@can_access_military_robots
def military_robot_detail(request, robot_id):
    """
    View that checks if user can access military robots.
    """
    return render(request, 'robots/military_detail.html', {
        'robot_id': robot_id
    })


# ============================================================================
# Example 7: Export-controlled products
# ============================================================================

@can_access_export_controlled
def export_controlled_product(request, product_id):
    """
    View for export-controlled products.
    """
    return render(request, 'products/export_controlled.html', {
        'product_id': product_id
    })


# ============================================================================
# Example 8: Restricted access (any clearance above 'none')
# ============================================================================

@restricted_access_required()
def restricted_dashboard(request):
    """
    View that requires any form of verification.
    """
    return render(request, 'dashboard/restricted.html')


# ============================================================================
# Example 9: Combining with other decorators
# ============================================================================

from django.contrib.auth.decorators import login_required

@login_required
@clearance_required(level='secret')
def combined_protection_view(request):
    """
    View with both authentication and clearance checks.
    """
    return render(request, 'protected/view.html')


# ============================================================================
# Example 10: Custom redirect URL
# ============================================================================

@clearance_required(level='top_secret', redirect_url='verification:request')
def custom_redirect_view(request):
    """
    View that redirects to custom URL if clearance insufficient.
    """
    return render(request, 'protected/view.html')









