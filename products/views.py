"""
Views for Products app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db.models import Q
from .models import (
    Product, Robot, Category, ProductGallery, ProductVariant,
    ProductTag, ProductReview, ProductFavorite, ProductView
)


# Product Views
def product_list(request):
    """List all products."""
    # Base query: only active and visible products for regular users
    products = Product.objects.filter(status='active', visibility=True)
    
    # For staff, show option to see all products
    show_all = request.GET.get('show_all') == '1' and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    if show_all:
        products = Product.objects.all()
    
    # Add ordering
    products = products.order_by('-created_at')
    
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)
    
    context = {
        'products': products_page,
        'show_all': show_all,
        'is_staff': request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser),
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, product_id):
    """Product detail view."""
    product = get_object_or_404(Product, id=product_id)
    
    # Check product status - handle non-active products
    is_owner = request.user.is_authenticated and product.seller == request.user
    is_staff = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    
    # Status messages for owners/staff viewing non-active products
    status_warning = None
    can_view = True
    
    if product.status != 'active':
        if is_owner or is_staff:
            # Owners and staff can view, but show warning
            status_messages = {
                'draft': '📝 This product is in DRAFT mode and not visible to buyers.',
                'pending': '⏳ This product is PENDING REVIEW by staff.',
                'paused': '⏸️ This product is PAUSED and not visible to buyers.',
                'out_of_stock': '❌ This product is marked as OUT OF STOCK.',
                'discontinued': '📦 This product has been DISCONTINUED.',
                'banned': '🚫 This product has been BANNED by staff.',
                'rejected': '❌ This product was REJECTED during review.',
            }
            status_warning = status_messages.get(product.status, f'Status: {product.status}')
        else:
            # Regular users cannot view non-active products
            messages.error(request, "This product is currently unavailable.")
            return redirect('products:product-list')
    
    # Track view
    if request.user.is_authenticated:
        ProductView.objects.create(product=product, user=request.user)
    else:
        ProductView.objects.create(product=product)
    
    context = {
        'product': product,
        'status_warning': status_warning,
        'is_owner': is_owner,
        'is_staff': is_staff,
    }
    
    return render(request, 'products/product_detail.html', context)


@login_required
def product_create(request):
    """Create new product."""
    if request.method == 'POST':
        # Check if seller wants to save as draft or submit for review
        submit_for_review = request.POST.get('submit_for_review') == '1'
        
        product = Product.objects.create(
            seller=request.user,
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
            price=request.POST.get('price', 0),
            status='pending' if submit_for_review else 'draft'
        )
        
        if submit_for_review:
            messages.success(request, "Product submitted for review! Staff will review it shortly.")
        else:
            messages.success(request, "Product saved as draft. You can submit it for review later.")
        return redirect('products:product-detail', product_id=product.id)
    
    categories = Category.objects.filter(is_active=True)
    return render(request, 'products/product_create.html', {'categories': categories})


@login_required
def product_update(request, product_id):
    """Update product."""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        product.title = request.POST.get('title', product.title)
        product.description = request.POST.get('description', product.description)
        
        # Check if submitting for review
        submit_for_review = request.POST.get('submit_for_review') == '1'
        if submit_for_review and product.status == 'draft':
            product.status = 'pending'
            messages.success(request, "Product submitted for review! Staff will review it shortly.")
        else:
            messages.success(request, "Product updated successfully.")
        
        product.save()
        return redirect('products:product-detail', product_id=product.id)
    
    return render(request, 'products/product_edit.html', {'product': product})


@login_required
def product_submit_for_review(request, product_id):
    """Submit a draft product for staff review."""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if product.status != 'draft':
        messages.error(request, "Only draft products can be submitted for review.")
        return redirect('products:product-detail', product_id=product.id)
    
    if request.method == 'POST':
        product.status = 'pending'
        product.save()
        messages.success(request, "Product submitted for review! Staff will review it shortly.")
        return redirect('products:product-detail', product_id=product.id)
    
    return render(request, 'products/product_submit_review.html', {'product': product})


@login_required
def product_delete(request, product_id):
    """Delete product. Staff/Admin can delete any product, sellers can delete their own."""
    product = get_object_or_404(Product, id=product_id)
    
    # Check permissions: must be staff, admin, or the product owner
    is_owner = product.seller == request.user
    is_staff_or_admin = request.user.is_staff or request.user.is_superuser or getattr(request.user, 'access_level', 0) >= 60
    
    if not (is_owner or is_staff_or_admin):
        messages.error(request, "You don't have permission to delete this product.")
        return redirect('products:product-detail', product_id=product_id)
    
    if request.method == 'POST':
        product_title = product.title
        product.delete()
        messages.success(request, f"Product '{product_title}' deleted successfully.")
        
        # Redirect staff/admin to product list, owners to their products
        if is_staff_or_admin and not is_owner:
            return redirect('products:product-list')
        return redirect('products:product-list')
    
    return render(request, 'products/product_delete.html', {'product': product, 'is_staff_action': is_staff_or_admin and not is_owner})


# Robot Views
def robot_list(request):
    """List all robots."""
    robots = Robot.objects.select_related('product').filter(product__status='active')
    paginator = Paginator(robots, 20)
    page = request.GET.get('page')
    robots_page = paginator.get_page(page)
    return render(request, 'products/robot_list.html', {'robots': robots_page})


def robot_detail(request, robot_id):
    """Robot detail view."""
    robot = get_object_or_404(Robot.objects.select_related('product'), id=robot_id)
    
    # Check if robot is restricted and user can access it
    if robot.is_restricted or robot.requires_verification:
        if request.user.is_authenticated:
            # Staff/superuser bypass all checks
            if not (request.user.is_superuser or request.user.is_staff):
                try:
                    from verification.utils import can_access_robot
                    can_access, reason = can_access_robot(request.user, robot)
                    if not can_access:
                        messages.error(request, reason)
                        return redirect('products:robot-list')
                except ImportError:
                    pass
        else:
            messages.warning(request, "Please log in to view restricted products.")
            return redirect('users:login')
    
    return render(request, 'products/robot_detail.html', {'robot': robot})


@login_required
def robot_create(request):
    """Create new robot."""
    # Placeholder - implement full robot creation
    messages.info(request, "Robot creation coming soon.")
    return redirect('products:robot-list')


@login_required
def robot_update(request, robot_id):
    """Update robot."""
    robot = get_object_or_404(Robot, id=robot_id, product__seller=request.user)
    return render(request, 'products/robot_edit.html', {'robot': robot})


def robot_specifications(request, robot_id):
    """Robot specifications view."""
    robot = get_object_or_404(Robot, id=robot_id)
    specs = getattr(robot, 'specifications', None)
    return render(request, 'products/robot_specifications.html', {'robot': robot, 'specs': specs})


def robot_ai_details(request, robot_id):
    """Robot AI details view."""
    robot = get_object_or_404(Robot, id=robot_id)
    ai_details = getattr(robot, 'ai_system', None)
    return render(request, 'products/robot_ai_details.html', {'robot': robot, 'ai_details': ai_details})


def robot_power_system(request, robot_id):
    """Robot power system view."""
    robot = get_object_or_404(Robot, id=robot_id)
    power_system = getattr(robot, 'power_system', None)
    return render(request, 'products/robot_power_system.html', {'robot': robot, 'power_system': power_system})


def robot_restrictions(request, robot_id):
    """Robot restrictions view."""
    robot = get_object_or_404(Robot, id=robot_id)
    restrictions = getattr(robot, 'usage_restriction', None)
    return render(request, 'products/robot_restrictions.html', {'robot': robot, 'restrictions': restrictions})


# Category Views
def category_list(request):
    """List all categories."""
    categories = Category.objects.filter(is_active=True, parent__isnull=True)
    return render(request, 'products/category_list.html', {'categories': categories})


def category_browse(request):
    """Browse categories with subcategories displayed attractively."""
    main_categories = Category.objects.filter(
        parent__isnull=True, 
        is_active=True
    ).prefetch_related('subcategories').order_by('order')
    
    return render(request, 'products/category_browse.html', {
        'main_categories': main_categories
    })


def category_detail(request, category_id):
    """Category detail view."""
    category = get_object_or_404(Category, id=category_id)
    return render(request, 'products/category_detail.html', {'category': category})


def category_products(request, category_id):
    """Products in category."""
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category, status='active')
    return render(request, 'products/category_products.html', {'category': category, 'products': products})


@login_required
def category_create(request):
    """Create category (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('products:category-list')
    
    messages.info(request, "Category creation coming soon.")
    return redirect('products:category-list')


@login_required
def category_update(request, category_id):
    """Update category (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('products:category-list')
    
    category = get_object_or_404(Category, id=category_id)
    return render(request, 'products/category_edit.html', {'category': category})


# Product Gallery
@login_required
def product_gallery_list(request, product_id):
    """Product gallery list."""
    product = get_object_or_404(Product, id=product_id)
    gallery = ProductGallery.objects.filter(product=product)
    return render(request, 'products/product_gallery_list.html', {'product': product, 'gallery': gallery})


@login_required
def product_gallery_add(request, product_id):
    """Add to product gallery."""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST' and request.FILES.get('image'):
        ProductGallery.objects.create(product=product, image=request.FILES['image'])
        messages.success(request, "Image added successfully.")
        return redirect('products:product-gallery-list', product_id=product.id)
    
    return render(request, 'products/product_gallery_add.html', {'product': product})


@login_required
def product_gallery_delete(request, gallery_id):
    """Delete gallery item."""
    gallery_item = get_object_or_404(ProductGallery, id=gallery_id, product__seller=request.user)
    
    if request.method == 'POST':
        gallery_item.delete()
        messages.success(request, "Image deleted successfully.")
        return redirect('products:product-gallery-list', product_id=gallery_item.product.id)
    
    return render(request, 'products/product_gallery_delete.html', {'gallery_item': gallery_item})


@login_required
def product_gallery_set_primary(request, gallery_id):
    """Set primary image."""
    gallery_item = get_object_or_404(ProductGallery, id=gallery_id, product__seller=request.user)
    gallery_item.is_primary = True
    gallery_item.save()
    messages.success(request, "Primary image updated.")
    return redirect('products:product-gallery-list', product_id=gallery_item.product.id)


# Product Variants
@login_required
def product_variant_list(request, product_id):
    """List product variants."""
    product = get_object_or_404(Product, id=product_id)
    variants = ProductVariant.objects.filter(product=product)
    return render(request, 'products/product_variant_list.html', {'product': product, 'variants': variants})


@login_required
def product_variant_create(request, product_id):
    """Create product variant."""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        ProductVariant.objects.create(
            product=product,
            name=request.POST.get('name', ''),
            price=request.POST.get('price', 0)
        )
        messages.success(request, "Variant created successfully.")
        return redirect('products:product-variant-list', product_id=product.id)
    
    return render(request, 'products/product_variant_create.html', {'product': product})


def product_variant_detail(request, variant_id):
    """Product variant detail."""
    variant = get_object_or_404(ProductVariant, id=variant_id)
    return render(request, 'products/product_variant_detail.html', {'variant': variant})


@login_required
def product_variant_update(request, variant_id):
    """Update product variant."""
    variant = get_object_or_404(ProductVariant, id=variant_id, product__seller=request.user)
    
    if request.method == 'POST':
        variant.name = request.POST.get('name', variant.name)
        variant.save()
        messages.success(request, "Variant updated successfully.")
        return redirect('products:product-variant-list', product_id=variant.product.id)
    
    return render(request, 'products/product_variant_edit.html', {'variant': variant})


@login_required
def product_variant_delete(request, variant_id):
    """Delete product variant."""
    variant = get_object_or_404(ProductVariant, id=variant_id, product__seller=request.user)
    
    if request.method == 'POST':
        product_id = variant.product.id
        variant.delete()
        messages.success(request, "Variant deleted successfully.")
        return redirect('products:product-variant-list', product_id=product_id)
    
    return render(request, 'products/product_variant_delete.html', {'variant': variant})


# Product Reviews
def product_review_list(request, product_id):
    """List product reviews."""
    product = get_object_or_404(Product, id=product_id)
    reviews = ProductReview.objects.filter(product=product, is_approved=True)
    return render(request, 'products/product_review_list.html', {'product': product, 'reviews': reviews})


@login_required
def product_review_create(request, product_id):
    """Create product review."""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        ProductReview.objects.create(
            product=product,
            user=request.user,
            rating=int(request.POST.get('rating', 5)),
            comment=request.POST.get('comment', '')
        )
        messages.success(request, "Review submitted successfully.")
        return redirect('products:product-detail', product_id=product.id)
    
    return render(request, 'products/product_review_create.html', {'product': product})


def product_review_detail(request, review_id):
    """Product review detail."""
    review = get_object_or_404(ProductReview, id=review_id)
    return render(request, 'products/product_review_detail.html', {'review': review})


@login_required
def product_review_update(request, review_id):
    """Update product review."""
    review = get_object_or_404(ProductReview, id=review_id, user=request.user)
    
    if request.method == 'POST':
        review.comment = request.POST.get('comment', review.comment)
        review.save()
        messages.success(request, "Review updated successfully.")
        return redirect('products:product-detail', product_id=review.product.id)
    
    return render(request, 'products/product_review_edit.html', {'review': review})


@login_required
def product_review_delete(request, review_id):
    """Delete product review."""
    review = get_object_or_404(ProductReview, id=review_id, user=request.user)
    
    if request.method == 'POST':
        product_id = review.product.id
        review.delete()
        messages.success(request, "Review deleted successfully.")
        return redirect('products:product-detail', product_id=product_id)
    
    return render(request, 'products/product_review_delete.html', {'review': review})


@login_required
def product_review_helpful(request, review_id):
    """Mark review as helpful."""
    review = get_object_or_404(ProductReview, id=review_id)
    review.helpful_count += 1
    review.save()
    messages.success(request, "Thank you for your feedback.")
    return redirect('products:product-review-detail', review_id=review_id)


# Product Tags
def product_tag_list(request):
    """List all tags."""
    tags = ProductTag.objects.filter(is_active=True)
    return render(request, 'products/product_tag_list.html', {'tags': tags})


def product_tag_detail(request, tag_id):
    """Tag detail view."""
    tag = get_object_or_404(ProductTag, id=tag_id)
    return render(request, 'products/product_tag_detail.html', {'tag': tag})


def product_tag_products(request, tag_id):
    """Products with tag."""
    tag = get_object_or_404(ProductTag, id=tag_id)
    products = Product.objects.filter(tags=tag, status='active')
    return render(request, 'products/product_tag_products.html', {'tag': tag, 'products': products})


# Favorites
@login_required
def product_favorite_list(request):
    """List user's favorites."""
    favorites = ProductFavorite.objects.filter(user=request.user)
    return render(request, 'products/product_favorite_list.html', {'favorites': favorites})


@login_required
def product_favorite_toggle(request, product_id):
    """Toggle favorite status."""
    product = get_object_or_404(Product, id=product_id)
    favorite, created = ProductFavorite.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        favorite.delete()
        messages.success(request, "Removed from favorites.")
    else:
        messages.success(request, "Added to favorites.")
    
    return redirect('products:product-detail', product_id=product.id)


@login_required
def product_favorite_delete(request, favorite_id):
    """Delete favorite."""
    favorite = get_object_or_404(ProductFavorite, id=favorite_id, user=request.user)
    
    if request.method == 'POST':
        favorite.delete()
        messages.success(request, "Removed from favorites.")
        return redirect('products:product-favorite-list')
    
    return render(request, 'products/product_favorite_delete.html', {'favorite': favorite})


# Product Views Tracking
@login_required
def product_view_list(request, product_id):
    """List product views (seller only)."""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    views = ProductView.objects.filter(product=product)[:100]
    return render(request, 'products/product_view_list.html', {'product': product, 'views': views})


def product_view_track(request, product_id):
    """Track product view."""
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        ProductView.objects.create(product=product, user=request.user)
    else:
        ProductView.objects.create(product=product)
    
    return JsonResponse({'status': 'ok'})


# Search & Filter
def product_search(request):
    """Search products."""
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        status='active'
    )
    return render(request, 'products/product_search.html', {'products': products, 'query': query})


def product_filter(request):
    """Filter products."""
    category_id = request.GET.get('category')
    products = Product.objects.filter(status='active')
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    return render(request, 'products/product_filter.html', {'products': products})


def product_bestsellers(request):
    """Best selling products."""
    products = Product.objects.filter(is_bestseller=True, status='active')
    return render(request, 'products/product_bestsellers.html', {'products': products})


def product_featured(request):
    """Featured products."""
    products = Product.objects.filter(is_featured=True, status='active')
    return render(request, 'products/product_featured.html', {'products': products})


def product_new_arrivals(request):
    """New arrivals."""
    products = Product.objects.filter(status='active').order_by('-created_at')[:20]
    return render(request, 'products/product_new_arrivals.html', {'products': products})


def product_on_sale(request):
    """Products on sale."""
    products = Product.objects.filter(status='active', compare_at_price__isnull=False)
    return render(request, 'products/product_on_sale.html', {'products': products})


# Seller Views
@login_required
def product_my_list(request):
    """My products (seller)."""
    products = Product.objects.filter(seller=request.user)
    return render(request, 'products/product_my_list.html', {'products': products})


@login_required
def product_seller_analytics(request):
    """Seller analytics."""
    products = Product.objects.filter(seller=request.user)
    total_sales = sum(p.order_count for p in products)
    return render(request, 'products/product_seller_analytics.html', {
        'products': products,
        'total_sales': total_sales
    })
