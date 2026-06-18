import django, os
os.environ['DJANGO_SETTINGS_MODULE']='ares_project.settings'
django.setup()

from products.models import Robot, Category
from django.db.models import Q

military_category = Category.objects.filter(slug='military-grade', parent__isnull=True).first()
print(f'Military Category: {military_category}')

if military_category:
    subcategory_ids = list(military_category.subcategories.filter(is_active=True).values_list('id', flat=True))
    all_military_ids = [military_category.id] + subcategory_ids
    print(f'Total category IDs: {len(all_military_ids)}')
    
    robots = Robot.objects.filter(
        Q(product__category_id__in=all_military_ids) |
        Q(robot_type='military_autonomous')
    ).select_related('product', 'product__category')
    
    print(f'Military robots count: {robots.count()}')
    print('')
    print('=== MILITARY ROBOTS ===')
    for r in robots[:15]:
        cat_name = r.product.category.name if r.product.category else 'None'
        print(f'  {r.product.title} -> {cat_name}')
else:
    print('Military category not found!')
