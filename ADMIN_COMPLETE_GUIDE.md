# Complete Admin Dashboard Setup Guide - ARES Platform

## 🔐 Accessing Admin Panel

1. **Login URL:** http://127.0.0.1:8000/admin/
2. **Credentials:**
   - Email: `admin@admin.com`
   - Password: `admin1234`

---

## 📋 Table of Contents

1. [Setting Up Clearance Levels](#1-setting-up-clearance-levels)
2. [Creating Users](#2-creating-users)
3. [Creating Categories](#3-creating-categories)
4. [Creating Products](#4-creating-products)
5. [Creating Robots](#5-creating-robots)
6. [Setting Up Robot Specifications](#6-setting-up-robot-specifications)
7. [Setting Up AI System Details](#7-setting-up-ai-system-details)
8. [Setting Up Power Systems](#8-setting-up-power-systems)
9. [Setting Up Usage Restrictions](#9-setting-up-usage-restrictions)
10. [Managing Verification Requests](#10-managing-verification-requests)

---

## 1. Setting Up Clearance Levels

**Location:** Admin Panel → Verification → Clearance Levels

### Why First?
Clearance levels determine who can access which robots. Set these up BEFORE creating restricted robots.

### Steps to Create Clearance Level

1. Click **"Add Clearance Level"**
2. Fill in the fields:

#### Field Explanations:

- **Name** (Required)
  - Example: `Military Clearance`
  - What it means: Display name for the clearance level
  - Format: Any text (e.g., "Public", "Confidential", "Secret", "Top Secret", "Military")

- **Code** (Required, Unique)
  - Example: `military`
  - What it means: Internal code used in the system
  - Format: lowercase, no spaces (e.g., "public", "confidential", "secret", "top_secret", "military")
  - Important: Use lowercase and underscores

- **Description** (Optional)
  - Example: `Provides access to military-grade autonomous systems`
  - What it means: Brief explanation of what this clearance allows

- **Priority** (Required, Integer)
  - Example: `50`
  - What it means: Higher number = higher clearance level
  - Recommended values:
    - Public: `0`
    - Confidential: `10`
    - Secret: `30`
    - Top Secret: `50`
    - Military: `40`

- **Can Access Military** (Checkbox)
  - Check this if clearance allows access to military robots
  - Example: ✓ Check for "Military Clearance"

- **Can Access Export Controlled** (Checkbox)
  - Check if clearance allows export-controlled items
  - Example: ✓ Check for "Military Clearance" and "Top Secret"

- **Can Access Top Secret** (Checkbox)
  - Check if clearance allows top-secret items
  - Example: ✓ Check only for "Top Secret Clearance"

- **Can Access Restricted** (Checkbox)
  - Check if clearance allows any restricted items
  - Example: ✓ Check for all clearance levels except "Public"

- **Validity Period Days** (Integer)
  - Example: `365`
  - What it means: How many days the clearance is valid
  - Recommended: `365` (1 year) or `730` (2 years)

- **Renewal Notice Days** (Integer)
  - Example: `30`
  - What it means: Days before expiry to send renewal reminder
  - Recommended: `30` days

- **Requires Background Check** (Checkbox)
  - Check if this clearance requires background verification
  - Example: ✓ Check for "Military" and "Top Secret"

- **Is Active** (Checkbox)
  - Always check ✓ (uncheck to disable without deleting)

### Example Clearance Levels to Create:

1. **Public Trust**
   - Name: `Public Trust`
   - Code: `public`
   - Priority: `0`
   - Can Access Restricted: ✗ (leave unchecked)
   - Validity: `365` days

2. **Military Clearance**
   - Name: `Military Clearance`
   - Code: `military`
   - Priority: `40`
   - Can Access Military: ✓
   - Can Access Export Controlled: ✓
   - Can Access Restricted: ✓
   - Validity: `365` days
   - Requires Background Check: ✓

3. **Top Secret**
   - Name: `Top Secret Clearance`
   - Code: `top_secret`
   - Priority: `50`
   - Can Access Top Secret: ✓
   - Can Access Export Controlled: ✓
   - Can Access Restricted: ✓
   - Validity: `180` days
   - Requires Background Check: ✓

---

## 2. Creating Users

**Location:** Admin Panel → Users → Users (Custom Users)

### Steps to Create User

1. Click **"Add User"**
2. Fill in the fields:

#### Required Fields:

- **Email Address** (Required, Unique)
  - Example: `john.doe@example.com`
  - What it means: User's email (used for login)
  - Format: Valid email address

- **Username** (Required, Unique)
  - Example: `johndoe`
  - What it means: Unique username for the user
  - Format: Letters, numbers, underscores (no spaces)

- **Password** (Required)
  - Click "Change password" link
  - Enter password twice
  - Example: `SecurePass123!`
  - What it means: User's login password
  - Minimum: 8 characters recommended

#### Important Optional Fields:

- **First Name**
  - Example: `John`

- **Last Name**
  - Example: `Doe`

- **Role** (Dropdown)
  - Select from: Guest, Client, Buyer, Seller, Moderator, Support Staff, etc.
  - Example: `Buyer` for regular customers, `Seller` for vendors

- **Is Active** (Checkbox)
  - ✓ Check to allow user to login
  - ✗ Uncheck to disable account

- **Is Verified** (Checkbox)
  - ✓ Check if user email is verified
  - Recommended: Check for legitimate users

- **Is Seller Approved** (Checkbox)
  - ✓ Check if user can sell products
  - Only check for sellers

- **Is Staff** (Checkbox)
  - ✓ Check to give admin panel access
  - Only for administrators

- **Is Superuser** (Checkbox)
  - ✓ Check for full admin access
  - Use sparingly

#### Example User Types:

**Regular Buyer:**
- Email: `buyer@example.com`
- Username: `buyer1`
- Role: `Buyer`
- Is Active: ✓
- Is Verified: ✓

**Seller:**
- Email: `seller@example.com`
- Username: `seller1`
- Role: `Seller`
- Is Active: ✓
- Is Verified: ✓
- Is Seller Approved: ✓

**Admin User:**
- Email: `admin2@example.com`
- Username: `admin2`
- Role: `System Admin`
- Is Active: ✓
- Is Staff: ✓
- Is Superuser: ✓

---

## 3. Creating Categories

**Location:** Admin Panel → Products → Categories

### Steps to Create Category

1. Click **"Add Category"**
2. Fill in the fields:

#### Field Explanations:

- **Name** (Required)
  - Example: `Consumer Drones`
  - What it means: Category name displayed to users

- **Slug** (Auto-generated, but editable)
  - Example: `consumer-drones` (auto from name)
  - What it means: URL-friendly version of name
  - Format: lowercase, hyphens instead of spaces

- **Description** (Optional)
  - Example: `Consumer-grade drones for personal and commercial use`
  - What it means: Category description

- **Parent** (Optional, Dropdown)
  - Select parent category if this is a subcategory
  - Example: If creating "Quadcopters", parent could be "Consumer Drones"
  - Leave empty for top-level categories

- **Order** (Integer)
  - Example: `1`
  - What it means: Display order (lower numbers appear first)
  - Recommended: `1`, `2`, `3`, etc.

- **Is Active** (Checkbox)
  - ✓ Check to show category
  - ✗ Uncheck to hide

- **Is Featured** (Checkbox)
  - ✓ Check to highlight on homepage
  - Use for popular categories

#### Example Categories to Create:

1. **Consumer Drones**
   - Name: `Consumer Drones`
   - Slug: `consumer-drones`
   - Order: `1`
   - Is Active: ✓
   - Is Featured: ✓

2. **Military-Grade Robots**
   - Name: `Military-Grade Robots`
   - Slug: `military-grade-robots`
   - Order: `2`
   - Is Active: ✓
   - Is Featured: ✓

3. **Autonomous Systems**
   - Name: `Autonomous Systems`
   - Slug: `autonomous-systems`
   - Order: `3`
   - Is Active: ✓

---

## 4. Creating Products

**Location:** Admin Panel → Products → Products

### Steps to Create Product

1. Click **"Add Product"**
2. Fill in the fields:

#### Critical Fields (Required):

- **Seller** (Required, Dropdown)
  - **DO NOT TYPE - USE DROPDOWN!**
  - Click dropdown and select a user
  - Example: Select "admin (admin@admin.com)"
  - What it means: Who is selling this product

- **Title** (Required)
  - Example: `ARES-X1 Military Drone`
  - What it means: Product name shown to customers

- **Slug** (Auto-generated)
  - Example: `ares-x1-military-drone` (auto from title)
  - What it means: URL-friendly version
  - Format: lowercase, hyphens

- **Description** (Required)
  - Example: `Advanced military-grade autonomous drone with AI navigation, high-altitude capabilities, and encrypted communication systems. Designed for surveillance and reconnaissance missions.`
  - What it means: Detailed product description
  - Format: Full paragraph, multiple sentences

- **Price** (Required, Decimal)
  - Example: `49999.99`
  - What it means: Product price in dollars
  - Format: Decimal number (e.g., `99.99`, `50000.00`)

- **Currency** (Dropdown)
  - Default: `USD`
  - What it means: Price currency

- **Status** (Required, Dropdown)
  - Options: Draft, Pending Review, Active, Paused, Out of Stock, Discontinued, Banned
  - For live products: Select `Active`
  - For testing: Select `Draft`

- **Category** (Required, Dropdown)
  - Select the category you created
  - Example: Select "Military-Grade Robots"

#### Important Optional Fields:

- **Short Description**
  - Example: `Military-grade autonomous drone with AI capabilities`
  - What it means: Brief summary (shown in listings)
  - Format: One sentence, ~150 characters

- **Compare at Price**
  - Example: `59999.99`
  - What it means: Original price (for showing discounts)
  - Leave empty if no discount

- **Stock Quantity**
  - Example: `10`
  - What it means: Available inventory count
  - Use `0` for out of stock

- **Track Inventory** (Checkbox)
  - ✓ Check to enable stock tracking
  - Recommended: Check for physical products

- **Is Featured** (Checkbox)
  - ✓ Check to highlight on homepage

- **Is Bestseller** (Checkbox)
  - ✓ Check for popular products

- **Visibility** (Dropdown)
  - Options: Public, Unlisted, Hidden
  - Default: `Public` (everyone can see)
  - `Unlisted`: Only via direct link
  - `Hidden`: Admin only

- **Shipping Type** (Dropdown)
  - Options: Digital Delivery, Physical Shipping, Digital & Physical
  - For robots: Select `Physical Shipping`
  - For software: Select `Digital Delivery`

- **Weight** (Decimal)
  - Example: `15.5`
  - What it means: Product weight in kg

- **Weight Unit** (Dropdown)
  - Default: `kg`
  - Options: kg, lbs

#### UUID Field:
- **LEAVE BLANK** - Auto-generated when you save!

### Example Products:

**Product 1: Consumer Drone**
- Seller: Select a seller user
- Title: `SkyFlyer Pro 4K`
- Description: `Professional 4K camera drone with GPS navigation and 30-minute flight time. Perfect for aerial photography and videography.`
- Price: `1299.99`
- Status: `Active`
- Category: `Consumer Drones`
- Stock Quantity: `25`
- Track Inventory: ✓

**Product 2: Military Robot**
- Seller: Select a seller user
- Title: `ARES-X1 Tactical Autonomous System`
- Description: `Advanced military-grade autonomous system designed for tactical operations. Features AI-powered navigation, encrypted communication, and modular payload system. Certified for military use.`
- Price: `125000.00`
- Status: `Active`
- Category: `Military-Grade Robots`
- Stock Quantity: `5`
- Track Inventory: ✓
- Is Featured: ✓

---

## 5. Creating Robots

**Location:** Admin Panel → Products → Robots

**IMPORTANT:** Create the Product FIRST, then create the Robot and link it to that product.

### Steps to Create Robot

1. Click **"Add Robot"**
2. Fill in the fields:

#### Required Fields:

- **Product** (Required, Dropdown/Magnifying Glass)
  - Click the magnifying glass 🔍 next to the field
  - Search for and select the product you created
  - Example: Select "ARES-X1 Tactical Autonomous System"
  - What it means: Links robot to a product

- **Robot Type** (Required, Dropdown)
  - Options:
    - `consumer_drone` - Consumer drones
    - `commercial_drone` - Commercial/Business drones
    - `military_autonomous` - Military autonomous systems
    - `industrial_robot` - Industrial robots
    - `service_robot` - Service robots
    - `humanoid_robot` - Humanoid robots
  - Example: For military robots, select `military_autonomous`
  - What it means: Category of robot

- **Manufacturer** (Required)
  - Example: `ARES Defense Systems`
  - What it means: Company that made the robot

- **Model Number** (Required)
  - Example: `ARES-X1-2024`
  - What it means: Model identifier
  - Format: Alphanumeric with hyphens

#### Physical Specifications:

- **Weight (kg)** (Decimal)
  - Example: `25.5`
  - What it means: Robot weight in kilograms

- **Dimensions Length (cm)** (Decimal)
  - Example: `120.0`
  - What it means: Length in centimeters

- **Dimensions Width (cm)** (Decimal)
  - Example: `80.0`

- **Dimensions Height (cm)** (Decimal)
  - Example: `45.0`

#### Capabilities:

- **Max Speed (km/h)** (Decimal)
  - Example: `150.0`
  - What it means: Maximum speed in kilometers per hour

- **Max Altitude (m)** (Decimal)
  - Example: `5000.0`
  - What it means: Maximum altitude in meters
  - For ground robots: `0` or leave empty

- **Max Payload (kg)** (Decimal)
  - Example: `10.5`
  - What it means: Maximum weight robot can carry

- **Operating Temperature Min (°C)** (Integer)
  - Example: `-20`
  - What it means: Minimum operating temperature

- **Operating Temperature Max (°C)** (Integer)
  - Example: `50`
  - What it means: Maximum operating temperature

#### Restrictions & Security:

- **Requires Verification** (Checkbox)
  - ✓ Check if robot needs user verification to purchase
  - Example: ✓ Check for military robots

- **Is Restricted** (Checkbox)
  - ✓ Check for restricted/controlled items
  - Example: ✓ Check for military robots
  - What it means: Only users with appropriate clearance can access

#### Certifications:

- **Certifications** (Text Field)
  - Example: `FAA Part 107, ISO 9001, MIL-STD-461`
  - What it means: Compliance certifications
  - Format: Comma-separated list

- **Compliance Standards** (Text Field)
  - Example: `MIL-STD-810G, DO-178C`
  - What it means: Standards the robot meets

- **Serial Number Format** (Text)
  - Example: `ARES-XXXX-YYYY`
  - What it means: Format for serial numbers

#### UUID Field:
- **LEAVE BLANK** - Auto-generated!

### Example Robots:

**Robot 1: Consumer Drone**
- Product: Select "SkyFlyer Pro 4K"
- Robot Type: `consumer_drone`
- Manufacturer: `SkyTech Industries`
- Model Number: `SF-PRO-4K-2024`
- Weight: `1.2` kg
- Dimensions: Length `45`, Width `35`, Height `15` cm
- Max Speed: `60` km/h
- Max Altitude: `500` m
- Max Payload: `0.5` kg
- Requires Verification: ✗ (unchecked)
- Is Restricted: ✗ (unchecked)

**Robot 2: Military Robot**
- Product: Select "ARES-X1 Tactical Autonomous System"
- Robot Type: `military_autonomous`
- Manufacturer: `ARES Defense Systems`
- Model Number: `ARES-X1-2024`
- Weight: `25.5` kg
- Dimensions: Length `120`, Width `80`, Height `45` cm
- Max Speed: `150` km/h
- Max Altitude: `5000` m
- Max Payload: `10.5` kg
- Operating Temp: Min `-20`, Max `50` °C
- Certifications: `MIL-STD-810G, DO-178C, FAA Part 107`
- Requires Verification: ✓ (checked)
- Is Restricted: ✓ (checked)

---

## 6. Setting Up Robot Specifications

**Location:** Admin Panel → Products → Robot Specifications

**Note:** This can be added as an inline when editing the Robot, OR created separately.

### Steps to Create Specification

1. Click **"Add Robot Specification"**
2. Fill in:

- **Robot** (Required)
  - Select the robot you created

- **CPU/Processor** (Text)
  - Example: `ARM Cortex-A78, 8-core, 2.84GHz`
  - What it means: Processing unit details

- **RAM** (Text)
  - Example: `16GB LPDDR5`
  - What it means: Memory specifications

- **Storage** (Text)
  - Example: `512GB NVMe SSD`
  - What it means: Storage capacity and type

- **GPU** (Text, Optional)
  - Example: `NVIDIA Jetson AGX Orin`
  - What it means: Graphics/AI processing unit

- **Sensors** (Text)
  - Example: `LiDAR, RGB Camera, Thermal Camera, IMU, GPS, Altimeter`
  - What it means: List of sensors
  - Format: Comma-separated

- **Communication** (Text)
  - Example: `WiFi 6, 4G/5G, Satellite Link, Encrypted Radio`
  - What it means: Communication capabilities

- **Operating System** (Text)
  - Example: `ROS 2 (Robot Operating System)`
  - What it means: Software platform

---

## 7. Setting Up AI System Details

**Location:** Admin Panel → Products → AI System Details

### Steps to Create AI Details

1. Click **"Add AI System Detail"**
2. Fill in:

- **Robot** (Required)
  - Select the robot

- **AI Model** (Text)
  - Example: `Custom CNN for Navigation, YOLO v8 for Object Detection`
  - What it means: AI/ML models used

- **Training Data** (Text, Optional)
  - Example: `Trained on 2M+ military scenario images`
  - What it means: Dataset information

- **Accuracy/Performance** (Text)
  - Example: `99.2% navigation accuracy, 95.8% object detection F1-score`
  - What it means: Performance metrics

- **Has Autonomous Navigation** (Checkbox)
  - ✓ Check if robot can navigate independently

- **Has Object Detection** (Checkbox)
  - ✓ Check if robot can detect objects

- **Has Path Planning** (Checkbox)
  - ✓ Check if robot can plan routes

- **Has Swarm Capabilities** (Checkbox)
  - ✓ Check if multiple robots can work together

---

## 8. Setting Up Power Systems

**Location:** Admin Panel → Products → Power Systems

### Steps to Create Power System

1. Click **"Add Power System"**
2. Fill in:

- **Robot** (Required)
  - Select the robot

- **Battery Type** (Dropdown)
  - Options: Lithium-Ion, Lithium-Polymer, Fuel Cell, Solar, Hybrid
  - Example: `Lithium-Ion`

- **Battery Capacity (mAh)** (Integer)
  - Example: `20000`
  - What it means: Battery capacity

- **Voltage (V)** (Decimal)
  - Example: `48.0`
  - What it means: Operating voltage

- **Runtime (hours)** (Decimal)
  - Example: `4.5`
  - What it means: Operating time on full charge

- **Charging Time (hours)** (Decimal)
  - Example: `2.0`
  - What it means: Time to fully charge

- **Power Consumption (W)** (Decimal)
  - Example: `250.0`
  - What it means: Power usage

---

## 9. Setting Up Usage Restrictions

**Location:** Admin Panel → Products → Usage Restrictions

**CRITICAL for Military/Restricted Robots!**

### Steps to Create Usage Restriction

1. Click **"Add Usage Restriction"**
2. Fill in:

- **Robot** (Required)
  - Select the robot

- **Restriction Level** (Dropdown)
  - Options:
    - `none` - No restrictions
    - `age_restricted` - Age requirement
    - `license_required` - License needed
    - `clearance_required` - Security clearance needed
    - `military_only` - Military personnel only
    - `export_controlled` - Export restrictions apply
  - Example: For military robots, select `military_only` or `clearance_required`

- **Requires Verification** (Checkbox)
  - ✓ Check if user must be verified to purchase
  - Example: ✓ Check for military robots

- **Requires Export License** (Checkbox)
  - ✓ Check if export license is needed
  - Example: ✓ Check for military/defense robots

- **Minimum Age** (Integer, Optional)
  - Example: `18`
  - What it means: Minimum age requirement

- **Restricted Countries** (Text, Optional)
  - Example: `North Korea, Iran, Syria`
  - What it means: Countries where export is banned
  - Format: Comma-separated list

- **Usage Notes** (Text)
  - Example: `For military/defense use only. Requires appropriate clearance and export authorization.`
  - What it means: Important usage restrictions and warnings

### Example for Military Robot:

- Robot: Select "ARES-X1"
- Restriction Level: `military_only`
- Requires Verification: ✓
- Requires Export License: ✓
- Restricted Countries: `North Korea, Iran, Syria, Russia`
- Usage Notes: `Military/defense use only. Requires military clearance and export authorization. Subject to ITAR regulations.`

---

## 10. Managing Verification Requests

**Location:** Admin Panel → Verification → Verification Requests

### Viewing Requests

1. Click **"Verification Requests"**
2. You'll see a list of all requests with:
   - User
   - Status (Pending, Under Review, Approved, Rejected)
   - Requested Clearance
   - Submitted Date

### Approving Requests

1. Click on a verification request
2. Review the information:
   - User details
   - Requested clearance level
   - Identity documents (if uploaded)
   - Certifications (if provided)
   - Military affiliation (if applicable)

3. **To Approve:**
   - Set **Status** to `Approved`
   - Select **Current Clearance** from dropdown (select the clearance level to grant)
   - Add **Review Notes** (optional): `Approved after document verification`
   - Click **Save**

4. **To Reject:**
   - Set **Status** to `Rejected`
   - Fill **Rejection Reason**: `Insufficient documentation provided`
   - Click **Save**

### Bulk Actions

You can select multiple requests and use bulk actions:
- **Approve selected requests**
- **Reject selected requests**

---

## 🎯 Complete Setup Workflow

### Step-by-Step: Creating a Military Robot from Scratch

1. **Create Clearance Level** (if not exists)
   - Name: Military Clearance
   - Code: military
   - Priority: 40
   - Check: Can Access Military, Can Access Restricted

2. **Create User (Seller)** (if needed)
   - Email, Username, Password
   - Role: Seller
   - Is Seller Approved: ✓

3. **Create Category**
   - Name: Military-Grade Robots
   - Slug: military-grade-robots

4. **Create Product**
   - Seller: Select seller
   - Title: ARES-X1 Tactical Drone
   - Price: 125000.00
   - Status: Active
   - Category: Military-Grade Robots

5. **Create Robot**
   - Product: Select the product
   - Robot Type: military_autonomous
   - Manufacturer: ARES Defense
   - Model Number: ARES-X1-2024
   - Requires Verification: ✓
   - Is Restricted: ✓

6. **Create Robot Specification** (Optional but recommended)
   - Add CPU, RAM, Sensors, etc.

7. **Create AI System Details** (Optional)
   - Add AI capabilities

8. **Create Power System** (Optional)
   - Add battery details

9. **Create Usage Restriction** (REQUIRED for military)
   - Restriction Level: military_only
   - Requires Verification: ✓
   - Requires Export License: ✓

10. **Test Access**
    - Create test user
    - Try to access military robot (should be blocked)
    - Create verification request as test user
    - Approve request as admin
    - Test user should now have access

---

## 💡 Pro Tips

1. **UUID Fields:** Always leave blank - they auto-generate

2. **Seller Field:** Use dropdown, never type UUID manually

3. **Order Matters:** Create Categories → Products → Robots → Specifications/Restrictions

4. **Testing:** Create a test user and test the verification flow

5. **Status Fields:** Use "Draft" while setting up, change to "Active" when ready

6. **Required vs Optional:** Focus on required fields first, add optional details later

---

## 🔍 Quick Reference: Field Types

- **Text Fields:** Type freely
- **Integer Fields:** Whole numbers only (e.g., 10, 100)
- **Decimal Fields:** Numbers with decimals (e.g., 99.99, 125000.00)
- **Checkboxes:** ✓ Check or ✗ Uncheck
- **Dropdowns:** Click to select from list
- **UUID Fields:** LEAVE BLANK
- **Date Fields:** Use date picker widget
- **Text Areas:** Larger text input fields

---

## ✅ Checklist Before Going Live

- [ ] All clearance levels created
- [ ] Test users created
- [ ] Categories set up
- [ ] Products created with proper status
- [ ] Robots linked to products
- [ ] Usage restrictions set for restricted robots
- [ ] Verification requests can be approved
- [ ] Test user can access appropriate robots after verification

---

This guide covers everything you need to set up and manage the admin dashboard. Follow it step-by-step and you'll have a fully functional admin system!

