"""
Management command to clean up and reorganize categories properly.
This removes duplicates and creates a clean hierarchical structure.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Category, Robot, Product


class Command(BaseCommand):
    help = 'Clean up and reorganize categories with proper hierarchy'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=== CLEANING UP CATEGORIES ==='))
        
        # First, let's identify the robots and their current categories
        robots = Robot.objects.select_related('product', 'product__category').all()
        robot_data = []
        for r in robots:
            if r.product.category:
                robot_data.append({
                    'robot': r,
                    'title': r.product.title,
                    'current_category': r.product.category.name,
                    'robot_type': r.robot_type,
                    'is_restricted': r.is_restricted,
                })
        
        self.stdout.write(f"Found {len(robot_data)} robots with categories")
        
        # Delete all existing categories
        self.stdout.write(self.style.WARNING('Deleting all existing categories...'))
        Category.objects.all().delete()
        
        # Create clean main categories
        self.stdout.write(self.style.SUCCESS('Creating clean category structure...'))
        
        main_categories = {}
        
        # 1. Military Grade (restricted)
        main_categories['military'] = Category.objects.create(
            name='Military Grade',
            slug='military-grade',
            description='Military-grade autonomous systems and war machines requiring clearance',
            icon='fas fa-shield-alt',
            order=1,
            is_active=True,
            is_featured=True,
        )
        
        # 2. Companion & Humanoid (18+)
        main_categories['companion'] = Category.objects.create(
            name='Companion Humanoids (18+)',
            slug='companion-humanoids-18-plus',
            description='Adult-only companion humanoid robots requiring age verification',
            icon='fas fa-user-friends',
            order=2,
            is_active=True,
            is_featured=True,
        )
        
        # 3. Autonomous Vehicles
        main_categories['vehicles'] = Category.objects.create(
            name='Autonomous Vehicles',
            slug='autonomous-vehicles',
            description='Ground, aerial, and marine autonomous vehicles',
            icon='fas fa-car',
            order=3,
            is_active=True,
            is_featured=True,
        )
        
        # 4. Industrial Robots
        main_categories['industrial'] = Category.objects.create(
            name='Industrial Robots',
            slug='industrial-robots',
            description='Manufacturing, logistics, and industrial automation systems',
            icon='fas fa-industry',
            order=4,
            is_active=True,
            is_featured=True,
        )
        
        # 5. Consumer Robots
        main_categories['consumer'] = Category.objects.create(
            name='Consumer Robots',
            slug='consumer-robots',
            description='Consumer-grade robots for personal and home use',
            icon='fas fa-home',
            order=5,
            is_active=True,
            is_featured=True,
        )
        
        # 6. Service & Healthcare
        main_categories['service'] = Category.objects.create(
            name='Service & Healthcare',
            slug='service-healthcare',
            description='Service robots and healthcare assistance systems',
            icon='fas fa-hand-holding-medical',
            order=6,
            is_active=True,
            is_featured=True,
        )
        
        # 7. Research & Experimental
        main_categories['research'] = Category.objects.create(
            name='Research & Experimental',
            slug='research-experimental',
            description='Advanced AI research platforms and experimental systems',
            icon='fas fa-flask',
            order=7,
            is_active=True,
            is_featured=True,
        )
        
        self.stdout.write(self.style.SUCCESS(f"Created {len(main_categories)} main categories"))
        
        # Create subcategories
        subcategories = {}
        
        # Military subcategories
        subcategories['war_machines'] = Category.objects.create(
            name='War Machines',
            slug='war-machines',
            description='Autonomous ground combat vehicles and heavy weapons platforms',
            parent=main_categories['military'],
            order=1,
            is_active=True,
        )
        
        subcategories['military_drones'] = Category.objects.create(
            name='Military Drones',
            slug='military-drones',
            description='Armed aerial drones and reconnaissance systems',
            parent=main_categories['military'],
            order=2,
            is_active=True,
        )
        
        subcategories['naval_systems'] = Category.objects.create(
            name='Naval Systems',
            slug='naval-systems',
            description='Autonomous submarines and naval warfare systems',
            parent=main_categories['military'],
            order=3,
            is_active=True,
        )
        
        subcategories['defense_systems'] = Category.objects.create(
            name='Defense Systems',
            slug='defense-systems',
            description='Perimeter defense and security autonomous systems',
            parent=main_categories['military'],
            order=4,
            is_active=True,
        )
        
        # Vehicle subcategories
        subcategories['ground_vehicles'] = Category.objects.create(
            name='Ground Vehicles',
            slug='ground-vehicles',
            description='Autonomous cars, trucks, and ground transport',
            parent=main_categories['vehicles'],
            order=1,
            is_active=True,
        )
        
        subcategories['aerial_vehicles'] = Category.objects.create(
            name='Aerial Vehicles',
            slug='aerial-vehicles',
            description='Commercial drones and aerial platforms',
            parent=main_categories['vehicles'],
            order=2,
            is_active=True,
        )
        
        subcategories['marine_vehicles'] = Category.objects.create(
            name='Marine Vehicles',
            slug='marine-vehicles',
            description='Autonomous boats and underwater vehicles',
            parent=main_categories['vehicles'],
            order=3,
            is_active=True,
        )
        
        # Industrial subcategories
        subcategories['manufacturing'] = Category.objects.create(
            name='Manufacturing',
            slug='manufacturing',
            description='Factory and assembly line robots',
            parent=main_categories['industrial'],
            order=1,
            is_active=True,
        )
        
        subcategories['logistics'] = Category.objects.create(
            name='Logistics & Warehousing',
            slug='logistics-warehousing',
            description='Warehouse automation and logistics robots',
            parent=main_categories['industrial'],
            order=2,
            is_active=True,
        )
        
        # Consumer subcategories
        subcategories['home_robots'] = Category.objects.create(
            name='Home Robots',
            slug='home-robots',
            description='Home assistance and entertainment robots',
            parent=main_categories['consumer'],
            order=1,
            is_active=True,
        )
        
        subcategories['consumer_drones'] = Category.objects.create(
            name='Consumer Drones',
            slug='consumer-drones',
            description='Consumer-grade drones for photography and recreation',
            parent=main_categories['consumer'],
            order=2,
            is_active=True,
        )
        
        # Service subcategories
        subcategories['healthcare'] = Category.objects.create(
            name='Healthcare Robots',
            slug='healthcare-robots',
            description='Medical assistance and healthcare automation',
            parent=main_categories['service'],
            order=1,
            is_active=True,
        )
        
        subcategories['elderly_care'] = Category.objects.create(
            name='Elderly Care',
            slug='elderly-care',
            description='Robots for elderly assistance and care',
            parent=main_categories['service'],
            order=2,
            is_active=True,
        )
        
        # Research subcategories
        subcategories['ai_research'] = Category.objects.create(
            name='AI Research Platforms',
            slug='ai-research-platforms',
            description='Advanced AI and machine learning research robots',
            parent=main_categories['research'],
            order=1,
            is_active=True,
        )
        
        subcategories['experimental'] = Category.objects.create(
            name='Experimental Systems',
            slug='experimental-systems',
            description='Cutting-edge experimental robotics',
            parent=main_categories['research'],
            order=2,
            is_active=True,
        )
        
        self.stdout.write(self.style.SUCCESS(f"Created {len(subcategories)} subcategories"))
        
        # Now reassign robots to correct categories based on their names and types
        self.stdout.write(self.style.WARNING('Reassigning robots to correct categories...'))
        
        for robot in robots:
            title = robot.product.title.lower()
            robot_type = robot.robot_type
            is_restricted = robot.is_restricted
            
            new_category = None
            
            # Companion/Adult robots - check first
            if any(word in title for word in ['companion', 'aurora', 'luna', 'eva', 'neo-humanoid', 'partner']):
                new_category = main_categories['companion']
            
            # Military robots
            elif any(word in title for word in ['warden', 'raven', 'spectre', 'vanguard', 'titan', 'ares', 'combat', 'attack', 'military', 'war']):
                if 'drone' in title or 'quadcopter' in title:
                    new_category = subcategories['military_drones']
                elif 'naval' in title or 'submarine' in title or 'submersible' in title:
                    new_category = subcategories['naval_systems']
                elif 'defense' in title or 'perimeter' in title:
                    new_category = subcategories['defense_systems']
                else:
                    new_category = subcategories['war_machines']
            
            # Check robot_type as fallback
            elif robot_type == 'military_autonomous':
                new_category = main_categories['military']
            elif robot_type == 'companion_humanoid':
                new_category = main_categories['companion']
            elif robot_type == 'industrial':
                new_category = main_categories['industrial']
            elif robot_type == 'consumer_drone':
                new_category = subcategories['consumer_drones']
            elif robot_type == 'service':
                new_category = main_categories['service']
            
            # Default based on keywords
            elif 'industrial' in title:
                new_category = main_categories['industrial']
            elif 'drone' in title:
                if is_restricted:
                    new_category = subcategories['military_drones']
                else:
                    new_category = subcategories['consumer_drones']
            elif 'vehicle' in title:
                new_category = main_categories['vehicles']
            else:
                # Default to consumer
                new_category = main_categories['consumer']
            
            if new_category:
                robot.product.category = new_category
                robot.product.save()
                self.stdout.write(f"  {robot.product.title} -> {new_category.name}")
        
        self.stdout.write(self.style.SUCCESS('=== CATEGORY CLEANUP COMPLETE ==='))
        
        # Print final summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== FINAL CATEGORY SUMMARY ==='))
        for cat in Category.objects.filter(parent__isnull=True).order_by('order'):
            count = Product.objects.filter(category=cat).count()
            sub_count = Product.objects.filter(category__parent=cat).count()
            total = count + sub_count
            self.stdout.write(f"  {cat.name}: {total} products")
            for subcat in cat.subcategories.all():
                sub_product_count = Product.objects.filter(category=subcat).count()
                self.stdout.write(f"    └─ {subcat.name}: {sub_product_count} products")
