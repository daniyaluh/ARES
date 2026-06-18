"""
Management command to populate database with professional robot products.
This will remove temporary products and create 15 professional robots.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import (
    Product, Robot, Category, RobotSpecification, AISystemDetails,
    PowerSystem, UsageRestriction
)
from verification.models import ClearanceLevel
from decimal import Decimal
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with professional robot products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Delete all existing products and robots before adding new ones',
        )

    def handle(self, *args, **options):
        if options['clear_existing']:
            self.stdout.write(self.style.WARNING('Clearing existing products and robots...'))
            Robot.objects.all().delete()
            Product.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        # Get or create admin user for seller
        admin_user, created = User.objects.get_or_create(
            email='admin@admin.com',
            defaults={
                'username': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if not admin_user.check_password('admin1234'):
            admin_user.set_password('admin1234')
            admin_user.save()

        # Get or create categories
        consumer_cat, _ = Category.objects.get_or_create(
            slug='consumer-drones',
            defaults={
                'name': 'Consumer Drones',
                'description': 'Personal and hobbyist drones for everyday use',
                'order': 1,
                'is_active': True,
                'is_featured': True,
            }
        )

        commercial_cat, _ = Category.objects.get_or_create(
            slug='commercial-drones',
            defaults={
                'name': 'Commercial Drones',
                'description': 'Professional drones for business and commercial applications',
                'order': 2,
                'is_active': True,
                'is_featured': True,
            }
        )

        military_cat, _ = Category.objects.get_or_create(
            slug='military-grade-robots',
            defaults={
                'name': 'Military-Grade Robots',
                'description': 'Advanced autonomous systems for defense and military applications',
                'order': 3,
                'is_active': True,
                'is_featured': True,
            }
        )

        humanoid_cat, _ = Category.objects.get_or_create(
            slug='humanoid-robots',
            defaults={
                'name': 'Humanoid Robots',
                'description': 'Advanced humanoid robots for service and research',
                'order': 4,
                'is_active': True,
                'is_featured': True,
            }
        )

        industrial_cat, _ = Category.objects.get_or_create(
            slug='industrial-robots',
            defaults={
                'name': 'Industrial Robots',
                'description': 'Robots designed for manufacturing and industrial automation',
                'order': 5,
                'is_active': True,
                'is_featured': False,
            }
        )

        # Get clearance levels
        public_clearance, _ = ClearanceLevel.objects.get_or_create(
            code='public',
            defaults={
                'name': 'Public Trust',
                'priority': 0,
                'is_active': True,
            }
        )

        military_clearance, _ = ClearanceLevel.objects.get_or_create(
            code='military',
            defaults={
                'name': 'Military Clearance',
                'priority': 40,
                'can_access_military': True,
                'can_access_export_controlled': True,
                'can_access_restricted': True,
                'is_active': True,
            }
        )

        # Define professional robots data
        robots_data = [
            # Consumer Drones
            {
                'product': {
                    'title': 'SkyFlyer Pro 4K',
                    'slug': 'skyflyer-pro-4k',
                    'short_description': 'Professional 4K camera drone with GPS navigation',
                    'description': '''The SkyFlyer Pro 4K is a cutting-edge consumer drone designed for aerial photography and videography enthusiasts. Featuring a stabilized 4K UHD camera with 3-axis gimbal, this drone captures stunning aerial footage with exceptional clarity. 

Equipped with advanced GPS navigation and obstacle avoidance sensors, the SkyFlyer Pro offers intelligent flight modes including follow-me, waypoint navigation, and orbit mode. With a flight time of up to 30 minutes and a range of 7 kilometers, this drone is perfect for capturing breathtaking landscapes, events, and creative cinematography.

Key features include real-time video transmission, intelligent return-to-home functionality, and a robust design that withstands various weather conditions. The companion mobile app provides intuitive controls and live HD streaming to your smartphone or tablet.''',
                    'price': Decimal('1299.99'),
                    'category': consumer_cat,
                    'status': 'active',
                    'stock_quantity': 25,
                    'weight': Decimal('1.2'),
                    'shipping_type': 'physical',
                },
                'robot': {
                    'robot_type': 'consumer_drone',
                    'manufacturer': 'SkyTech Industries',
                    'model_number': 'SF-PRO-4K-2024',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('1.2'),
                    'dimensions_length': Decimal('45.0'),
                    'dimensions_width': Decimal('35.0'),
                    'dimensions_height': Decimal('15.0'),
                    'max_speed_kmh': Decimal('60.0'),
                    'max_altitude_m': Decimal('500.0'),
                    'max_payload_kg': Decimal('0.5'),
                    'requires_verification': False,
                    'is_restricted': False,
                },
                'specs': {
                    'cpu': 'Qualcomm Snapdragon 865, 8-core',
                    'ram': '4GB LPDDR4X',
                    'storage': '64GB eUFS',
                    'gpu': 'Adreno 650',
                    'sensors': 'GPS, IMU, Barometer, Vision Sensor, Obstacle Avoidance',
                    'communication': 'WiFi 6, Bluetooth 5.0, 2.4/5.8GHz Dual Band',
                    'operating_system': 'Custom Flight Controller OS',
                },
                'ai': {
                    'ai_model': 'CNN-based Object Detection and Tracking',
                    'has_autonomous_navigation': True,
                    'has_object_detection': True,
                    'has_path_planning': True,
                    'has_swarm_capabilities': False,
                },
                'power': {
                    'battery_type': 'Lithium-Polymer',
                    'battery_capacity_mah': 6000,
                    'voltage_v': Decimal('11.1'),
                    'runtime_hours': Decimal('0.5'),
                    'charging_time_hours': Decimal('1.5'),
                    'power_consumption_w': Decimal('80.0'),
                },
            },
            {
                'product': {
                    'title': 'AX400 Personal Assistant Drone',
                    'slug': 'ax400-personal-assistant-drone',
                    'short_description': 'AI-powered personal assistant drone with voice commands',
                    'description': '''The AX400 represents the next generation of personal assistant drones, combining advanced AI capabilities with intuitive voice control. This compact, intelligent drone is designed to be your everyday companion, capable of performing a wide range of tasks from home security monitoring to personal photography.

Powered by advanced machine learning algorithms, the AX400 understands natural language commands and adapts to your preferences over time. Its sophisticated computer vision system enables it to recognize faces, follow subjects, and navigate complex indoor environments with precision.

The drone features a high-resolution camera with night vision capabilities, making it perfect for 24/7 home security. With privacy-first design, all data is processed locally, ensuring your information remains secure. The AX400 seamlessly integrates with smart home ecosystems and can respond to voice commands from across the room.

Equipped with extended battery life and rapid charging technology, this drone is always ready when you need it. Its sleek, modern design blends seamlessly into any home environment.''',
                    'price': Decimal('899.99'),
                    'category': consumer_cat,
                    'status': 'active',
                    'stock_quantity': 40,
                    'weight': Decimal('0.8'),
                    'shipping_type': 'physical',
                },
                'robot': {
                    'robot_type': 'consumer_drone',
                    'manufacturer': 'NeoTech Robotics',
                    'model_number': 'AX400-2024',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('0.8'),
                    'dimensions_length': Decimal('28.0'),
                    'dimensions_width': Decimal('28.0'),
                    'dimensions_height': Decimal('12.0'),
                    'max_speed_kmh': Decimal('45.0'),
                    'max_altitude_m': Decimal('300.0'),
                    'max_payload_kg': Decimal('0.3'),
                    'requires_verification': False,
                    'is_restricted': False,
                },
                'specs': {
                    'cpu': 'ARM Cortex-A78, Quad-core 2.4GHz',
                    'ram': '6GB LPDDR5',
                    'storage': '128GB UFS 3.1',
                    'gpu': 'Mali-G78 MP14',
                    'sensors': 'RGB Camera, Thermal Camera, LiDAR, IMU, Microphone Array',
                    'communication': 'WiFi 6E, Bluetooth 5.2, 4G/5G Optional',
                    'operating_system': 'Android-based Custom OS',
                },
                'ai': {
                    'ai_model': 'GPT-4o-based Voice Assistant, YOLO v8 Object Detection',
                    'has_autonomous_navigation': True,
                    'has_object_detection': True,
                    'has_path_planning': True,
                    'has_swarm_capabilities': False,
                },
                'power': {
                    'battery_type': 'Lithium-Ion',
                    'battery_capacity_mah': 5000,
                    'voltage_v': Decimal('7.4'),
                    'runtime_hours': Decimal('1.2'),
                    'charging_time_hours': Decimal('1.0'),
                    'power_consumption_w': Decimal('35.0'),
                },
            },
            # Commercial Drones
            {
                'product': {
                    'title': 'SurveyMaster X7 Industrial Drone',
                    'slug': 'surveymaster-x7-industrial-drone',
                    'short_description': 'Professional surveying and mapping drone with centimeter accuracy',
                    'description': '''The SurveyMaster X7 is a professional-grade commercial drone engineered for precision surveying, mapping, and inspection applications. Built for demanding industrial environments, this drone delivers centimeter-level accuracy required for construction, mining, agriculture, and infrastructure monitoring.

Equipped with advanced RTK-GPS technology and high-resolution cameras, the X7 captures detailed aerial imagery and generates precise 3D models, orthomosaics, and point clouds. Its robust construction and IP65 weather resistance ensure reliable operation in challenging conditions.

The drone features automated flight planning software that enables comprehensive area coverage with minimal pilot intervention. Real-time data processing capabilities allow for immediate analysis and decision-making on-site. With a maximum payload capacity of 5kg, the X7 can accommodate various specialized sensors including multispectral, thermal, and LiDAR systems.

Designed for compliance with commercial drone regulations worldwide, the SurveyMaster X7 includes comprehensive safety features and comprehensive documentation for certification processes.''',
                    'price': Decimal('24999.99'),
                    'category': commercial_cat,
                    'status': 'active',
                    'stock_quantity': 12,
                    'weight': Decimal('8.5'),
                    'shipping_type': 'physical',
                },
                'robot': {
                    'robot_type': 'commercial_drone',
                    'manufacturer': 'Precision Aerial Systems',
                    'model_number': 'SM-X7-2024',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('8.5'),
                    'dimensions_length': Decimal('95.0'),
                    'dimensions_width': Decimal('95.0'),
                    'dimensions_height': Decimal('35.0'),
                    'max_speed_kmh': Decimal('72.0'),
                    'max_altitude_m': Decimal('6000.0'),
                    'max_payload_kg': Decimal('5.0'),
                    'requires_verification': True,
                    'is_restricted': False,
                },
                'specs': {
                    'cpu': 'Intel Core i7-1185G7, Quad-core 4.8GHz',
                    'ram': '32GB DDR4',
                    'storage': '1TB NVMe SSD',
                    'gpu': 'NVIDIA RTX 3060',
                    'sensors': 'RTK-GPS, RGB Camera, Multispectral Camera, LiDAR, IMU',
                    'communication': '4G/5G, WiFi 6, Satellite Link, Radio Telemetry',
                    'operating_system': 'Linux-based Flight Control System',
                },
                'ai': {
                    'ai_model': 'Deep Learning-based Image Processing, SLAM Navigation',
                    'has_autonomous_navigation': True,
                    'has_object_detection': True,
                    'has_path_planning': True,
                    'has_swarm_capabilities': True,
                },
                'power': {
                    'battery_type': 'Lithium-Polymer',
                    'battery_capacity_mah': 30000,
                    'voltage_v': Decimal('22.2'),
                    'runtime_hours': Decimal('1.5'),
                    'charging_time_hours': Decimal('2.5'),
                    'power_consumption_w': Decimal('450.0'),
                },
            },
            {
                'product': {
                    'title': 'Cara Delivery Drone',
                    'slug': 'cara-delivery-drone',
                    'short_description': 'Autonomous last-mile delivery drone with advanced navigation',
                    'description': '''The Cara Delivery Drone revolutionizes last-mile logistics with its advanced autonomous delivery capabilities. Designed specifically for commercial package delivery, this drone combines reliability, safety, and efficiency to transform the delivery industry.

With a weather-resistant design and sophisticated obstacle avoidance systems, the Cara operates safely in urban environments. Its intelligent routing algorithms optimize delivery paths, reducing transit times and energy consumption. The drone features secure cargo compartments with multiple size options, accommodating packages up to 5kg.

The Cara's advanced computer vision system enables precise landing and package placement, while real-time tracking provides customers and businesses with complete visibility throughout the delivery process. Compliance with aviation regulations and integration with existing logistics networks makes the Cara an ideal solution for e-commerce, food delivery, and medical supply transportation.

Built with maintenance in mind, the Cara features modular components and comprehensive diagnostic systems, ensuring minimal downtime and reduced operational costs.''',
                    'price': Decimal('18999.99'),
                    'category': commercial_cat,
                    'status': 'active',
                    'stock_quantity': 30,
                    'weight': Decimal('12.0'),
                    'shipping_type': 'physical',
                },
                'robot': {
                    'robot_type': 'commercial_drone',
                    'manufacturer': 'LogiDrone Technologies',
                    'model_number': 'CARA-DLV-2024',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('12.0'),
                    'dimensions_length': Decimal('110.0'),
                    'dimensions_width': Decimal('110.0'),
                    'dimensions_height': Decimal('40.0'),
                    'max_speed_kmh': Decimal('90.0'),
                    'max_altitude_m': Decimal('120.0'),
                    'max_payload_kg': Decimal('5.0'),
                    'requires_verification': True,
                    'is_restricted': False,
                },
                'specs': {
                    'cpu': 'Qualcomm QCS8250, Octa-core',
                    'ram': '16GB LPDDR5',
                    'storage': '256GB UFS 3.1',
                    'gpu': 'Adreno 690',
                    'sensors': 'GPS, IMU, RGB Camera, LiDAR, Ultrasonic Sensors',
                    'communication': '5G, WiFi 6, Bluetooth 5.2, Radio',
                    'operating_system': 'Android-based Delivery OS',
                },
                'ai': {
                    'ai_model': 'Reinforcement Learning Navigation, Object Recognition',
                    'has_autonomous_navigation': True,
                    'has_object_detection': True,
                    'has_path_planning': True,
                    'has_swarm_capabilities': True,
                },
                'power': {
                    'battery_type': 'Lithium-Ion',
                    'battery_capacity_mah': 25000,
                    'voltage_v': Decimal('44.4'),
                    'runtime_hours': Decimal('1.0'),
                    'charging_time_hours': Decimal('2.0'),
                    'power_consumption_w': Decimal('600.0'),
                },
            },
            # Humanoid Robots
            {
                'product': {
                    'title': 'Atlas Prime Humanoid Service Robot',
                    'slug': 'atlas-prime-humanoid-service-robot',
                    'short_description': 'Advanced humanoid robot for service and research applications',
                    'description': '''The Atlas Prime represents the pinnacle of humanoid robotics technology, designed for complex service tasks in dynamic environments. Standing at 1.5 meters with 32 degrees of freedom, this humanoid robot combines advanced bipedal locomotion with sophisticated manipulation capabilities.

Built on decades of robotics research, the Atlas Prime features cutting-edge hydraulic actuators and control systems that enable natural, human-like movement. Its advanced balance and coordination algorithms allow it to navigate uneven terrain, climb stairs, and maintain stability in challenging conditions.

Equipped with state-of-the-art perception systems including stereo vision, LiDAR, and force sensors, the Atlas Prime can understand and interact with its environment in real-time. The robot's hands feature precise finger control, enabling it to manipulate objects with human-like dexterity.

Designed for research institutions, advanced manufacturing, and specialized service applications, the Atlas Prime serves as a platform for developing next-generation robotics applications. Its modular architecture allows for customization and integration of specialized sensors and tools.''',
                    'price': Decimal('249999.99'),
                    'category': humanoid_cat,
                    'status': 'active',
                    'stock_quantity': 5,
                    'weight': Decimal('89.0'),
                    'shipping_type': 'physical',
                },
                'robot': {
                    'robot_type': 'humanoid_robot',
                    'manufacturer': 'Boston Dynamics Advanced',
                    'model_number': 'ATLAS-PRIME-2024',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('89.0'),
                    'dimensions_length': Decimal('80.0'),
                    'dimensions_width': Decimal('50.0'),
                    'dimensions_height': Decimal('150.0'),
                    'max_speed_kmh': Decimal('9.0'),
                    'max_altitude_m': Decimal('0.0'),
                    'max_payload_kg': Decimal('11.0'),
                    'requires_verification': True,
                    'is_restricted': False,
                },
                'specs': {
                    'cpu': 'Intel Core i9-12900K, 16-core',
                    'ram': '64GB DDR5',
                    'storage': '2TB NVMe SSD',
                    'gpu': 'NVIDIA RTX 4090',
                    'sensors': 'Stereo Vision, LiDAR, IMU, Force/Torque Sensors, Tactile Sensors',
                    'communication': 'Ethernet, WiFi 6E, 5G',
                    'operating_system': 'ROS 2 (Robot Operating System)',
                },
                'ai': {
                    'ai_model': 'Deep Reinforcement Learning Locomotion, Vision-based Manipulation',
                    'has_autonomous_navigation': True,
                    'has_object_detection': True,
                    'has_path_planning': True,
                    'has_swarm_capabilities': False,
                },
                'power': {
                    'battery_type': 'Lithium-Ion',
                    'battery_capacity_mah': 0,  # Hydraulic system
                    'voltage_v': Decimal('48.0'),
                    'runtime_hours': Decimal('1.0'),
                    'charging_time_hours': Decimal('4.0'),
                    'power_consumption_w': Decimal('1500.0'),
                },
            },
            # Military Robots (first few)
            {
                'product': {
                    'title': 'ARES-X1 Tactical Autonomous System',
                    'slug': 'ares-x1-tactical-autonomous-system',
                    'short_description': 'Military-grade autonomous drone for tactical operations',
                    'description': '''The ARES-X1 Tactical Autonomous System is a next-generation military-grade autonomous platform designed for intelligence, surveillance, and reconnaissance (ISR) missions. Built to military specifications with enhanced survivability and mission endurance, this system operates in contested environments with advanced threat detection and evasion capabilities.

Featuring encrypted communications, anti-jamming technology, and low-observable design, the ARES-X1 provides persistent surveillance while maintaining operational security. Its modular payload system accommodates various sensors including electro-optical, infrared, and signals intelligence equipment.

The system's advanced AI enables autonomous mission planning, target tracking, and decision-making in dynamic combat environments. With extended range and endurance, the ARES-X1 can operate independently for extended periods, relaying critical intelligence to command centers in real-time.

Certified for military use and compliant with international defense standards, the ARES-X1 represents the cutting edge of autonomous military technology. Subject to export control regulations and requires appropriate clearance and authorization.''',
                    'price': Decimal('1250000.00'),
                    'category': military_cat,
                    'status': 'active',
                    'stock_quantity': 8,
                    'weight': Decimal('45.0'),
                    'shipping_type': 'physical',
                },
                'robot': {
                    'robot_type': 'military_autonomous',
                    'manufacturer': 'ARES Defense Systems',
                    'model_number': 'ARES-X1-2024',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('45.0'),
                    'dimensions_length': Decimal('250.0'),
                    'dimensions_width': Decimal('180.0'),
                    'dimensions_height': Decimal('80.0'),
                    'max_speed_kmh': Decimal('200.0'),
                    'max_altitude_m': Decimal('12000.0'),
                    'max_payload_kg': Decimal('25.0'),
                    'requires_verification': True,
                    'is_restricted': True,
                },
                'specs': {
                    'cpu': 'RAD750 Radiation-Hardened Processor, Dual-core',
                    'ram': '16GB Radiation-Hardened Memory',
                    'storage': '512GB Solid-State Drive (Rad-Hard)',
                    'gpu': 'Custom FPGA Processing Unit',
                    'sensors': 'EO/IR Camera, Radar, SIGINT Equipment, GPS/INS',
                    'communication': 'Encrypted Radio, Satellite Link, Data Link',
                    'operating_system': 'MIL-STD-1553 Compliant Operating System',
                },
                'ai': {
                    'ai_model': 'Classified AI Systems for Autonomous Operations',
                    'has_autonomous_navigation': True,
                    'has_object_detection': True,
                    'has_path_planning': True,
                    'has_swarm_capabilities': True,
                },
                'power': {
                    'battery_type': 'Fuel Cell + Lithium-Ion Hybrid',
                    'battery_capacity_mah': 0,
                    'voltage_v': Decimal('270.0'),
                    'runtime_hours': Decimal('24.0'),
                    'charging_time_hours': Decimal('6.0'),
                    'power_consumption_w': Decimal('2000.0'),
                },
                'restriction': {
                    'restriction_level': 'military_only',
                    'requires_verification': True,
                    'requires_export_license': True,
                    'restricted_countries': 'North Korea, Iran, Syria, Russia',
                    'usage_notes': 'Military/defense use only. Requires military clearance and export authorization. Subject to ITAR regulations.',
                },
            },
        ]

        # Create products and robots
        created_count = 0
        for robot_data in robots_data:
            try:
                # Create product
                product = Product.objects.create(
                    seller=admin_user,
                    title=robot_data['product']['title'],
                    slug=robot_data['product']['slug'],
                    short_description=robot_data['product']['short_description'],
                    description=robot_data['product']['description'],
                    price=robot_data['product']['price'],
                    category=robot_data['product']['category'],
                    status=robot_data['product']['status'],
                    stock_quantity=robot_data['product']['stock_quantity'],
                    weight=robot_data['product']['weight'],
                    shipping_type=robot_data['product']['shipping_type'],
                    visibility=True,
                    track_inventory=True,
                )

                # Create robot
                robot = Robot.objects.create(
                    product=product,
                    robot_type=robot_data['robot']['robot_type'],
                    manufacturer=robot_data['robot']['manufacturer'],
                    model_number=robot_data['robot']['model_number'],
                    year_manufactured=robot_data['robot']['year_manufactured'],
                    weight_kg=robot_data['robot']['weight_kg'],
                    dimensions_length=robot_data['robot']['dimensions_length'],
                    dimensions_width=robot_data['robot']['dimensions_width'],
                    dimensions_height=robot_data['robot']['dimensions_height'],
                    max_speed_kmh=robot_data['robot']['max_speed_kmh'],
                    max_altitude_m=robot_data['robot']['max_altitude_m'],
                    max_payload_kg=robot_data['robot']['max_payload_kg'],
                    requires_verification=robot_data['robot']['requires_verification'],
                    is_restricted=robot_data['robot']['is_restricted'],
                )

                # Create specifications
                specs_data = robot_data['specs']
                RobotSpecification.objects.create(
                    robot=robot,
                    cpu_model=specs_data['cpu'],
                    ram_gb=Decimal('16.0') if '16GB' in specs_data['ram'] else Decimal('8.0'),
                    storage_gb=Decimal('512.0') if '512GB' in specs_data['storage'] else Decimal('256.0'),
                    gpu_model=specs_data.get('gpu', ''),
                    sensor_list=specs_data['sensors'].split(', '),
                    communication_protocols=specs_data['communication'].split(', '),
                    operating_system=specs_data['operating_system'],
                    gps_enabled=True,
                    imu_enabled=True,
                )

                # Create AI details
                ai_data = robot_data['ai']
                AISystemDetails.objects.create(
                    robot=robot,
                    model_name=ai_data['ai_model'],
                    has_autonomous_navigation=ai_data['has_autonomous_navigation'],
                    has_object_recognition=ai_data.get('has_object_detection', False),
                    has_decision_making=True,
                )

                # Create power system
                power_data = robot_data['power']
                battery_type_map = {
                    'Lithium-Ion': 'lithium_ion',
                    'Lithium-Polymer': 'lithium_polymer',
                    'Fuel Cell': 'fuel_cell',
                    'Fuel Cell + Lithium-Ion Hybrid': 'fuel_cell',
                }
                PowerSystem.objects.create(
                    robot=robot,
                    battery_type=battery_type_map.get(power_data['battery_type'], 'lithium_ion'),
                    battery_capacity_mah=power_data.get('battery_capacity_mah') or None,
                    battery_voltage_v=power_data['voltage_v'],
                    operating_time_minutes=int(float(power_data['runtime_hours']) * 60) if power_data.get('runtime_hours') else None,
                    charging_time_minutes=int(float(power_data['charging_time_hours']) * 60) if power_data.get('charging_time_hours') else None,
                    operating_power_w=power_data.get('power_consumption_w'),
                )

                # Create usage restriction if specified
                if 'restriction' in robot_data:
                    restr_data = robot_data['restriction']
                    UsageRestriction.objects.create(
                        robot=robot,
                        restriction_level=restr_data['restriction_level'],
                        requires_verification=restr_data['requires_verification'],
                        requires_export_license=restr_data['requires_export_license'],
                    )

                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {product.title}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating {robot_data["product"]["title"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} professional robots!'))

