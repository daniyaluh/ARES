"""
Management command to fix any robots that are incorrectly categorized.
Specifically fixes age-restricted robots in military categories.
"""
from django.core.management.base import BaseCommand
from products.models import Robot, Category


class Command(BaseCommand):
    help = 'Fix robots that are incorrectly categorized (age-restricted in military categories)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Fixing category errors...'))
        
        # Get categories
        try:
            humanoid_companions_18 = Category.objects.get(slug='humanoid-companions-18')
            military_cats = Category.objects.filter(slug__in=['military-grade', 'military-drones', 'war-machines', 'naval-systems', 'defense-systems'])
        except Category.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Category not found: {e}'))
            return
        
        # Find age-restricted robots in military categories
        fixed_count = 0
        robots_in_military = Robot.objects.filter(product__category__in=military_cats).select_related('product', 'usage_restriction')
        
        for robot in robots_in_military:
            try:
                # Check if it's age-restricted
                if (hasattr(robot, 'usage_restriction') and robot.usage_restriction and 
                    robot.usage_restriction.restriction_level == 'age_restricted'):
                    # Move to correct category
                    robot.product.category = humanoid_companions_18
                    robot.product.save(update_fields=['category'])
                    fixed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Fixed: {robot.product.title[:50]} -> {humanoid_companions_18.name}'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error fixing {robot.product.title}: {str(e)}')
                )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'Fixed {fixed_count} robots with incorrect categories')
        )







