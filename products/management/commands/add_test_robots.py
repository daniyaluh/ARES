"""
Management command to add 10 test robots with detailed specifications.
3 Humanoids, 2 Drones, 3 Military War Machines, 2 Others (Industrial/Service)
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from products.models import (
    Product, Robot, Category, RobotSpecification, AISystemDetails,
    PowerSystem, UsageRestriction, ProductGallery
)
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Add 10 test robots with detailed specifications'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting robot creation...'))
        
        # Get or create seller
        try:
            seller = CustomUser.objects.get(email='seller@ares.com')
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR('Seller user not found. Please run setup_test_users first.'))
            return
        
        # Get or create categories
        military_category, _ = Category.objects.get_or_create(
            name='Military & Defense',
            defaults={'slug': 'military-defense', 'description': 'Military-grade autonomous systems'}
        )
        consumer_category, _ = Category.objects.get_or_create(
            name='Consumer',
            defaults={'slug': 'consumer', 'description': 'Consumer-grade robots'}
        )
        industrial_category, _ = Category.objects.get_or_create(
            name='Industrial',
            defaults={'slug': 'industrial', 'description': 'Industrial automation robots'}
        )
        
        # Clear existing robots and products (optional - comment out if you want to keep existing)
        # Robot.objects.all().delete()
        # Product.objects.filter(robot__isnull=False).delete()
        
        robots_data = [
            # === HUMANOIDS (3) ===
            {
                'title': 'Atlas Advanced Humanoid Robot',
                'description': 'Next-generation humanoid robot designed for complex industrial and research applications. Features advanced bipedal locomotion, dexterous manipulation, and human-like agility.',
                'short_description': 'Advanced humanoid robot with bipedal locomotion',
                'price': Decimal('450000.00'),
                'category': industrial_category,
                'robot_type': 'humanoid',
                'manufacturer': 'Boston Dynamics',
                'model_number': 'Atlas-Pro-2025',
                'year_manufactured': 2025,
                'weight_kg': 89,
                'dimensions_length': 150,
                'dimensions_width': 75,
                'dimensions_height': 150,
                'specs': {
                    'cpu_model': 'Intel Xeon W-2295 (18-core)',
                    'cpu_cores': 18,
                    'ram_gb': 64,
                    'storage_gb': 2048,
                    'gpu_model': 'NVIDIA RTX 6000 Ada',
                    'camera_resolution': '4K UHD (3840x2160)',
                    'camera_count': 6,
                    'lidar_enabled': True,
                    'radar_enabled': True,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'wifi_standard': 'WiFi 6E',
                    'bluetooth_version': '5.3',
                    'operating_system': 'ROS 2 Humble',
                    'motor_count': 28,
                    'motor_type': 'Brushless DC Servo',
                },
                'ai_system': {
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_speech_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'GPT-4 Vision Integration',
                    'model_version': '4.0',
                    'model_framework': 'PyTorch',
                    'accuracy_percentage': 95,
                },
                'power_system': {
                    'battery_type': 'lithium_polymer',
                    'battery_capacity_mah': 50000,
                    'battery_voltage_v': 48,
                    'operating_time_minutes': 120,
                    'charging_time_minutes': 90,
                },
                'usage_restriction': {
                    'restriction_level': 'commercial',
                    'requires_verification': False,
                }
            },
            {
                'title': 'H1 Humanoid Service Robot',
                'description': 'Professional service humanoid robot designed for hospitality, healthcare, and customer service applications. Features natural language processing and emotion recognition.',
                'short_description': 'Service humanoid for hospitality and healthcare',
                'price': Decimal('125000.00'),
                'category': consumer_category,
                'robot_type': 'humanoid',
                'manufacturer': 'UBTech Robotics',
                'model_number': 'H1-Pro-2025',
                'year_manufactured': 2025,
                'weight_kg': 55,
                'dimensions_length': 130,
                'dimensions_width': 60,
                'dimensions_height': 165,
                'specs': {
                    'cpu_model': 'Snapdragon 8 Gen 3',
                    'cpu_cores': 8,
                    'ram_gb': 32,
                    'storage_gb': 512,
                    'gpu_model': 'Adreno 750',
                    'camera_resolution': '1080p Full HD',
                    'camera_count': 4,
                    'lidar_enabled': False,
                    'radar_enabled': False,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'wifi_standard': 'WiFi 6',
                    'bluetooth_version': '5.2',
                    'operating_system': 'Android 14',
                    'motor_count': 17,
                    'motor_type': 'Servo Motor',
                },
                'ai_system': {
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_speech_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'BERT Language Model',
                    'model_version': '2.0',
                    'model_framework': 'TensorFlow',
                    'accuracy_percentage': 88,
                },
                'power_system': {
                    'battery_type': 'lithium_ion',
                    'battery_capacity_mah': 20000,
                    'battery_voltage_v': Decimal('24.00'),
                    'operating_time_minutes': 480,
                    'charging_time_minutes': 120,
                },
                'usage_restriction': {
                    'restriction_level': 'commercial',
                    'requires_verification': False,
                }
            },
            {
                'title': 'Ameca Humanoid Research Platform',
                'description': 'State-of-the-art humanoid research platform with advanced facial expressions and gestures. Designed for human-robot interaction research and entertainment applications.',
                'short_description': 'Research humanoid with advanced expressions',
                'price': Decimal('275000.00'),
                'category': industrial_category,
                'robot_type': 'humanoid',
                'manufacturer': 'Engineered Arts',
                'model_number': 'Ameca-Pro-Research',
                'year_manufactured': 2024,
                'weight_kg': 49,
                'dimensions_length': 120,
                'dimensions_width': 55,
                'dimensions_height': 170,
                'specs': {
                    'cpu_model': 'AMD Ryzen 9 7950X',
                    'cpu_cores': 16,
                    'ram_gb': 64,
                    'storage_gb': 1024,
                    'gpu_model': 'NVIDIA RTX 4090',
                    'camera_resolution': '4K UHD',
                    'camera_count': 2,
                    'lidar_enabled': False,
                    'radar_enabled': False,
                    'gps_enabled': False,
                    'imu_enabled': True,
                    'wifi_standard': 'WiFi 6',
                    'bluetooth_version': '5.1',
                    'operating_system': 'Ubuntu 22.04 LTS',
                    'motor_count': 52,
                    'motor_type': 'Linear Actuator',
                },
                'ai_system': {
                    'has_autonomous_navigation': False,
                    'has_object_recognition': True,
                    'has_speech_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'Custom Expression Engine',
                    'model_version': '3.2',
                    'model_framework': 'PyTorch',
                    'accuracy_percentage': 92,
                },
                'power_system': {
                    'battery_type': 'lithium_polymer',
                    'battery_capacity_mah': 30000,
                    'battery_voltage_v': Decimal('36.00'),
                    'operating_time_minutes': 180,
                    'charging_time_minutes': 150,
                },
                'usage_restriction': {
                    'restriction_level': 'commercial',
                    'requires_verification': False,
                }
            },
            
            # === DRONES (2) ===
            {
                'title': 'DJI Matrice 350 RTK Enterprise Drone',
                'description': 'Professional enterprise drone with RTK precision positioning, 45-minute flight time, and advanced obstacle avoidance. Ideal for surveying, inspection, and mapping applications.',
                'short_description': 'Enterprise drone with RTK positioning',
                'price': Decimal('25000.00'),
                'category': industrial_category,
                'robot_type': 'drone',
                'manufacturer': 'DJI',
                'model_number': 'M350-RTK-Pro',
                'year_manufactured': 2024,
                'weight_kg': 9.2,
                'dimensions_length': 81,
                'dimensions_width': 81,
                'dimensions_height': 42,
                'max_speed_kmh': 82,
                'max_altitude_m': 7000,
                'max_payload_kg': 2.7,
                'specs': {
                    'cpu_model': 'Dual IMU/GNSS',
                    'cpu_cores': 2,
                    'ram_gb': 8,
                    'storage_gb': 64,
                    'camera_resolution': '6K (6248x4168)',
                    'camera_count': 1,
                    'lidar_enabled': False,
                    'radar_enabled': True,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'wifi_standard': 'WiFi 6',
                    'bluetooth_version': '5.0',
                    'operating_system': 'DJI Flight OS',
                    'motor_count': 4,
                    'motor_type': 'Brushless DC',
                },
                'ai_system': {
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_speech_recognition': False,
                    'has_decision_making': True,
                    'model_name': 'DJI Flight Autopilot',
                    'model_version': '2.5',
                    'model_framework': 'Custom',
                    'accuracy_percentage': 99,
                },
                'power_system': {
                    'battery_type': 'lithium_polymer',
                    'battery_capacity_mah': 6000,
                    'battery_voltage_v': Decimal('52.22'),
                    'battery_cells': 6,
                    'operating_time_minutes': 45,
                    'charging_time_minutes': 90,
                },
                'usage_restriction': {
                    'restriction_level': 'commercial',
                    'requires_verification': False,
                }
            },
            {
                'title': 'Autel EVO Lite+ Professional Drone',
                'description': 'High-performance professional drone with 6K video recording, 40-minute flight time, and advanced AI-powered flight modes. Perfect for cinematography and professional photography.',
                'short_description': 'Professional cinematography drone',
                'price': Decimal('18000.00'),
                'category': consumer_category,
                'robot_type': 'drone',
                'manufacturer': 'Autel Robotics',
                'model_number': 'EVO-Lite-Plus-Pro',
                'year_manufactured': 2024,
                'weight_kg': 0.835,
                'dimensions_length': 21.6,
                'dimensions_width': 17.2,
                'dimensions_height': 8.2,
                'max_speed_kmh': 72,
                'max_altitude_m': 8000,
                'specs': {
                    'cpu_model': 'Quad-core ARM Cortex-A78',
                    'cpu_cores': 4,
                    'ram_gb': 8,
                    'storage_gb': 128,
                    'camera_resolution': '6K (5472x3648)',
                    'camera_count': 1,
                    'lidar_enabled': False,
                    'radar_enabled': True,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'wifi_standard': 'WiFi 6',
                    'bluetooth_version': '5.1',
                    'operating_system': 'Autel Flight OS',
                    'motor_count': 4,
                    'motor_type': 'Brushless DC',
                },
                'ai_system': {
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_speech_recognition': False,
                    'has_decision_making': True,
                    'model_name': 'Autel AI Flight System',
                    'model_version': '3.0',
                    'model_framework': 'TensorFlow Lite',
                    'accuracy_percentage': 94,
                },
                'power_system': {
                    'battery_type': 'lithium_polymer',
                    'battery_capacity_mah': 7100,
                    'battery_voltage_v': Decimal('11.40'),
                    'battery_cells': 3,
                    'operating_time_minutes': 40,
                    'charging_time_minutes': 75,
                },
                'usage_restriction': {
                    'restriction_level': 'commercial',
                    'requires_verification': False,
                }
            },
            
            # === MILITARY WAR MACHINES (3) ===
            {
                'title': 'SWORD Ground Combat Unit',
                'description': 'Autonomous ground combat unit equipped with advanced AI targeting systems, modular weapon platforms, and stealth capabilities. Designed for tactical operations and perimeter defense.',
                'short_description': 'Autonomous ground combat unit',
                'price': Decimal('2500000.00'),
                'category': military_category,
                'robot_type': 'military',
                'manufacturer': 'Defense Systems International',
                'model_number': 'SWORD-GCU-2025',
                'year_manufactured': 2025,
                'weight_kg': 450,
                'dimensions_length': 280,
                'dimensions_width': 180,
                'dimensions_height': 150,
                'max_speed_kmh': 65,
                'max_payload_kg': 500,
                'operating_temperature_min': -40,
                'operating_temperature_max': 55,
                'specs': {
                    'cpu_model': 'Dual Xeon Platinum 8480',
                    'cpu_cores': 112,
                    'ram_gb': 512,
                    'storage_gb': 8192,
                    'gpu_model': 'NVIDIA A100 (x4)',
                    'camera_resolution': '8K UHD (7680x4320)',
                    'camera_count': 12,
                    'lidar_enabled': True,
                    'radar_enabled': True,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'sensor_list': ['Thermal Imaging', 'Night Vision', 'Acoustic Sensors', 'Chemical Detection'],
                    'wifi_standard': 'Military Secure WiFi',
                    'bluetooth_version': '5.3',
                    'cellular_support': True,
                    'communication_protocols': ['Tactical Radio', 'Satellite Link', 'Encrypted Mesh'],
                    'operating_system': 'Military Linux (Hardened)',
                    'firmware_version': '2.8.1-SECURE',
                    'motor_count': 6,
                    'motor_type': 'High-Torque Servo',
                },
                'ai_system': {
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_speech_recognition': True,
                    'has_decision_making': True,
                    'ai_types': ['Deep Learning', 'Reinforcement Learning', 'Computer Vision'],
                    'model_name': 'Tactical AI Core v4',
                    'model_version': '4.2',
                    'model_framework': 'PyTorch (Hardened)',
                    'training_data_size': '500TB',
                    'inference_speed_ms': 15,
                    'accuracy_percentage': 99.7,
                    'edge_inference': True,
                    'safety_constraints': ['ROE Compliance', 'Civilian Protection', 'IFF Systems'],
                },
                'power_system': {
                    'battery_type': 'lithium_polymer',
                    'battery_capacity_mah': 200000,
                    'battery_voltage_v': Decimal('96.00'),
                    'battery_cells': 24,
                    'operating_time_minutes': 1440,
                    'charging_time_minutes': 180,
                    'charging_method': 'Rapid Charge Station',
                    'has_fast_charging': True,
                    'operating_power_w': Decimal('5000.00'),
                    'peak_power_w': Decimal('15000.00'),
                    'has_power_saving_mode': True,
                    'backup_battery': True,
                },
                'usage_restriction': {
                    'restriction_level': 'military_only',
                    'requires_verification': True,
                    'export_control_classification': 'ITAR Controlled',
                    'requires_export_license': True,
                    'dual_use': False,
                    'legal_notices': 'Restricted to authorized military personnel only. Export restricted.',
                }
            },
            {
                'title': 'SKYHAWK Autonomous Combat Drone',
                'description': 'High-altitude autonomous combat drone with stealth capabilities, advanced AI targeting, and multi-weapon platform support. Designed for reconnaissance and precision strikes.',
                'short_description': 'Autonomous combat drone with stealth',
                'price': Decimal('8500000.00'),
                'category': military_category,
                'robot_type': 'military',
                'manufacturer': 'AeroDefense Systems',
                'model_number': 'SKYHAWK-ACD-2025',
                'year_manufactured': 2025,
                'weight_kg': 1850,
                'dimensions_length': 1200,
                'dimensions_width': 850,
                'dimensions_height': 180,
                'max_speed_kmh': 850,
                'max_altitude_m': 18000,
                'max_payload_kg': 2000,
                'operating_temperature_min': -55,
                'operating_temperature_max': 60,
                'specs': {
                    'cpu_model': 'Quad Xeon Platinum',
                    'cpu_cores': 224,
                    'ram_gb': 1024,
                    'storage_gb': 16384,
                    'gpu_model': 'NVIDIA H100 (x8)',
                    'camera_resolution': '12K (12288x6912)',
                    'camera_count': 8,
                    'lidar_enabled': True,
                    'radar_enabled': True,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'sensor_list': ['Synthetic Aperture Radar', 'EO/IR Sensors', 'Electronic Warfare Suite'],
                    'communication_protocols': ['Satellite Link', 'Tactical Data Link', 'Encrypted RF'],
                    'operating_system': 'Military Real-Time OS',
                    'motor_count': 4,
                    'motor_type': 'Jet Turbine',
                },
                'ai_system': {
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_speech_recognition': False,
                    'has_decision_making': True,
                    'ai_types': ['Deep Learning', 'Swarm Intelligence', 'Predictive AI'],
                    'model_name': 'Combat AI System v5',
                    'model_version': '5.1',
                    'model_framework': 'Custom Military Framework',
                    'training_data_size': '2PB',
                    'inference_speed_ms': 8,
                    'accuracy_percentage': 99.9,
                    'edge_inference': True,
                    'safety_constraints': ['Rules of Engagement', 'Target Identification', 'Collateral Damage Assessment'],
                },
                'power_system': {
                    'battery_type': 'fuel_cell',
                    'battery_capacity_mah': None,  # Fuel cell - no capacity
                    'battery_voltage_v': 380,
                    'operating_time_minutes': 4320,
                    'charging_time_minutes': 120,
                    'charging_method': 'Refueling',
                    'operating_power_w': 15000,
                    'peak_power_w': 50000,
                },
                'usage_restriction': {
                    'restriction_level': 'military_only',
                    'requires_verification': True,
                    'export_control_classification': 'ITAR/EAR Restricted',
                    'requires_export_license': True,
                    'dual_use': False,
                    'legal_notices': 'CLASSIFIED - Restricted to authorized military use only. Export strictly prohibited.',
                }
            },
            {
                'title': 'GUARDIAN Perimeter Defense System',
                'description': 'Autonomous perimeter defense system with AI-powered threat detection, automated response capabilities, and integrated counter-measure systems. Designed for base security and critical infrastructure protection.',
                'short_description': 'Autonomous perimeter defense system',
                'price': Decimal('3200000.00'),
                'category': military_category,
                'robot_type': 'military',
                'manufacturer': 'SecureDefense Technologies',
                'model_number': 'GUARDIAN-PDS-2025',
                'year_manufactured': 2025,
                'weight_kg': 780,
                'dimensions_length': 350,
                'dimensions_width': 250,
                'dimensions_height': 220,
                'max_speed_kmh': 45,
                'max_payload_kg': 800,
                'operating_temperature_min': -30,
                'operating_temperature_max': 50,
                'specs': {
                    'cpu_model': 'Dual Xeon Gold 6438',
                    'cpu_cores': 64,
                    'ram_gb': 256,
                    'storage_gb': 4096,
                    'gpu_model': 'NVIDIA RTX 6000 Ada (x2)',
                    'camera_resolution': '8K UHD',
                    'camera_count': 16,
                    'lidar_enabled': True,
                    'radar_enabled': True,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'sensor_list': ['Motion Detection', 'Thermal Imaging', 'Acoustic Sensors', 'Magnetic Sensors'],
                    'communication_protocols': ['Secure Mesh Network', 'Satellite Backup', 'Encrypted Radio'],
                    'operating_system': 'Hardened Linux',
                    'motor_count': 8,
                    'motor_type': 'All-Wheel Drive Servo',
                },
                'ai_system': {
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_speech_recognition': True,
                    'has_decision_making': True,
                    'ai_types': ['Deep Learning', 'Behavioral Analysis', 'Anomaly Detection'],
                    'model_name': 'Defense AI Core v3',
                    'model_version': '3.8',
                    'model_framework': 'PyTorch',
                    'training_data_size': '200TB',
                    'inference_speed_ms': 20,
                    'accuracy_percentage': 98.5,
                    'edge_inference': True,
                    'safety_constraints': ['Non-Lethal First', 'Threat Assessment', 'Human Oversight'],
                },
                'power_system': {
                    'battery_type': 'lithium_polymer',
                    'battery_capacity_mah': 150000,
                    'battery_voltage_v': Decimal('72.00'),
                    'battery_cells': 18,
                    'operating_time_minutes': 2880,
                    'charging_time_minutes': 240,
                    'charging_method': 'Rapid Charge + Solar',
                    'has_fast_charging': True,
                    'supports_solar_charging': True,
                    'operating_power_w': Decimal('3500.00'),
                    'peak_power_w': Decimal('12000.00'),
                    'backup_battery': True,
                },
                'usage_restriction': {
                    'restriction_level': 'military_only',
                    'requires_verification': True,
                    'export_control_classification': 'ITAR Controlled',
                    'requires_export_license': True,
                    'dual_use': False,
                    'legal_notices': 'Restricted to authorized military and government use only.',
                }
            },
            
            # === OTHERS - Industrial/Service (2) ===
            {
                'title': 'KIVA Warehouse Automation Robot',
                'description': 'Advanced warehouse automation robot with AI-powered inventory management, autonomous navigation, and collaborative picking capabilities. Designed for e-commerce fulfillment and logistics.',
                'short_description': 'Warehouse automation robot',
                'price': Decimal('75000.00'),
                'category': industrial_category,
                'robot_type': 'industrial',
                'manufacturer': 'Amazon Robotics',
                'model_number': 'KIVA-XL-2025',
                'year_manufactured': 2025,
                'weight_kg': 145,
                'dimensions_length': 76,
                'dimensions_width': 64,
                'dimensions_height': 41,
                'max_speed_kmh': 13,
                'max_payload_kg': 340,
                'specs': {
                    'cpu_model': 'Intel Core i7-13700',
                    'cpu_cores': 16,
                    'ram_gb': 32,
                    'storage_gb': 512,
                    'camera_resolution': '1080p Full HD',
                    'camera_count': 4,
                    'lidar_enabled': True,
                    'radar_enabled': False,
                    'gps_enabled': False,
                    'imu_enabled': True,
                    'wifi_standard': 'WiFi 6',
                    'bluetooth_version': '5.2',
                    'communication_protocols': ['MQTT', 'ROS 2'],
                    'operating_system': 'ROS 2 Humble',
                    'motor_count': 4,
                    'motor_type': 'Omni-directional Wheel',
                },
                'ai_system': {
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_speech_recognition': False,
                    'has_decision_making': True,
                    'model_name': 'Warehouse AI',
                    'model_version': '2.3',
                    'model_framework': 'TensorFlow',
                    'accuracy_percentage': 96,
                },
                'power_system': {
                    'battery_type': 'lithium_ion',
                    'battery_capacity_mah': 50000,
                    'battery_voltage_v': Decimal('48.00'),
                    'operating_time_minutes': 720,
                    'charging_time_minutes': 60,
                    'has_fast_charging': True,
                },
                'usage_restriction': {
                    'restriction_level': 'commercial',
                    'requires_verification': False,
                }
            },
            {
                'title': 'SpotMini Service & Inspection Robot',
                'description': 'Versatile quadruped robot designed for inspection, security, and service applications. Features advanced locomotion, manipulation capabilities, and rugged design for industrial environments.',
                'short_description': 'Quadruped inspection and service robot',
                'price': Decimal('95000.00'),
                'category': industrial_category,
                'robot_type': 'service',
                'manufacturer': 'Boston Dynamics',
                'model_number': 'SpotMini-Pro-2025',
                'year_manufactured': 2025,
                'weight_kg': 32,
                'dimensions_length': 84,
                'dimensions_width': 50,
                'dimensions_height': 84,
                'max_speed_kmh': 5.8,
                'max_payload_kg': 14,
                'specs': {
                    'cpu_model': 'Intel NUC Compute Element',
                    'cpu_cores': 8,
                    'ram_gb': 16,
                    'storage_gb': 256,
                    'camera_resolution': '4K UHD',
                    'camera_count': 5,
                    'lidar_enabled': True,
                    'radar_enabled': False,
                    'gps_enabled': True,
                    'imu_enabled': True,
                    'wifi_standard': 'WiFi 6',
                    'bluetooth_version': '5.1',
                    'operating_system': 'ROS 2',
                    'motor_count': 12,
                    'motor_type': 'High-Torque Servo',
                },
                'ai_system': {
                    'has_autonomous_navigation': True,
                    'has_object_recognition': True,
                    'has_speech_recognition': False,
                    'has_decision_making': True,
                    'model_name': 'Locomotion AI',
                    'model_version': '3.1',
                    'model_framework': 'PyTorch',
                    'accuracy_percentage': 97,
                },
                'power_system': {
                    'battery_type': 'lithium_ion',
                    'battery_capacity_mah': 18000,
                    'battery_voltage_v': Decimal('28.80'),
                    'operating_time_minutes': 90,
                    'charging_time_minutes': 60,
                },
                'usage_restriction': {
                    'restriction_level': 'commercial',
                    'requires_verification': False,
                }
            },
        ]
        
        created_count = 0
        for robot_data in robots_data:
            try:
                # Extract nested data
                specs_data = robot_data.pop('specs', {})
                ai_data = robot_data.pop('ai_system', {})
                power_data = robot_data.pop('power_system', {})
                restriction_data = robot_data.pop('usage_restriction', {})
                
                # Create product
                category = robot_data.pop('category')
                product = Product.objects.create(
                    seller=seller,
                    category=category,
                    title=robot_data.pop('title'),
                    description=robot_data.pop('description'),
                    short_description=robot_data.pop('short_description'),
                    price=robot_data.pop('price'),
                    status='published',
                    visibility=True,
                    stock_quantity=5,
                )
                
                # Create robot
                robot = Robot.objects.create(
                    product=product,
                    **robot_data
                )
                
                # Create specifications
                RobotSpecification.objects.create(
                    robot=robot,
                    **specs_data
                )
                
                # Create AI system details
                AISystemDetails.objects.create(
                    robot=robot,
                    **ai_data
                )
                
                # Create power system (ensure Decimal types for decimal fields)
                power_kwargs = {}
                decimal_fields = ['battery_voltage_v', 'operating_power_w', 'peak_power_w', 'idle_power_w']
                for k, v in power_data.items():
                    if v is not None:
                        if k in decimal_fields:
                            power_kwargs[k] = Decimal(str(v)) if not isinstance(v, Decimal) else v
                        else:
                            power_kwargs[k] = v
                
                PowerSystem.objects.create(
                    robot=robot,
                    **power_kwargs
                )
                
                # Create usage restriction
                UsageRestriction.objects.create(
                    robot=robot,
                    **restriction_data
                )
                
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {product.title}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating {robot_data.get("title", "robot")}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Successfully created {created_count} robots ==='))

