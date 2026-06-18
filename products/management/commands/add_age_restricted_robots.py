"""
Django management command to add age-restricted companion/humanoid robots.
These robots require age verification (18+) clearance.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from products.models import (
    Category, Product, Robot, RobotSpecification, AISystemDetails,
    PowerSystem, UsageRestriction
)
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Add age-restricted companion and humanoid robots with full specifications'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating age-restricted robots...'))
        
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
        
        # Get or create Age-Restricted category
        category, _ = Category.objects.get_or_create(
            slug='companion-robots',
            defaults={
                'name': 'Companion & Humanoid Robots',
                'description': 'Advanced humanoid companion robots and interactive partners. Age-restricted content (18+).',
                'is_active': True,
            }
        )
        
        # Age-restricted robot data
        age_restricted_robots = [
            {
                'product': {
                    'title': 'Eva-X9 Premium Companion Humanoid',
                    'short_description': 'Advanced humanoid companion robot with realistic AI personality and interactive features',
                    'description': '''The Eva-X9 Premium Companion Humanoid represents the cutting edge of human-robot interaction technology. Designed for companionship, conversation, and emotional connection, this advanced humanoid features sophisticated AI, realistic movements, and customizable personality traits.

**Key Features:**
- Advanced AI personality system with customizable traits
- Realistic human-like appearance and movements
- Natural conversation and emotional intelligence
- Sensory feedback and touch response systems
- Long-term memory and relationship building
- Personalized interaction patterns
- Voice recognition and natural language processing
- Emotional expression through facial features and body language

**Physical Specifications:**
- Lifelike human proportions and appearance
- Advanced synthetic skin technology
- Articulated joints for natural movement
- High-resolution expressive eyes with LED display
- Realistic hair and customizable appearance options
- Durable yet flexible construction materials

**AI Capabilities:**
- Deep learning personality system
- Context-aware conversation
- Emotional state recognition and response
- Adaptive behavior based on interaction history
- Multi-modal communication (speech, gestures, expressions)
- Learning preferences and routines

**Age Restriction:** 18+ Only
**Verification Required:** Age verification clearance needed
**Use Case:** Adult companionship, social interaction, emotional support''',
                    'price': Decimal('125000.00'),
                    'stock_quantity': 15,
                    'status': 'active',
                    'is_featured': True,
                },
                'robot': {
                    'robot_type': 'service_robot',
                    'model_number': 'EVA-X9-2024',
                    'manufacturer': 'Companion Robotics Inc.',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('58.00'),
                    'dimensions_length': Decimal('45.00'),
                    'dimensions_width': Decimal('35.00'),
                    'dimensions_height': Decimal('165.00'),
                    'requires_verification': True,
                    'is_restricted': True,
                },
                'specs': {
                    'cpu_model': 'NVIDIA Jetson AGX Orin',
                    'cpu_cores': 12,
                    'ram_gb': Decimal('32.00'),
                    'storage_gb': Decimal('512.00'),
                    'gpu_model': 'NVIDIA Ampere',
                    'camera_resolution': '4K',
                    'camera_count': 4,
                    'lidar_enabled': False,
                    'radar_enabled': False,
                    'gps_enabled': False,
                    'imu_enabled': True,
                    'sensor_list': ['Touch Sensors', 'Proximity Sensors', 'Temperature Sensors', 'Audio Array'],
                    'wifi_standard': 'WiFi 6',
                    'bluetooth_version': '5.2',
                    'cellular_support': False,
                    'servo_count': 32,
                    'motor_type': 'Precision servo with haptic feedback',
                    'operating_system': 'CompanionOS 3.0',
                    'sdk_available': False,
                    'firmware_version': 'X9-2024.1',
                },
                'ai_system': {
                    'ai_types': ['nlp', 'computer_vision', 'reinforcement_learning'],
                    'has_autonomous_navigation': False,
                    'has_object_recognition': True,
                    'has_speech_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'Eva-Personality-AI',
                    'model_version': '2.1.0',
                    'model_framework': 'PyTorch',
                    'training_data_size': '500GB',
                    'inference_speed_ms': 50,
                    'supports_online_learning': True,
                    'edge_inference': True,
                },
                'power': {
                    'battery_type': 'lithium_ion',
                    'battery_capacity_mah': 800000,  # ~8000Wh at ~10V
                    'battery_voltage_v': Decimal('10.00'),
                    'operating_time_minutes': 480,  # 8 hours
                    'charging_time_minutes': 180,  # 3 hours
                    'operating_power_w': Decimal('100.00'),
                    'peak_power_w': Decimal('200.00'),
                    'has_fast_charging': True,
                },
                'restrictions': {
                    'restriction_level': 'age_restricted',
                    'requires_verification': True,
                    'minimum_age': 18,
                    'commercial_use_allowed': False,
                    'personal_use_allowed': True,
                    'research_use_allowed': False,
                }
            },
            {
                'product': {
                    'title': 'Neo-Humanoid Partner System Pro',
                    'short_description': 'Premium humanoid partner robot with advanced AI and realistic interaction capabilities',
                    'description': '''The Neo-Humanoid Partner System Pro is designed for long-term companionship and interaction. Featuring state-of-the-art AI personality, natural conversation abilities, and customizable features to create a truly personalized companion experience.

**Advanced Features:**
- Sophisticated personality AI with emotional depth
- Natural language processing and conversation
- Physical interaction capabilities
- Customizable appearance and personality
- Long-term relationship memory system
- Adaptive behavior learning
- Multi-sensory feedback systems
- Privacy-focused local processing

**Design & Build:**
- Human-like proportions and aesthetics
- Premium materials and construction
- Expressive facial features with LED display
- Smooth, natural movements
- Durable and long-lasting design
- Easy maintenance and care

**AI & Interaction:**
- Emotional intelligence and empathy simulation
- Context-aware conversation
- Personality traits and quirks
- Learning and adaptation over time
- Natural communication patterns
- Respectful and appropriate interaction

**Privacy & Safety:**
- All data processed locally (optional cloud features)
- Secure communication protocols
- User data protection
- Ethical AI design principles
- Respectful interaction boundaries

**Age Restriction:** 18+ Only
**Verification Required:** Age verification clearance needed
**Intended Use:** Adult companionship and social interaction''',
                    'price': Decimal('189000.00'),
                    'stock_quantity': 10,
                    'status': 'active',
                    'is_featured': True,
                },
                'robot': {
                    'robot_type': 'service_robot',
                    'model_number': 'NEO-PRO-2024',
                    'manufacturer': 'Neo Robotics Solutions',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('62.00'),
                    'dimensions_length': Decimal('48.00'),
                    'dimensions_width': Decimal('38.00'),
                    'dimensions_height': Decimal('170.00'),
                    'requires_verification': True,
                    'is_restricted': True,
                },
                'specs': {
                    'cpu_model': 'Qualcomm Snapdragon 8cx Gen 3',
                    'cpu_cores': 8,
                    'ram_gb': Decimal('64.00'),
                    'storage_gb': Decimal('1000.00'),
                    'gpu_model': 'Adreno 690',
                    'camera_resolution': '8K',
                    'camera_count': 6,
                    'lidar_enabled': False,
                    'radar_enabled': False,
                    'gps_enabled': False,
                    'imu_enabled': True,
                    'sensor_list': ['Touch Sensors', 'Pressure Sensors', 'Temperature Sensors', 'Microphone Array', 'Proximity Sensors'],
                    'wifi_standard': 'WiFi 6E',
                    'bluetooth_version': '5.3',
                    'cellular_support': False,
                    'servo_count': 36,
                    'motor_type': 'High-precision servo with feedback',
                    'operating_system': 'NeoOS 4.0',
                    'sdk_available': False,
                    'firmware_version': 'PRO-2024.2',
                },
                'ai_system': {
                    'ai_types': ['nlp', 'computer_vision', 'reinforcement_learning', 'sensor_fusion'],
                    'has_autonomous_navigation': False,
                    'has_object_recognition': True,
                    'has_speech_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'Neo-Personality-Pro-AI',
                    'model_version': '3.0.0',
                    'model_framework': 'TensorFlow',
                    'training_data_size': '1TB',
                    'inference_speed_ms': 35,
                    'supports_online_learning': True,
                    'edge_inference': True,
                },
                'power': {
                    'battery_type': 'lithium_ion',
                    'battery_capacity_mah': 1000000,  # ~10000Wh at ~10V
                    'battery_voltage_v': Decimal('10.00'),
                    'operating_time_minutes': 600,  # 10 hours
                    'charging_time_minutes': 240,  # 4 hours
                    'operating_power_w': Decimal('120.00'),
                    'peak_power_w': Decimal('250.00'),
                    'has_fast_charging': True,
                },
                'restrictions': {
                    'restriction_level': 'age_restricted',
                    'requires_verification': True,
                    'minimum_age': 18,
                    'commercial_use_allowed': False,
                    'personal_use_allowed': True,
                    'research_use_allowed': False,
                }
            },
            {
                'product': {
                    'title': 'Luna-Interactive Companion Humanoid',
                    'short_description': 'Advanced interactive companion robot with emotional AI and natural interaction',
                    'description': '''The Luna-Interactive Companion Humanoid offers an advanced level of human-robot interaction through sophisticated AI, realistic appearance, and natural communication. Designed for meaningful companionship and social interaction.

**Core Features:**
- Advanced emotional AI system
- Natural conversation capabilities
- Realistic human-like appearance
- Customizable personality and traits
- Long-term memory system
- Adaptive learning behavior
- Natural movement and gestures
- Multi-modal communication

**Interaction Capabilities:**
- Voice-based conversation
- Facial expression recognition
- Gesture and body language
- Touch and proximity sensing
- Emotional state expression
- Context-aware responses
- Personalized interaction patterns

**Technical Excellence:**
- State-of-the-art AI processing
- High-quality materials and build
- Reliable and durable construction
- Privacy-focused design
- User-friendly interface
- Regular software updates

**Age Restriction:** 18+ Only
**Verification Required:** Age verification clearance needed
**Use Case:** Adult companionship, emotional support, social interaction''',
                    'price': Decimal('95000.00'),
                    'stock_quantity': 20,
                    'status': 'active',
                    'is_featured': False,
                },
                'robot': {
                    'robot_type': 'service_robot',
                    'model_number': 'LUNA-IC-2024',
                    'manufacturer': 'Luna Robotics',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('55.00'),
                    'dimensions_length': Decimal('43.00'),
                    'dimensions_width': Decimal('33.00'),
                    'dimensions_height': Decimal('162.00'),
                    'requires_verification': True,
                    'is_restricted': True,
                },
                'specs': {
                    'cpu_model': 'Intel Core i7-12700H',
                    'cpu_cores': 14,
                    'ram_gb': Decimal('32.00'),
                    'storage_gb': Decimal('512.00'),
                    'gpu_model': 'Intel Iris Xe',
                    'camera_resolution': '4K',
                    'camera_count': 4,
                    'lidar_enabled': False,
                    'radar_enabled': False,
                    'gps_enabled': False,
                    'imu_enabled': True,
                    'sensor_list': ['Touch Sensors', 'Temperature Sensors', 'Audio Array', 'Proximity Sensors'],
                    'wifi_standard': 'WiFi 6',
                    'bluetooth_version': '5.2',
                    'cellular_support': False,
                    'servo_count': 28,
                    'motor_type': 'Precision servo',
                    'operating_system': 'LunaOS 2.5',
                    'sdk_available': False,
                    'firmware_version': 'IC-2024.1',
                },
                'ai_system': {
                    'ai_types': ['nlp', 'computer_vision'],
                    'has_autonomous_navigation': False,
                    'has_object_recognition': True,
                    'has_speech_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'Luna-Companion-AI',
                    'model_version': '1.8.0',
                    'model_framework': 'PyTorch',
                    'training_data_size': '300GB',
                    'inference_speed_ms': 60,
                    'supports_online_learning': True,
                    'edge_inference': True,
                },
                'power': {
                    'battery_type': 'lithium_polymer',
                    'battery_capacity_mah': 750000,  # ~7500Wh at ~10V
                    'battery_voltage_v': Decimal('10.00'),
                    'operating_time_minutes': 480,  # 8 hours
                    'charging_time_minutes': 180,  # 3 hours
                    'operating_power_w': Decimal('90.00'),
                    'peak_power_w': Decimal('180.00'),
                    'has_fast_charging': True,
                },
                'restrictions': {
                    'restriction_level': 'age_restricted',
                    'requires_verification': True,
                    'minimum_age': 18,
                    'commercial_use_allowed': False,
                    'personal_use_allowed': True,
                    'research_use_allowed': False,
                }
            },
            {
                'product': {
                    'title': 'Aurora-Premium Humanoid Companion',
                    'short_description': 'Premium humanoid companion with advanced AI personality and interaction systems',
                    'description': '''The Aurora-Premium Humanoid Companion represents the pinnacle of companion robot technology, featuring cutting-edge AI, realistic appearance, and sophisticated interaction capabilities designed for meaningful long-term relationships.

**Premium Features:**
- Ultra-advanced AI personality with emotional depth
- Lifelike human appearance and movements
- Natural conversation and communication
- Deep learning relationship system
- Customizable personality traits
- Long-term memory and adaptation
- Expressive features and body language
- Multi-sensory interaction capabilities

**Design Excellence:**
- Premium materials and craftsmanship
- Realistic human proportions
- High-quality synthetic skin
- Articulated movements and gestures
- Expressive LED facial features
- Customizable appearance options
- Durable construction for longevity

**AI & Technology:**
- State-of-the-art neural networks
- Emotional intelligence simulation
- Context-aware interactions
- Learning and adaptation algorithms
- Privacy-focused local processing
- Regular AI updates and improvements
- Ethical AI design principles

**Interaction & Communication:**
- Natural language understanding
- Voice recognition and synthesis
- Facial expression analysis
- Gesture and posture recognition
- Touch and proximity feedback
- Emotional state expression
- Personalized communication style

**Age Restriction:** 18+ Only
**Verification Required:** Age verification clearance needed
**Intended Use:** Adult companionship and social interaction''',
                    'price': Decimal('225000.00'),
                    'stock_quantity': 8,
                    'status': 'active',
                    'is_featured': True,
                },
                'robot': {
                    'robot_type': 'service_robot',
                    'model_number': 'AURORA-PREM-2024',
                    'manufacturer': 'Aurora Advanced Robotics',
                    'year_manufactured': 2024,
                    'weight_kg': Decimal('60.00'),
                    'dimensions_length': Decimal('47.00'),
                    'dimensions_width': Decimal('37.00'),
                    'dimensions_height': Decimal('168.00'),
                    'requires_verification': True,
                    'is_restricted': True,
                },
                'specs': {
                    'cpu_model': 'Apple M2 Pro',
                    'cpu_cores': 12,
                    'ram_gb': Decimal('64.00'),
                    'storage_gb': Decimal('2000.00'),
                    'gpu_model': 'Apple M2 GPU (19-core)',
                    'camera_resolution': '8K',
                    'camera_count': 8,
                    'lidar_enabled': False,
                    'radar_enabled': False,
                    'gps_enabled': False,
                    'imu_enabled': True,
                    'sensor_list': ['Advanced Touch Sensors', 'Pressure Sensors', 'Temperature Sensors', 'Multi-microphone Array', 'Proximity Sensors', 'Haptic Feedback'],
                    'wifi_standard': 'WiFi 6E',
                    'bluetooth_version': '5.3',
                    'cellular_support': False,
                    'servo_count': 40,
                    'motor_type': 'Ultra-precision servo with haptic feedback',
                    'operating_system': 'AuroraOS 5.0',
                    'sdk_available': False,
                    'firmware_version': 'PREM-2024.1',
                },
                'ai_system': {
                    'ai_types': ['nlp', 'computer_vision', 'reinforcement_learning', 'sensor_fusion'],
                    'has_autonomous_navigation': False,
                    'has_object_recognition': True,
                    'has_speech_recognition': True,
                    'has_decision_making': True,
                    'model_name': 'Aurora-Premium-AI',
                    'model_version': '4.0.0',
                    'model_framework': 'PyTorch',
                    'training_data_size': '2TB',
                    'inference_speed_ms': 25,
                    'supports_online_learning': True,
                    'edge_inference': True,
                    'has_explainability': False,
                },
                'power': {
                    'battery_type': 'lithium_ion',
                    'battery_capacity_mah': 1200000,  # ~12000Wh at ~10V
                    'battery_voltage_v': Decimal('10.00'),
                    'operating_time_minutes': 720,  # 12 hours
                    'charging_time_minutes': 300,  # 5 hours
                    'operating_power_w': Decimal('150.00'),
                    'peak_power_w': Decimal('300.00'),
                    'has_fast_charging': True,
                },
                'restrictions': {
                    'restriction_level': 'age_restricted',
                    'requires_verification': True,
                    'minimum_age': 18,
                    'commercial_use_allowed': False,
                    'personal_use_allowed': True,
                    'research_use_allowed': False,
                }
            },
        ]
        
        created_count = 0
        
        for robot_data in age_restricted_robots:
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
                power_data = robot_data['power'].copy()
                # Remove any None values that might cause issues
                power_data = {k: v for k, v in power_data.items() if v is not None}
                PowerSystem.objects.create(
                    robot=robot,
                    **power_data
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
            self.style.SUCCESS(f'\nSuccessfully created {created_count} age-restricted robots')
        )
        self.stdout.write(
            self.style.WARNING('\nWARNING: All robots require age verification (18+) clearance')
        )







