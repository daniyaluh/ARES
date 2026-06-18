# ARES Dashboard Comprehensive Guide

## 🎯 Overview

ARES (Autonomous Robotics Enterprise System) is a secure marketplace for robotics, from consumer drones to military-grade autonomous systems. This guide explains each section and how to use them.

---

## 🏠 HOME PAGE (`/`)

**Purpose:** Main landing page with overview and quick access to key features.

**Features:**
- System statistics (Total Robots, Active Users, Orders, System Status)
- Quick action cards for:
  - Browse Robots
  - Military-Grade Systems
  - Get Verified

**How to Use:**
- View overall system status
- Navigate to different sections via quick action cards
- Access login/register if not authenticated

---

## 👥 USERS SECTION (`/users/`)

### Purpose
Manage user accounts, profiles, authentication, and user-related settings.

### Key Features

#### 1. **Authentication** (`/users/login/`, `/users/register/`)
- **Login:** Access the platform with email and password
- **Register:** Create new user accounts
- **Password Reset:** Reset forgotten passwords (coming soon)

#### 2. **User Profile** (`/users/profile/`)
- **Profile Detail:** View your profile information
- **Profile Edit:** Update personal information, bio, avatar
- **Profile Settings:** Configure account preferences
- **Profile Security:** Manage password, 2FA, security keys

**Features:**
- View and edit personal information
- Manage profile picture
- Update contact details
- Security settings (2FA, security keys)

#### 3. **Address Book** (`/users/addresses/`)
- **List Addresses:** View all saved addresses
- **Create Address:** Add shipping/billing addresses
- **Edit/Delete:** Manage addresses
- **Set Default:** Mark primary address

**Use Case:** Store multiple addresses for shipping robots/products

#### 4. **Roles & Permissions** (`/users/roles/`)
- **View Roles:** See all system roles (Admin, Buyer, Seller, etc.)
- **Role Details:** Understand permissions for each role
- **Permission Matrix:** Configure what each role can do

**Roles Available:**
- Guest, Client, Buyer, Seller
- Moderator, Support Staff
- Account Manager, Compliance Officer
- Military Auditor, System Admin, Super Admin

#### 5. **Sessions & Activity** (`/users/sessions/`, `/users/activity/`)
- **Active Sessions:** View and manage logged-in sessions
- **Activity Logs:** Audit trail of user actions
- **Revoke Sessions:** Logout from specific devices

**Security Feature:** Monitor account access and activity

#### 6. **Notification Preferences** (`/users/notifications/`)
- Configure email notifications
- Set on-site notification preferences
- Manage push notifications (if enabled)

---

## 🤖 PRODUCTS SECTION (`/products/`)

### Purpose
Browse, create, and manage products and robots in the marketplace.

### Key Features

#### 1. **Product List** (`/products/`)
- View all available products
- Filter by category, price, status
- Search products

#### 2. **Product Detail** (`/products/<id>/`)
- View full product information
- See specifications, pricing, reviews
- Add to favorites
- Purchase/request product

#### 3. **Create Product** (`/products/create/`)
- **Required Fields:**
  - Title, Description, Price
  - Seller (auto-filled if you're logged in)
  - Status, Category
- **Optional:**
  - Short description, Images
  - Variants, Tags

**Note:** UUID field auto-generates - leave blank!

#### 4. **Robots** (`/products/robots/`)
- Browse all robots
- View robot-specific details:
  - **Specifications:** CPU, RAM, sensors, communication
  - **AI System Details:** AI capabilities, models, performance
  - **Power System:** Battery, runtime, charging
  - **Usage Restrictions:** Clearance requirements, export controls

#### 5. **Categories** (`/products/categories/`)
- Browse product categories
- Hierarchical structure (parent/child categories)
- Filter products by category

#### 6. **Product Reviews** (`/products/<id>/reviews/`)
- View customer reviews and ratings
- Create reviews for purchased products
- Mark reviews as helpful

#### 7. **Favorites/Wishlist** (`/products/favorites/`)
- Save products for later
- Manage wishlist
- Set priorities and reminders

#### 8. **Seller Features** (`/products/my-products/`)
- View your products
- Analytics and sales metrics
- Manage inventory

**Use Case:** Sellers create and manage their product catalog

---

## 🔐 VERIFICATION SECTION (`/verification/`)

### Purpose
Trust & Verification engine for accessing restricted/military-grade robots.

### Key Features

#### 1. **Robot Lists with Access Control**
- **All Robots** (`/verification/robots/`)
  - Browse all robots
  - Automatically filters based on your clearance level
  - Shows only robots you're authorized to view

- **Military-Grade Robots** (`/verification/military-robots/`)
  - **REQUIRES MILITARY CLEARANCE**
  - Advanced autonomous systems
  - Restricted access - will redirect if no clearance

#### 2. **Verification Requests** (`/verification/request/`)
- **Submit Request:**
  - Select requested clearance level
  - Provide reason for request
  - Describe intended use
  - Upload identity documents
  - Add certifications
  - Provide military affiliation (if applicable)

- **View Requests** (`/verification/requests/my/`)
  - Track request status (Pending, Under Review, Approved, Rejected)
  - View review notes
  - See current clearance level if approved

#### 3. **Clearance Levels**
- **None:** No clearance
- **Public:** Public trust
- **Confidential:** Confidential level
- **Secret:** Secret clearance
- **Top Secret:** Top secret clearance
- **Military:** Military clearance
- **Government:** Government clearance
- **Contractor:** Defense contractor clearance

#### 4. **My Clearance Status** (`/verification/my-clearance/`)
- View your current clearance level
- Check expiration date
- Renew clearance if expired

#### 5. **Admin Review** (`/verification/review/`) - Staff Only
- Review pending verification requests
- Approve/reject requests
- Assign clearance levels
- View identity documents and certifications
- Add review notes

**Security Features:**
- Clearance-based access control
- Document verification
- Audit logging
- Expiration management

**Use Case:** Users submit verification requests to access restricted robots. Admins review and approve.

---

## 📦 ORDERS SECTION (`/orders/`)

### Purpose
Manage orders, purchase requests, transactions, and shipping.

### Key Features

#### 1. **Purchase Requests** (`/orders/purchase-requests/`)
- **Create Request:** Submit request to purchase (non-direct buy)
- **View Requests:** Track your purchase requests
- **Status:** Pending → Under Review → Approved/Rejected
- **Admin Approval:** Staff review and approve requests

**Use Case:** For restricted products that require approval before purchase

#### 2. **Orders** (`/orders/`)
- **List Orders:** View all orders (staff) or your orders
- **Order Detail:** View full order information
- **Order Items:** Products included in order
- **Order Status:** Track order progress
- **Status History:** See order status changes over time

#### 3. **Transactions** (`/orders/transactions/`)
- View payment transactions
- Track transaction status
- Link transactions to orders

#### 4. **Invoices** (`/orders/invoices/`)
- View invoices for orders
- Download invoices (PDF)
- Send invoices via email

#### 5. **Shipping** (`/orders/<id>/shipping/`)
- View shipping details
- Track shipping status
- Update shipping information
- Tracking numbers

#### 6. **Approval Chain** (`/orders/<id>/approvals/`)
- Multi-level approval workflow
- Assign approvers
- Track approval status
- Approve/reject at each level

**Use Case:** Process orders, handle payments, manage shipping, and track order status

---

## 🎫 SUPPORT SECTION (`/support/`)

### Purpose
Customer support, help resources, and technical documentation.

### Key Features

#### 1. **Support Tickets** (`/support/tickets/`)
- **Create Ticket:** Submit support requests
- **View Tickets:** Track ticket status
- **Add Responses:** Communicate with support staff
- **Close/Reopen:** Manage ticket lifecycle

**Ticket Status:** Open → In Progress → Resolved → Closed

#### 2. **Technical Manuals** (`/support/manuals/`)
- View technical documentation
- Download manuals
- Search by category
- Access robot specifications and guides

#### 3. **FAQs** (`/support/faqs/`)
- Browse frequently asked questions
- Search FAQs
- Mark helpful answers
- Filter by category

**Use Case:** Get help, access documentation, and submit support requests

---

## 📊 ANALYTICS SECTION (`/analytics/`) - Staff Only

### Purpose
System analytics, metrics, and monitoring dashboards.

### Key Features

#### 1. **Dashboard** (`/analytics/dashboard/`)
- Overview of system metrics
- Real-time statistics
- Key performance indicators

#### 2. **System Health** (`/analytics/system-health/`)
- Monitor system status
- View health logs
- Check for alerts
- Component status tracking

#### 3. **Sales Metrics** (`/analytics/sales/`)
- Revenue analytics
- Product sales reports
- Seller performance
- Export sales data

#### 4. **User Activity** (`/analytics/user-activity/`)
- Track user actions
- View activity logs
- Filter by user or activity type
- Security audit trail

#### 5. **Inventory** (`/analytics/inventory/`)
- Inventory snapshots
- Low stock alerts
- Product inventory analytics
- Track inventory changes

#### 6. **Market Trends** (`/analytics/market-trends/`)
- Analyze market trends
- Category performance
- Trend analysis reports

**Use Case:** Monitor system performance, analyze sales, and track user activity

---

## 🔒 SECURITY FEATURES

### Clearance-Based Access Control

**How It Works:**
1. User submits verification request
2. Admin reviews documents and information
3. Admin approves and assigns clearance level
4. User can now access resources matching their clearance

**Protected Resources:**
- Military-grade robots require military clearance
- Restricted products require appropriate clearance
- Export-controlled items need export license clearance

**Decorators Used:**
- `@clearance_required(level='TOP_SECRET')` - Specific clearance needed
- `@military_clearance_required()` - Military clearance required
- `@restricted_access_required()` - Any clearance above 'none'

---

## 📋 TESTING WORKFLOW

### Step 1: Create Test Data (Admin)
1. Login as admin (admin@admin.com / admin1234)
2. Go to Admin Panel: http://127.0.0.1:8000/admin/
3. Create a Category: Products → Categories → Add
4. Create a Product: Products → Products → Add
5. Create a Robot: Products → Robots → Add (link to product)

### Step 2: Test as Regular User
1. Register new user: http://127.0.0.1:8000/users/register/
2. Login: http://127.0.0.1:8000/users/login/
3. Browse products: http://127.0.0.1:8000/products/
4. Try accessing military robots: http://127.0.0.1:8000/verification/military-robots/
   - Should redirect to verification request page

### Step 3: Test Verification
1. Submit verification request: http://127.0.0.1:8000/verification/request/
2. Login as admin
3. Review request: http://127.0.0.1:8000/verification/review/
4. Approve request and assign clearance
5. Login as regular user
6. Try accessing military robots again - should work!

### Step 4: Test Orders
1. Create purchase request: http://127.0.0.1:8000/orders/purchase-requests/create/
2. Admin approves: Admin Panel → Orders → Purchase Requests
3. Order gets created
4. View order: http://127.0.0.1:8000/orders/

---

## 🎯 Key URLs Reference

### Public Pages
- Home: `/`
- Products: `/products/`
- Robots: `/verification/robots/`

### Authentication Required
- Login: `/users/login/`
- Register: `/users/register/`
- Profile: `/users/profile/`
- My Orders: `/orders/my-orders/`

### Requires Clearance
- Military Robots: `/verification/military-robots/`
- Restricted Products: (automatically filtered)

### Admin Only
- Admin Panel: `/admin/`
- Review Verification: `/verification/review/`
- Analytics: `/analytics/dashboard/`

---

## 💡 Tips

1. **UUID Fields:** Always leave blank - auto-generated
2. **Seller Field:** Use dropdown to select user, not text input
3. **Clearance:** Start with lower clearance, request higher if needed
4. **Templates:** Basic templates created - customize as needed
5. **Admin Panel:** Best place to create test data

---

## 🐛 Troubleshooting

**Template Errors:**
- Basic templates are created for all major views
- Some views may need additional templates
- Check template directory structure

**Access Denied:**
- Check if you're logged in
- Verify you have required clearance
- Check if resource requires staff status

**UUID Errors:**
- Leave UUID fields blank
- Django generates them automatically

---

This guide covers all major sections of the ARES platform. Each section is functional and ready for testing!









