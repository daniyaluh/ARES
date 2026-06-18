"""
Django management command to add military-grade autonomous and war machine robots.
These robots require military clearance level access.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from products.models import (
    Category, Product, Robot, RobotSpecification, AISystemDetails,
    PowerSystem, UsageRestriction, ProductGallery
)
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Add 5-6 military-grade autonomous and war machine robots with full specifications'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating military-grade robots...'))
        
        # Get or create admin user as seller
        try:
            seller = User.objects.filter(is_staff=True).first()
            if not seller:
                seller = User.objects.create_user(
                    email='admin@ares.com',
                    username='admin',
                    password='admin1234',
                    is_staff=True,
                    is_superuser=True
                )
            self.stdout.write(f'Using seller: {seller.email}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting seller: {e}'))
            return
        
        # Get or create Military category
        category, _ = Category.objects.get_or_create(
            slug='military-autonomous-systems',
            defaults={
                'name': 'Military Autonomous Systems',
                'description': 'Military-grade autonomous systems and war machines requiring clearance',
                'is_active': True,
            }
        )
        
        # Military robot data
        military_robots = [
            {
                'product': {
                    'title': 'ARES-MK7 Combat Autonomous Ground Vehicle',
                    'short_description': 'Next-generation autonomous combat vehicle with AI-driven tactical decision making',
                    'description': '''The ARES-MK7 Combat Autonomous Ground Vehicle represents the pinnacle of military robotics technology. This fully autonomous combat platform integrates advanced artificial intelligence with hardened military hardware for unprecedented battlefield capabilities.

**Key Features:**
- Fully autonomous operation with human override capabilities
- AI-powered threat detection and engagement systems
- Modular weapon systems compatible with standard NATO platforms
- Advanced armor plating rated for small arms and shrapnel
- Silent electric drive system for stealth operations
- Integrated command and control systems for squad coordination

**Capabilities:**
- Autonomous navigation in urban and hostile terrain
- Real-time threat assessment and response protocols
- Multi-spectral sensor suite for 360° situational awareness
- Remote operation via secure military networks
- Autonomous resupply and logistics support

**Clearance Required:** TOP SECRET / Military Personnel Only
**Export Control:** ITAR Restricted
**End-Use Certificate:** Required''',
                    'price': Decimal('2850000.00'),
                    'stock_quantity': 3,
                    'status': 'active',
                    'is_featured': True,
                },
                'robot': {
                    'robot_type': 'military_autonomous',
                    'model_number': 'ARES-MK7-CAGV-2024',
                    'manufacturer': 'ARES Defense Systems',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('1850.00'),
                    'dimensions_length': Decimal('450.00'),
                    'dimensions_width': Decimal('220.00'),
                    'dimensions_height': Decimal('180.00'),
                    'max_speed_kmh': Decimal('95.00'),
                    'max_payload_kg': Decimal('1200.00'),
                    'requires_verification': True,
                    'is_restricted': True,
                },
                'specs': {
                    'cpu_model': 'NVIDIA A100 80GB',
                    'cpu_cores': 128,
                    'ram_gb': Decimal('512.00'),
                    'storage_gb': Decimal('2000.00'),
                    'gpu_model': 'Dual NVIDIA A100',
                    'camera_resolution': '8K',
                    'camera_count': 12,
                    'lidar_enabled': True,
                    'radar_enabled': True,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'sensor_list': ['LiDAR 360°', 'Radar Array', 'Thermal Imaging', 'Night Vision', 'Chemical Detection', 'Acoustic Sensors'],
                    'wifi_standard': 'Military Grade Encrypted',
                    'cellular_support': True,
                    'motor_count': 6,
                    'motor_type': 'Brushless DC with regenerative braking',
                    'operating_system': 'ARES Military Linux 3.0',
                    'sdk_available': False,
                    'firmware_version': 'MK7-2024.1-SEC',
                },
                'ai_system': {
                    'ai_types': ['reinforcement_learning', 'sensor_fusion', 'path_planning', 'object_detection'],
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'ARES-MK7-Tactical-AI',
                    'model_version': '3.2.1',
                    'model_framework': 'PyTorch',
                    'training_data_size': '500TB',
                    'inference_speed_ms': 12,
                    'supports_online_learning': True,
                    'edge_inference': True,
                    'has_explainability': False,
                },
                'power': {
                    'battery_type': 'lithium_ion',
                    'battery_capacity_mah': 8500000,  # ~85000Wh at ~10V
                    'battery_voltage_v': Decimal('10.00'),
                    'operating_time_minutes': 2880,  # 48 hours
                    'charging_time_minutes': 270,  # 4.5 hours
                    # Power values too large for max_digits=6, leaving blank
                    # operating_power_w: 450000W (exceeds 9999.99 limit)
                    # peak_power_w: 500000W (exceeds 9999.99 limit)
                    'has_fast_charging': True,
                },
                'restrictions': {
                    'restriction_level': 'military_only',
                    'requires_verification': True,
                    'military_use_allowed': True,
                    'export_control_classification': 'ITAR Restricted',
                    'requires_export_license': True,
                    'restricted_airspace': True,
                }
            },
            {
                'product': {
                    'title': 'Titan-X8 Autonomous Attack Drone System',
                    'short_description': 'Stealth-capable autonomous attack drone with swarm intelligence capabilities',
                    'description': '''The Titan-X8 Autonomous Attack Drone System is a cutting-edge unmanned aerial combat platform designed for precision strikes and intelligence gathering in contested airspace.

**Mission Capabilities:**
- Autonomous flight with AI-driven mission planning
- Swarm coordination for multi-drone operations
- Precision strike capabilities with guided munitions
- Electronic warfare and jamming systems
- Real-time intelligence, surveillance, and reconnaissance (ISR)
- Stealth design for low radar cross-section

**Technical Specifications:**
- Advanced composite materials for reduced detectability
- Hybrid propulsion system (electric + micro-turbine)
- Multi-spectral stealth coating
- AI-powered target recognition and classification
- Autonomous threat evasion and counter-measures
- Secure encrypted communication links

**Operational Features:**
- Autonomous mission execution with human oversight
- Swarm intelligence for coordinated attacks
- Adaptive flight path planning
- Real-time battlefield intelligence fusion
- Autonomous return-to-base capabilities

**Clearance Required:** SECRET / Military Personnel Only
**Export Control:** ITAR Restricted / Dual-Use Regulated''',
                    'price': Decimal('1250000.00'),
                    'stock_quantity': 8,
                    'status': 'active',
                    'is_featured': True,
                },
                'robot': {
                    'robot_type': 'military_autonomous',
                    'model_number': 'TITAN-X8-2024',
                    'manufacturer': 'Titan Aerospace Defense',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('85.00'),
                    'dimensions_length': Decimal('320.00'),
                    'dimensions_width': Decimal('280.00'),
                    'dimensions_height': Decimal('45.00'),
                    'max_speed_kmh': Decimal('420.00'),
                    'max_altitude_m': Decimal('15000.00'),
                    'max_payload_kg': Decimal('45.00'),
                    'requires_verification': True,
                    'is_restricted': True,
                },
                'specs': {
                    'cpu_model': 'Qualcomm QCS8250',
                    'cpu_cores': 24,
                    'ram_gb': Decimal('128.00'),
                    'storage_gb': Decimal('512.00'),
                    'gpu_model': 'Qualcomm Adreno 690',
                    'camera_resolution': '4K HDR',
                    'camera_count': 8,
                    'lidar_enabled': True,
                    'radar_enabled': True,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'sensor_list': ['EO/IR Gimbal', 'SAR Radar', 'ESM Sensors', 'LiDAR', 'Multispectral Imaging'],
                    'wifi_standard': 'Military Encrypted',
                    'cellular_support': True,
                    'motor_count': 8,
                    'motor_type': 'Brushless DC with variable pitch',
                    'operating_system': 'TitanOS Military 2.0',
                    'sdk_available': False,
                    'firmware_version': 'X8-2024.2-SEC',
                },
                'ai_system': {
                    'ai_types': ['reinforcement_learning', 'sensor_fusion', 'path_planning'],
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'Titan-X8-Swarm-AI',
                    'model_version': '2.5.0',
                    'model_framework': 'TensorFlow',
                    'training_data_size': '250TB',
                    'inference_speed_ms': 8,
                    'supports_online_learning': True,
                    'edge_inference': True,
                },
                'power': {
                    'battery_type': 'lithium_polymer',
                    'battery_capacity_mah': 1500000,  # ~15000Wh at ~10V
                    'battery_voltage_v': Decimal('10.00'),
                    'operating_time_minutes': 360,  # 6 hours
                    'charging_time_minutes': 120,  # 2 hours
                    # Power values too large for max_digits=6, leaving blank
                    'has_fast_charging': True,
                },
                'restrictions': {
                    'restriction_level': 'military_only',
                    'requires_verification': True,
                    'military_use_allowed': True,
                    'export_control_classification': 'ITAR Restricted',
                    'requires_export_license': True,
                    'restricted_airspace': True,
                }
            },
            {
                'product': {
                    'title': 'Vanguard-H9 Autonomous Humanoid Combat Unit',
                    'short_description': 'Bipedal autonomous humanoid designed for urban warfare and CQB operations',
                    'description': '''The Vanguard-H9 represents a breakthrough in humanoid military robotics, designed for operations in complex urban environments where traditional vehicles cannot operate effectively.

**Unique Capabilities:**
- Human-like bipedal locomotion for navigation in buildings
- Advanced CQB (Close Quarters Battle) protocols
- Autonomous door breaching and room clearing
- Human-robot team coordination
- Modular weapon integration
- Biometric threat identification

**Physical Specifications:**
- Human-scale design (180cm height) for standard infrastructure compatibility
- Advanced joint actuators with human-like range of motion
- Durable composite exoskeleton
- Tactile sensors for manipulation tasks
- Advanced balance and stability systems

**Combat Features:**
- Autonomous threat engagement protocols
- Integrated weapon systems (rifle, sidearm, tactical equipment)
- Advanced armor protection
- Self-diagnostic and field repair capabilities
- Secure communication with human operators
- Autonomous medical aid capabilities

**Operational Use:**
- Urban warfare and building clearing
- Hostage rescue operations
- Perimeter defense
- Forward observation and intelligence
- Tactical support for special forces

**Clearance Required:** TOP SECRET / Special Operations Personnel
**Export Control:** ITAR Restricted / Prohibited Export''',
                    'price': Decimal('4200000.00'),
                    'stock_quantity': 2,
                    'status': 'active',
                    'is_featured': True,
                },
                'robot': {
                    'robot_type': 'military_autonomous',
                    'model_number': 'VG-H9-2024',
                    'manufacturer': 'Vanguard Robotics Systems',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('125.00'),
                    'dimensions_length': Decimal('85.00'),
                    'dimensions_width': Decimal('45.00'),
                    'dimensions_height': Decimal('180.00'),
                    'max_speed_kmh': Decimal('25.00'),
                    'max_payload_kg': Decimal('35.00'),
                    'requires_verification': True,
                    'is_restricted': True,
                },
                'specs': {
                    'cpu_model': 'AMD EPYC 9554',
                    'cpu_cores': 128,
                    'ram_gb': Decimal('256.00'),
                    'storage_gb': Decimal('1000.00'),
                    'gpu_model': 'NVIDIA RTX 6000 Ada',
                    'camera_resolution': '4K',
                    'camera_count': 6,
                    'lidar_enabled': True,
                    'radar_enabled': False,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'sensor_list': ['Stereo Vision', 'LiDAR', 'Tactile Sensors', 'Force/Torque Sensors', 'Audio Array'],
                    'wifi_standard': 'Military Encrypted',
                    'cellular_support': True,
                    'servo_count': 28,
                    'motor_type': 'High-torque brushless servo',
                    'operating_system': 'VanguardOS 4.0',
                    'sdk_available': False,
                    'firmware_version': 'H9-2024.1-SPEC-OPS',
                },
                'ai_system': {
                    'ai_types': ['reinforcement_learning', 'computer_vision', 'sensor_fusion'],
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'Vanguard-H9-Behavior-AI',
                    'model_version': '4.1.0',
                    'model_framework': 'PyTorch',
                    'training_data_size': '800TB',
                    'inference_speed_ms': 15,
                    'supports_online_learning': True,
                    'edge_inference': True,
                },
                'power': {
                    'battery_type': 'lithium_ion',
                    'battery_capacity_mah': 1200000,  # ~12000Wh at ~10V
                    'battery_voltage_v': Decimal('10.00'),
                    'operating_time_minutes': 480,  # 8 hours
                    'charging_time_minutes': 180,  # 3 hours
                    'operating_power_w': Decimal('9999.99'),  # Max allowed (actual 15000)
                    'peak_power_w': Decimal('9999.99'),  # Max allowed (actual 20000)
                    'has_fast_charging': True,
                },
                'restrictions': {
                    'restriction_level': 'military_only',
                    'requires_verification': True,
                    'military_use_allowed': True,
                    'export_control_classification': 'ITAR Restricted',
                    'requires_export_license': True,
                }
            },
            {
                'product': {
                    'title': 'Spectre-M12 Naval Autonomous Submersible',
                    'short_description': 'Unmanned underwater vehicle for mine countermeasures and intelligence gathering',
                    'description': '''The Spectre-M12 is an advanced autonomous underwater vehicle (AUV) designed for naval operations including mine detection, intelligence gathering, and underwater surveillance.

**Maritime Capabilities:**
- Autonomous underwater navigation and mission execution
- Mine detection and classification systems
- Underwater intelligence gathering
- Port security and surveillance
- Underwater infrastructure inspection
- Autonomous deployment from submarines or surface vessels

**Technical Features:**
- Deep diving capability (6000m depth rating)
- Long-endurance operations (72+ hours)
- Stealth acoustic signature reduction
- Advanced sonar array systems
- Autonomous obstacle avoidance
- Secure underwater communication links

**Sensor Suite:**
- Multi-beam sonar systems
- Side-scan sonar for seabed mapping
- Forward-looking sonar
- Magnetic anomaly detection
- Chemical and biological sensors
- High-resolution underwater cameras

**Operational Modes:**
- Fully autonomous mission execution
- Remote operator control
- Hybrid autonomous/remote operation
- Swarm coordination capabilities
- Autonomous return and recovery

**Clearance Required:** SECRET / Naval Personnel Only
**Export Control:** ITAR Restricted / Naval Export Controls''',
                    'price': Decimal('1850000.00'),
                    'stock_quantity': 5,
                    'status': 'active',
                    'is_featured': False,
                },
                'robot': {
                    'robot_type': 'military_autonomous',
                    'model_number': 'SPECTRE-M12-2024',
                    'manufacturer': 'Naval Robotics Corporation',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('850.00'),
                    'dimensions_length': Decimal('450.00'),
                    'dimensions_width': Decimal('80.00'),
                    'dimensions_height': Decimal('60.00'),
                    'max_speed_kmh': Decimal('25.00'),  # Underwater
                    'requires_verification': True,
                    'is_restricted': True,
                },
                'specs': {
                    'cpu_model': 'Intel Xeon D-2796',
                    'cpu_cores': 40,
                    'ram_gb': Decimal('128.00'),
                    'storage_gb': Decimal('2000.00'),
                    'camera_resolution': '4K',
                    'camera_count': 4,
                    'lidar_enabled': False,
                    'radar_enabled': False,
                    'gps_enabled': False,  # Underwater GPS not available
                    'imu_enabled': True,
                    'sensor_list': ['Multi-beam Sonar', 'Side-scan Sonar', 'Magnetometer', 'Depth Sensors', 'Acoustic Doppler'],
                    'wifi_standard': 'Underwater Acoustic Communication',
                    'motor_count': 6,
                    'motor_type': 'Brushless thruster',
                    'operating_system': 'SpectreOS Naval 3.0',
                    'sdk_available': False,
                    'firmware_version': 'M12-2024.1-NAVAL',
                },
                'ai_system': {
                    'ai_types': ['supervised_learning', 'sensor_fusion', 'path_planning'],
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'Spectre-M12-Sonar-AI',
                    'model_version': '1.8.2',
                    'model_framework': 'TensorFlow',
                    'training_data_size': '150TB',
                    'inference_speed_ms': 25,
                    'supports_online_learning': False,
                    'edge_inference': True,
                },
                'power': {
                    'battery_type': 'lithium_ion',
                    'battery_capacity_mah': 5000000,  # ~50000Wh at ~10V
                    'battery_voltage_v': Decimal('10.00'),
                    'operating_time_minutes': 4320,  # 72 hours
                    'charging_time_minutes': 360,  # 6 hours
                    # Power values too large for max_digits=6, leaving blank
                },
                'restrictions': {
                    'restriction_level': 'military_only',
                    'requires_verification': True,
                    'military_use_allowed': True,
                    'export_control_classification': 'ITAR Restricted',
                    'requires_export_license': True,
                }
            },
            {
                'product': {
                    'title': 'Raven-S4 Autonomous Reconnaissance Quadcopter',
                    'short_description': 'Stealth reconnaissance drone with advanced sensor fusion and autonomous patrolling',
                    'description': '''The Raven-S4 is a compact, stealth-capable autonomous reconnaissance platform designed for covert surveillance and intelligence gathering operations.

**Reconnaissance Capabilities:**
- Silent operation with noise-reduction systems
- Advanced multi-spectral imaging
- Long-range communication capabilities
- Autonomous patrolling with waypoint navigation
- Real-time data transmission to command centers
- Autonomous return-to-base on low battery

**Stealth Features:**
- Low radar cross-section design
- Acoustic signature reduction
- Thermal signature masking
- Visual camouflage options
- Low electromagnetic emissions
- Autonomous evasion protocols

**Sensor Payload:**
- High-resolution optical camera with zoom
- Thermal imaging camera
- Multi-spectral sensor array
- Electronic intelligence (ELINT) sensors
- Signals intelligence (SIGINT) capabilities
- LiDAR for 3D mapping

**Mission Types:**
- Area surveillance and monitoring
- Target identification and tracking
- Border patrol operations
- Forward observation
- Battle damage assessment
- Search and rescue support

**Clearance Required:** SECRET / Intelligence Personnel
**Export Control:** ITAR Restricted / Dual-Use Regulated''',
                    'price': Decimal('450000.00'),
                    'stock_quantity': 15,
                    'status': 'active',
                    'is_featured': False,
                },
                'robot': {
                    'robot_type': 'military_autonomous',
                    'model_number': 'RAVEN-S4-2024',
                    'manufacturer': 'Raven Defense Technologies',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('12.50'),
                    'dimensions_length': Decimal('85.00'),
                    'dimensions_width': Decimal('85.00'),
                    'dimensions_height': Decimal('30.00'),
                    'max_speed_kmh': Decimal('95.00'),
                    'max_altitude_m': Decimal('6000.00'),
                    'max_payload_kg': Decimal('3.50'),
                    'requires_verification': True,
                    'is_restricted': True,
                },
                'specs': {
                    'cpu_model': 'NVIDIA Jetson AGX Orin',
                    'cpu_cores': 12,
                    'ram_gb': Decimal('64.00'),
                    'storage_gb': Decimal('256.00'),
                    'gpu_model': 'NVIDIA Ampere (1024-core)',
                    'camera_resolution': '4K',
                    'camera_count': 3,
                    'lidar_enabled': True,
                    'radar_enabled': False,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'sensor_list': ['EO Camera', 'Thermal Camera', 'Multi-spectral Sensors', 'LiDAR', 'Magnetometer'],
                    'wifi_standard': 'Military Encrypted Long-Range',
                    'cellular_support': True,
                    'motor_count': 4,
                    'motor_type': 'Brushless DC with noise reduction',
                    'operating_system': 'RavenOS 2.5',
                    'sdk_available': False,
                    'firmware_version': 'S4-2024.1-INTEL',
                },
                'ai_system': {
                    'ai_types': ['computer_vision', 'sensor_fusion', 'path_planning'],
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'Raven-S4-Vision-AI',
                    'model_version': '2.0.1',
                    'model_framework': 'TensorFlow Lite',
                    'training_data_size': '100TB',
                    'inference_speed_ms': 10,
                    'supports_online_learning': False,
                    'edge_inference': True,
                },
                'power': {
                    'battery_type': 'lithium_polymer',
                    'battery_capacity_mah': 300000,  # ~3000Wh at ~10V
                    'battery_voltage_v': Decimal('10.00'),
                    'operating_time_minutes': 270,  # 4.5 hours
                    'charging_time_minutes': 90,  # 1.5 hours
                    'operating_power_w': Decimal('8000.00'),
                    'peak_power_w': Decimal('9999.99'),  # Max allowed
                    'has_fast_charging': True,
                },
                'restrictions': {
                    'restriction_level': 'military_only',
                    'requires_verification': True,
                    'military_use_allowed': True,
                    'export_control_classification': 'ITAR Restricted',
                    'requires_export_license': True,
                    'restricted_airspace': True,
                }
            },
            {
                'product': {
                    'title': 'Warden-A6 Autonomous Perimeter Defense System',
                    'short_description': 'Ground-based autonomous sentry system with integrated weapon systems',
                    'description': '''The Warden-A6 is an autonomous ground-based perimeter defense system designed for protecting military installations, forward operating bases, and critical infrastructure.

**Defense Capabilities:**
- 360° autonomous threat detection and engagement
- Integrated non-lethal and lethal weapon options
- Multi-threat classification and response protocols
- Perimeter patrolling with autonomous route planning
- Integration with base defense networks
- Autonomous threat escalation protocols

**Detection Systems:**
- Multi-spectral sensor fusion
- Long-range target identification
- Biometric recognition capabilities
- Vehicle and personnel classification
- Autonomous IFF (Identify Friend or Foe)
- Intrusion detection and alerting

**Weapon Systems:**
- Modular weapon mounting (remote weapons station compatible)
- Non-lethal deterrents (acoustic, visual, gas)
- Lethal engagement protocols (with authorization)
- Automatic target tracking
- Precision engagement capabilities
- Autonomous reloading systems

**Operational Features:**
- Fully autonomous 24/7 operation
- Weather-resistant operation
- Autonomous maintenance alerts
- Integration with command and control
- Historical threat pattern analysis
- Autonomous patrol route optimization

**Clearance Required:** SECRET / Base Security Personnel
**Export Control:** ITAR Restricted / Dual-Use Regulated''',
                    'price': Decimal('950000.00'),
                    'stock_quantity': 12,
                    'status': 'active',
                    'is_featured': False,
                },
                'robot': {
                    'robot_type': 'military_autonomous',
                    'model_number': 'WARDEN-A6-2024',
                    'manufacturer': 'Defense Systems International',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('450.00'),
                    'dimensions_length': Decimal('180.00'),
                    'dimensions_width': Decimal('150.00'),
                    'dimensions_height': Decimal('220.00'),
                    'max_speed_kmh': Decimal('35.00'),
                    'requires_verification': True,
                    'is_restricted': True,
                },
                'specs': {
                    'cpu_model': 'NVIDIA A6000',
                    'cpu_cores': 48,
                    'ram_gb': Decimal('128.00'),
                    'storage_gb': Decimal('1000.00'),
                    'gpu_model': 'NVIDIA A6000',
                    'camera_resolution': '8K',
                    'camera_count': 8,
                    'lidar_enabled': True,
                    'radar_enabled': True,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'sensor_list': ['360° Camera Array', 'Radar', 'LiDAR', 'Thermal Imaging', 'Acoustic Sensors', 'Motion Detectors'],
                    'wifi_standard': 'Military Encrypted',
                    'cellular_support': True,
                    'motor_count': 4,
                    'motor_type': 'All-terrain brushless',
                    'operating_system': 'WardenOS 3.0',
                    'sdk_available': False,
                    'firmware_version': 'A6-2024.1-DEFENSE',
                },
                'ai_system': {
                    'ai_types': ['computer_vision', 'sensor_fusion', 'object_detection'],
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'Warden-A6-Threat-AI',
                    'model_version': '3.0.0',
                    'model_framework': 'PyTorch',
                    'training_data_size': '300TB',
                    'inference_speed_ms': 20,
                    'supports_online_learning': True,
                    'edge_inference': True,
                },
                'power': {
                    'battery_type': 'lithium_ion',
                    'battery_capacity_mah': 2500000,  # ~25000Wh at ~10V
                    'battery_voltage_v': Decimal('10.00'),
                    'operating_time_minutes': 2880,  # 48 hours
                    'charging_time_minutes': 300,  # 5 hours
                    # Power values too large for max_digits=6, leaving blank
                    'supports_solar_charging': True,
                },
                'restrictions': {
                    'restriction_level': 'military_only',
                    'requires_verification': True,
                    'military_use_allowed': True,
                    'export_control_classification': 'ITAR Restricted',
                    'requires_export_license': True,
                }
            },
        ]
        
        created_count = 0
        
        for robot_data in military_robots:
            try:
                # Create Product
                product = Product.objects.create(
                    seller=seller,
                    category=category,
                    **robot_data['product']
                )
                
                # Create Robot
                robot = Robot.objects.create(
                    product=product,
                    **robot_data['robot']
                )
                
                # Create RobotSpecification
                RobotSpecification.objects.create(
                    robot=robot,
                    **robot_data['specs']
                )
                
                # Create AISystemDetails
                AISystemDetails.objects.create(
                    robot=robot,
                    **robot_data['ai_system']
                )
                
                # Create PowerSystem
                PowerSystem.objects.create(
                    robot=robot,
                    **robot_data['power']
                )
                
                # Create UsageRestriction (links to robot, not product)
                UsageRestriction.objects.create(
                    robot=robot,
                    **robot_data['restrictions']
                )
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {product.title}')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating {robot_data["product"]["title"]}: {str(e)}')
                )
                import traceback
                traceback.print_exc()
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} military-grade robots')
        )
        self.stdout.write(
            self.style.WARNING('\nWARNING: All robots require military clearance level verification')
        )

