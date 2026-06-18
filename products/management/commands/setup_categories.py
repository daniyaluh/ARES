"""
Management command to set up comprehensive hierarchical category structure.
"""
from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Set up comprehensive hierarchical category structure for robots'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up category structure...'))
        
        # Clear existing categories (optional - comment out if you want to keep existing)
        # Category.objects.all().delete()
        
        # ============================================
        # MAIN CATEGORIES (Parent categories)
        # ============================================
        
        # 1. Military Grade
        military_grade, _ = Category.objects.get_or_create(
            slug='military-grade',
            defaults={
                'name': 'Military Grade',
                'description': 'Military-grade autonomous systems and war machines requiring clearance',
                'order': 1,
                'is_active': True,
                'is_featured': True,
            }
        )
        self.stdout.write(f'Created/Updated: {military_grade.name}')
        
        # 2. Humanoids
        humanoids, _ = Category.objects.get_or_create(
            slug='humanoids',
            defaults={
                'name': 'Humanoid Robots',
                'description': 'Advanced humanoid robots for various applications',
                'order': 2,
                'is_active': True,
                'is_featured': True,
            }
        )
        self.stdout.write(f'Created/Updated: {humanoids.name}')
        
        # 3. Vehicles
        vehicles, _ = Category.objects.get_or_create(
            slug='vehicles',
            defaults={
                'name': 'Autonomous Vehicles',
                'description': 'Autonomous ground, air, and water vehicles',
                'order': 3,
                'is_active': True,
                'is_featured': True,
            }
        )
        self.stdout.write(f'Created/Updated: {vehicles.name}')
        
        # 4. Industrial
        industrial, _ = Category.objects.get_or_create(
            slug='industrial',
            defaults={
                'name': 'Industrial Robots',
                'description': 'Industrial automation and manufacturing robots',
                'order': 4,
                'is_active': True,
                'is_featured': False,
            }
        )
        self.stdout.write(f'Created/Updated: {industrial.name}')
        
        # 5. Super Intelligent (Priority 50)
        super_intelligent, _ = Category.objects.get_or_create(
            slug='super-intelligent',
            defaults={
                'name': 'Super Intelligent Systems',
                'description': 'Cutting-edge research robotics and experimental prototypes requiring highest clearance',
                'order': 5,
                'is_active': True,
                'is_featured': True,
            }
        )
        self.stdout.write(f'Created/Updated: {super_intelligent.name}')
        
        # 6. Consumer
        consumer, _ = Category.objects.get_or_create(
            slug='consumer',
            defaults={
                'name': 'Consumer Robots',
                'description': 'Consumer-grade robots for personal use',
                'order': 6,
                'is_active': True,
                'is_featured': False,
            }
        )
        self.stdout.write(f'Created/Updated: {consumer.name}')
        
        # 7. Service & Assistance
        service, _ = Category.objects.get_or_create(
            slug='service-assistance',
            defaults={
                'name': 'Service & Assistance',
                'description': 'Service robots for home, healthcare, and assistance',
                'order': 7,
                'is_active': True,
                'is_featured': False,
            }
        )
        self.stdout.write(f'Created/Updated: {service.name}')
        
        # ============================================
        # MILITARY GRADE SUBCATEGORIES
        # ============================================
        
        military_drones, _ = Category.objects.get_or_create(
            slug='military-drones',
            defaults={
                'name': 'Military Drones',
                'description': 'Combat and reconnaissance drones',
                'parent': military_grade,
                'order': 1,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {military_drones.name}')
        
        war_machines, _ = Category.objects.get_or_create(
            slug='war-machines',
            defaults={
                'name': 'War Machines',
                'description': 'Autonomous combat vehicles and ground systems',
                'parent': military_grade,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {war_machines.name}')
        
        naval_systems, _ = Category.objects.get_or_create(
            slug='naval-systems',
            defaults={
                'name': 'Naval Systems',
                'description': 'Underwater autonomous vehicles and naval systems',
                'parent': military_grade,
                'order': 3,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {naval_systems.name}')
        
        defense_systems, _ = Category.objects.get_or_create(
            slug='defense-systems',
            defaults={
                'name': 'Defense Systems',
                'description': 'Perimeter defense and security systems',
                'parent': military_grade,
                'order': 4,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {defense_systems.name}')
        
        # ============================================
        # HUMANOID SUBCATEGORIES
        # ============================================
        
        humanoid_companions_18, _ = Category.objects.get_or_create(
            slug='humanoid-companions-18',
            defaults={
                'name': 'Companion Humanoids (18+)',
                'description': 'Adult companion humanoid robots - Age restricted',
                'parent': humanoids,
                'order': 1,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {humanoid_companions_18.name}')
        
        humanoid_home_service, _ = Category.objects.get_or_create(
            slug='humanoid-home-service',
            defaults={
                'name': 'Home Service Humanoids',
                'description': 'Humanoid robots for home assistance and service',
                'parent': humanoids,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {humanoid_home_service.name}')
        
        humanoid_assistance, _ = Category.objects.get_or_create(
            slug='humanoid-assistance',
            defaults={
                'name': 'Assistance Humanoids',
                'description': 'Humanoid robots for healthcare and assistance',
                'parent': humanoids,
                'order': 3,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {humanoid_assistance.name}')
        
        humanoid_research, _ = Category.objects.get_or_create(
            slug='humanoid-research',
            defaults={
                'name': 'Research Humanoids',
                'description': 'Advanced research and development humanoids',
                'parent': humanoids,
                'order': 4,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {humanoid_research.name}')
        
        # ============================================
        # VEHICLE SUBCATEGORIES
        # ============================================
        
        ground_vehicles, _ = Category.objects.get_or_create(
            slug='ground-vehicles',
            defaults={
                'name': 'Ground Vehicles',
                'description': 'Autonomous ground vehicles and rovers',
                'parent': vehicles,
                'order': 1,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {ground_vehicles.name}')
        
        aerial_vehicles, _ = Category.objects.get_or_create(
            slug='aerial-vehicles',
            defaults={
                'name': 'Aerial Vehicles',
                'description': 'Drones and aerial autonomous systems',
                'parent': vehicles,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {aerial_vehicles.name}')
        
        marine_vehicles, _ = Category.objects.get_or_create(
            slug='marine-vehicles',
            defaults={
                'name': 'Marine Vehicles',
                'description': 'Underwater and surface marine vehicles',
                'parent': vehicles,
                'order': 3,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {marine_vehicles.name}')
        
        # ============================================
        # INDUSTRIAL SUBCATEGORIES
        # ============================================
        
        manufacturing, _ = Category.objects.get_or_create(
            slug='manufacturing',
            defaults={
                'name': 'Manufacturing',
                'description': 'Manufacturing and assembly robots',
                'parent': industrial,
                'order': 1,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {manufacturing.name}')
        
        logistics, _ = Category.objects.get_or_create(
            slug='logistics',
            defaults={
                'name': 'Logistics & Warehousing',
                'description': 'Warehouse and logistics automation',
                'parent': industrial,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {logistics.name}')
        
        inspection, _ = Category.objects.get_or_create(
            slug='inspection',
            defaults={
                'name': 'Inspection & Maintenance',
                'description': 'Inspection and maintenance robots',
                'parent': industrial,
                'order': 3,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {inspection.name}')
        
        # ============================================
        # SUPER INTELLIGENT SUBCATEGORIES
        # ============================================
        
        experimental, _ = Category.objects.get_or_create(
            slug='experimental',
            defaults={
                'name': 'Experimental Systems',
                'description': 'Experimental and prototype systems',
                'parent': super_intelligent,
                'order': 1,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {experimental.name}')
        
        ai_research, _ = Category.objects.get_or_create(
            slug='ai-research',
            defaults={
                'name': 'AI Research Platforms',
                'description': 'Advanced AI research and development platforms',
                'parent': super_intelligent,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {ai_research.name}')
        
        quantum_systems, _ = Category.objects.get_or_create(
            slug='quantum-systems',
            defaults={
                'name': 'Quantum Systems',
                'description': 'Quantum computing and quantum-enabled robots',
                'parent': super_intelligent,
                'order': 3,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {quantum_systems.name}')
        
        # ============================================
        # CONSUMER SUBCATEGORIES
        # ============================================
        
        consumer_drones, _ = Category.objects.get_or_create(
            slug='consumer-drones',
            defaults={
                'name': 'Consumer Drones',
                'description': 'Consumer-grade drones for personal use',
                'parent': consumer,
                'order': 1,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {consumer_drones.name}')
        
        home_robots, _ = Category.objects.get_or_create(
            slug='home-robots',
            defaults={
                'name': 'Home Robots',
                'description': 'Robots for home automation and assistance',
                'parent': consumer,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {home_robots.name}')
        
        # ============================================
        # SERVICE & ASSISTANCE SUBCATEGORIES
        # ============================================
        
        healthcare, _ = Category.objects.get_or_create(
            slug='healthcare',
            defaults={
                'name': 'Healthcare Robots',
                'description': 'Medical and healthcare assistance robots',
                'parent': service,
                'order': 1,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {healthcare.name}')
        
        elderly_care, _ = Category.objects.get_or_create(
            slug='elderly-care',
            defaults={
                'name': 'Elderly Care',
                'description': 'Robots for elderly care and assistance',
                'parent': service,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write(f'  - Created/Updated: {elderly_care.name}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Category structure setup complete!'))
        self.stdout.write('')
        self.stdout.write('Main Categories:')
        main_cats = Category.objects.filter(parent__isnull=True, is_active=True).order_by('order')
        for cat in main_cats:
            sub_count = cat.subcategories.filter(is_active=True).count()
            self.stdout.write(f'  {cat.name} ({sub_count} subcategories)')

