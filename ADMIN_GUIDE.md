# ARES Admin Panel Guide

## 🔑 Login Credentials

- **Email:** admin@admin.com
- **Password:** admin1234

## 📝 Adding Products - UUID Field Explanation

### ⚠️ Important: UUID Field

**You DO NOT need to fill in the UUID field!**

The UUID field is **automatically generated** when you create a new product. Here's what you need to know:

1. **Leave it blank** - The system will automatically create a unique UUID
2. **It's read-only** - You cannot edit it after creation
3. **Auto-generated** - Django generates it using `uuid.uuid4()`

### ✅ Steps to Add a Product

1. Go to Admin Panel: http://127.0.0.1:8000/admin/
2. Navigate to **Products** → **Products**
3. Click **"Add Product"**
4. Fill in these **required fields**:
   - **Seller:** Select a user (or yourself)
   - **Title:** Product name (e.g., "Autonomous Drone X1")
   - **Description:** Detailed product description
   - **Price:** Product price (e.g., 999.99)
   - **Status:** Choose status (start with "draft" or "active")
   - **Category:** Select a category (create one first if needed)

5. **Optional fields** you can fill:
   - Short Description
   - Compare at Price (for discounts)
   - Stock Quantity
   - Shipping Type
   - Tags
   - SEO fields

6. **UUID Field:** 
   - **LEAVE IT BLANK** or ignore it completely
   - It will be auto-generated when you save

7. Click **"Save"**

### 📦 Adding a Robot (After Product)

After creating a Product, you can add Robot details:

1. Go to **Products** → **Robots**
2. Click **"Add Robot"**
3. **Product:** Select the product you just created
4. Fill in robot-specific fields:
   - Robot Type (e.g., "military_autonomous")
   - Manufacturer
   - Model Number
   - Physical specifications
   - etc.

5. **UUID Field:** Again, leave it blank - auto-generated

### 🎯 Quick Test Data Creation

**Create a Category First:**
1. Products → Categories → Add Category
2. Name: "Military Drones"
3. Save

**Create a Product:**
1. Products → Products → Add Product
2. Seller: admin
3. Title: "ARES-1 Military Drone"
4. Description: "Advanced autonomous military-grade drone"
5. Price: 50000.00
6. Category: Military Drones
7. Status: active
8. **UUID: Leave blank**
9. Save

**Create Robot Details:**
1. Products → Robots → Add Robot
2. Product: Select "ARES-1 Military Drone"
3. Robot Type: military_autonomous
4. Manufacturer: "ARES Defense Systems"
5. Model Number: "ARES-1"
6. Requires Verification: ✓ (check this)
7. Is Restricted: ✓ (check this)
8. **UUID: Leave blank**
9. Save

## 🔍 Understanding UUID Fields

UUID (Universally Unique Identifier) fields:
- Format: `550e8400-e29b-41d4-a716-446655440000`
- Automatically generated
- Unique for each record
- Used for security (harder to guess than sequential IDs)
- **Never manually enter these** - Django handles it

## ✅ All Models with Auto-Generated UUIDs

These models have auto-generated UUIDs (leave blank):
- Products
- Robots
- Categories
- Orders
- Verification Requests
- Support Tickets
- All other models

## 🐛 If UUID Field Shows Error

If you see an error about UUID format:
1. **Clear the field** - Leave it completely empty
2. **Save again** - Django will generate it automatically
3. If still having issues, refresh the page and try again

## 💡 Pro Tip

When adding any new record in admin:
- **Always leave UUID fields blank**
- Focus on filling the actual data fields
- Let Django handle the ID generation automatically

Happy Admin-ing! 🚀









