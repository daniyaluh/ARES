"""
URL patterns for Products app.
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product List/Detail (General)
    path('', views.product_list, name='product-list'),
    path('<uuid:product_id>/', views.product_detail, name='product-detail'),
    path('create/', views.product_create, name='product-create'),
    path('<uuid:product_id>/edit/', views.product_update, name='product-edit'),
    path('<uuid:product_id>/delete/', views.product_delete, name='product-delete'),
    path('<uuid:product_id>/submit-review/', views.product_submit_for_review, name='product-submit-review'),
    
    # Robot-specific URLs
    path('robots/', views.robot_list, name='robot-list'),
    path('robots/<uuid:robot_id>/', views.robot_detail, name='robot-detail'),
    path('robots/create/', views.robot_create, name='robot-create'),
    path('robots/<uuid:robot_id>/edit/', views.robot_update, name='robot-edit'),
    path('robots/<uuid:robot_id>/specifications/', views.robot_specifications, name='robot-specifications'),
    path('robots/<uuid:robot_id>/ai-details/', views.robot_ai_details, name='robot-ai-details'),
    path('robots/<uuid:robot_id>/power-system/', views.robot_power_system, name='robot-power-system'),
    path('robots/<uuid:robot_id>/restrictions/', views.robot_restrictions, name='robot-restrictions'),
    
    # Categories
    path('categories/', views.category_list, name='category-list'),
    path('categories/browse/', views.category_browse, name='category-browse'),
    path('categories/<uuid:category_id>/', views.category_detail, name='category-detail'),
    path('categories/<uuid:category_id>/products/', views.category_products, name='category-products'),
    path('categories/create/', views.category_create, name='category-create'),
    path('categories/<uuid:category_id>/edit/', views.category_update, name='category-edit'),
    
    # Product Gallery
    path('<uuid:product_id>/gallery/', views.product_gallery_list, name='product-gallery-list'),
    path('<uuid:product_id>/gallery/add/', views.product_gallery_add, name='product-gallery-add'),
    path('gallery/<uuid:gallery_id>/delete/', views.product_gallery_delete, name='product-gallery-delete'),
    path('gallery/<uuid:gallery_id>/set-primary/', views.product_gallery_set_primary, name='product-gallery-set-primary'),
    
    # Product Variants
    path('<uuid:product_id>/variants/', views.product_variant_list, name='product-variant-list'),
    path('<uuid:product_id>/variants/create/', views.product_variant_create, name='product-variant-create'),
    path('variants/<uuid:variant_id>/', views.product_variant_detail, name='product-variant-detail'),
    path('variants/<uuid:variant_id>/edit/', views.product_variant_update, name='product-variant-edit'),
    path('variants/<uuid:variant_id>/delete/', views.product_variant_delete, name='product-variant-delete'),
    
    # Product Reviews
    path('<uuid:product_id>/reviews/', views.product_review_list, name='product-review-list'),
    path('<uuid:product_id>/reviews/create/', views.product_review_create, name='product-review-create'),
    path('reviews/<uuid:review_id>/', views.product_review_detail, name='product-review-detail'),
    path('reviews/<uuid:review_id>/edit/', views.product_review_update, name='product-review-edit'),
    path('reviews/<uuid:review_id>/delete/', views.product_review_delete, name='product-review-delete'),
    path('reviews/<uuid:review_id>/helpful/', views.product_review_helpful, name='product-review-helpful'),
    
    # Product Tags
    path('tags/', views.product_tag_list, name='product-tag-list'),
    path('tags/<uuid:tag_id>/', views.product_tag_detail, name='product-tag-detail'),
    path('tags/<uuid:tag_id>/products/', views.product_tag_products, name='product-tag-products'),
    
    # Favorites/Wishlist
    path('favorites/', views.product_favorite_list, name='product-favorite-list'),
    path('<uuid:product_id>/favorite/', views.product_favorite_toggle, name='product-favorite-toggle'),
    path('favorites/<uuid:favorite_id>/delete/', views.product_favorite_delete, name='product-favorite-delete'),
    
    # Product Views & Analytics
    path('<uuid:product_id>/views/', views.product_view_list, name='product-view-list'),
    path('<uuid:product_id>/track-view/', views.product_view_track, name='product-view-track'),
    
    # Filter & Search
    path('search/', views.product_search, name='product-search'),
    path('filter/', views.product_filter, name='product-filter'),
    path('bestsellers/', views.product_bestsellers, name='product-bestsellers'),
    path('featured/', views.product_featured, name='product-featured'),
    path('new-arrivals/', views.product_new_arrivals, name='product-new-arrivals'),
    path('on-sale/', views.product_on_sale, name='product-on-sale'),
    
    # Seller-specific
    path('my-products/', views.product_my_list, name='product-my-list'),
    path('my-products/analytics/', views.product_seller_analytics, name='product-seller-analytics'),
]



