"""
URL configuration for ares_project project.
Comprehensive URL routing for all apps.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Home view with categories
from products.models import Category

class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get main categories for homepage display
        context['main_categories'] = Category.objects.filter(
            parent__isnull=True, 
            is_active=True
        ).prefetch_related('subcategories').order_by('order')[:7]
        return context

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home
    path('', HomeView.as_view(), name='home'),
    
    # App URLs
    path('users/', include('users.urls')),
    path('products/', include('products.urls')),
    path('verification/', include('verification.urls')),
    path('orders/', include('orders.urls')),
    path('support/', include('support.urls')),
    path('analytics/', include('analytics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)
