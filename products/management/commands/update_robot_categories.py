"""
Management command to update all robots with correct categories based on their type and restrictions.
"""
from django.core.management.base import BaseCommand
from products.models import Robot, Category, Product


class Command(BaseCommand):
    help = 'Update all robots with correct categories based on type and restrictions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Updating robot categories...'))
        
        # Get categories
        try:
            # Military Grade categories
            military_grade = Category.objects.get(slug='military-grade')
            military_drones = Category.objects.get(slug='military-drones')
            war_machines = Category.objects.get(slug='war-machines')
            naval_systems = Category.objects.get(slug='naval-systems')
            defense_systems = Category.objects.get(slug='defense-systems')
            
            # Humanoid categories
            humanoids = Category.objects.get(slug='humanoids')
            humanoid_companions_18 = Category.objects.get(slug='humanoid-companions-18')
            humanoid_home_service = Category.objects.get(slug='humanoid-home-service')
            humanoid_assistance = Category.objects.get(slug='humanoid-assistance')
            
            # Vehicle categories
            vehicles = Category.objects.get(slug='vehicles')
            ground_vehicles = Category.objects.get(slug='ground-vehicles')
            aerial_vehicles = Category.objects.get(slug='aerial-vehicles')
            marine_vehicles = Category.objects.get(slug='marine-vehicles')
            
            # Industrial
            industrial = Category.objects.get(slug='industrial')
            
            # Super Intelligent
            super_intelligent = Category.objects.get(slug='super-intelligent')
            
            # Consumer
            consumer = Category.objects.get(slug='consumer')
            consumer_drones = Category.objects.get(slug='consumer-drones')
            
        except Category.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Category not found: {e}'))
            self.stdout.write(self.style.WARNING('Please run setup_categories first!'))
            return
        
        updated_count = 0
        
        # Process all robots
        robots = Robot.objects.select_related('product', 'usage_restriction').all()
        
        for robot in robots:
            try:
                product = robot.product
                old_category = product.category
                
                # Determine category based on robot type and restrictions
                new_category = None
                title_lower = (product.title or '').lower()
                desc_lower = (product.description or '').lower()
                combined_text = f'{title_lower} {desc_lower}'
                
                # PRIORITY 1: Check if it's age-restricted (18+) companion FIRST
                # This must come BEFORE military check to prevent misclassification
                try:
                    if hasattr(robot, 'usage_restriction') and robot.usage_restriction:
                        if robot.usage_restriction.restriction_level == 'age_restricted':
                            # Age-restricted robots should NEVER be in military categories
                            if 'companion' in combined_text or 'humanoid' in combined_text or 'partner' in combined_text:
                                new_category = humanoid_companions_18
                except:
                    pass
                
                # PRIORITY 2: Check if it's military-grade (ONLY if not age-restricted)
                if not new_category:
                    try:
                        # Explicitly exclude age_restricted from military classification
                        is_age_restricted = (
                            hasattr(robot, 'usage_restriction') and robot.usage_restriction and 
                            robot.usage_restriction.restriction_level == 'age_restricted'
                        )
                        
                        if not is_age_restricted:
                            is_military = (
                                robot.is_restricted and 
                                (robot.robot_type == 'military_autonomous' or
                                 (hasattr(robot, 'usage_restriction') and robot.usage_restriction and 
                                  robot.usage_restriction.restriction_level == 'military_only'))
                            )
                        
                        if is_military:
                            # Determine military subcategory based on title/description
                            if 'drone' in combined_text or 'quadcopter' in combined_text or 'uav' in combined_text or 'reconnaissance' in combined_text or 'skyhawk' in combined_text:
                                new_category = military_drones
                            elif 'war' in combined_text or 'combat' in combined_text or 'ground vehicle' in combined_text or 'cagv' in combined_text or 'humanoid combat' in combined_text or 'sword' in combined_text:
                                new_category = war_machines
                            elif 'naval' in combined_text or 'submersible' in combined_text or 'underwater' in combined_text or 'marine' in combined_text or 'spectre' in combined_text:
                                new_category = naval_systems
                            elif 'defense' in combined_text or 'perimeter' in combined_text or 'sentry' in combined_text or 'warden' in combined_text or 'guardian' in combined_text:
                                new_category = defense_systems
                            else:
                                new_category = military_grade  # Default to parent
                    except:
                        pass
                
                # Check if it's a humanoid (non-military, non-age-restricted)
                if not new_category:
                    try:
                        if (robot.robot_type in ['service_robot'] and 
                            'humanoid' in combined_text and
                            not robot.is_restricted):
                            # Check if it's for home service
                            if 'home' in combined_text or 'service' in combined_text:
                                new_category = humanoid_home_service
                            elif 'assistance' in combined_text or 'healthcare' in combined_text:
                                new_category = humanoid_assistance
                            else:
                                new_category = humanoids  # Default to parent
                    except:
                        pass
                
                # Check if it's a vehicle
                if not new_category:
                    try:
                        if robot.robot_type in ['commercial_drone', 'consumer_drone']:
                            if robot.is_restricted:
                                new_category = military_drones
                            else:
                                new_category = consumer_drones
                        elif 'vehicle' in combined_text or 'rover' in combined_text:
                            if 'ground' in combined_text or 'cagv' in combined_text:
                                new_category = ground_vehicles
                            elif 'marine' in combined_text or 'naval' in combined_text:
                                new_category = marine_vehicles
                            else:
                                new_category = vehicles
                    except:
                        pass
                
                # Check if it's industrial
                if not new_category:
                    try:
                        if robot.robot_type == 'industrial_robot':
                            new_category = industrial
                    except:
                        pass
                
                # Check if it requires research clearance (priority 50)
                if not new_category:
                    try:
                        if (hasattr(robot, 'usage_restriction') and robot.usage_restriction and 
                            robot.usage_restriction.restriction_level == 'clearance_required' and
                            robot.usage_restriction.requires_verification):
                            # This is a heuristic - if it's highly advanced, mark as super intelligent
                            if 'research' in combined_text or 'experimental' in combined_text:
                                new_category = super_intelligent
                            else:
                                new_category = industrial  # Default
                    except:
                        pass
                
                # Default fallback
                if not new_category:
                    # Try to infer from existing category
                    if product.category:
                        # Keep existing if it's a valid category
                        if product.category.is_active:
                            new_category = product.category
                        else:
                            new_category = consumer  # Default fallback
                    else:
                        new_category = consumer  # Default fallback
                
                # Update product category
                if product.category != new_category:
                    product.category = new_category
                    product.save(update_fields=['category'])
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated: {product.title[:50]} -> {new_category.name}'
                        )
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error updating {robot.product.title if hasattr(robot, "product") and robot.product else "Unknown"}: {str(e)}')
                )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'Updated {updated_count} robots with correct categories')
        )
