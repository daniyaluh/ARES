# ARES Testing Guide

## 🔐 Superuser Credentials

- **Email:** admin@admin.com
- **Username:** admin
- **Password:** admin1234

## 🚀 Quick Start Testing

### 1. Access the Application

The server should already be running at:
- **Main Site:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

### 2. Admin Panel Testing

#### Login to Admin
1. Go to: http://127.0.0.1:8000/admin/
2. Login with:
   - Email: `admin@admin.com`
   - Password: `admin1234`

#### Test Admin Features
- **Users Management:** View and manage all users
- **Products:** Create and manage products/robots
- **Verification:** Review verification requests
- **Orders:** View orders and transactions
- **Support:** Manage support tickets
- **Analytics:** View system logs and metrics

### 3. Frontend Testing

#### User Registration & Login
1. **Register a New User:**
   - Go to: http://127.0.0.1:8000/users/register/
   - Fill in the registration form
   - Create an account

2. **Login:**
   - Go to: http://127.0.0.1:8000/users/login/
   - Use your credentials to login

#### Product & Robot Testing
1. **View Products:**
   - http://127.0.0.1:8000/products/
   - http://127.0.0.1:8000/products/robots/

2. **Create Product (as logged-in seller):**
   - http://127.0.0.1:8000/products/create/
   - Fill in product details

3. **View Categories:**
   - http://127.0.0.1:8000/products/categories/

#### Verification Testing
1. **Submit Verification Request:**
   - http://127.0.0.1:8000/verification/request/
   - Fill in verification details

2. **View My Requests:**
   - http://127.0.0.1:8000/verification/requests/my/

3. **View Military Robots (requires clearance):**
   - http://127.0.0.1:8000/verification/military-robots/
   - Will redirect if no clearance

4. **Review Requests (Admin only):**
   - http://127.0.0.1:8000/verification/review/
   - Approve/reject verification requests

#### Orders Testing
1. **View Orders:**
   - http://127.0.0.1:8000/orders/
   - http://127.0.0.1:8000/orders/my-orders/

2. **Create Purchase Request:**
   - http://127.0.0.1:8000/orders/purchase-requests/create/

3. **View Purchase Requests:**
   - http://127.0.0.1:8000/orders/purchase-requests/

#### Support Testing
1. **View Support Tickets:**
   - http://127.0.0.1:8000/support/tickets/

2. **Create Support Ticket:**
   - http://127.0.0.1:8000/support/tickets/create/

3. **View FAQs:**
   - http://127.0.0.1:8000/support/faqs/

#### Analytics Testing (Admin only)
1. **Dashboard:**
   - http://127.0.0.1:8000/analytics/dashboard/

2. **System Health:**
   - http://127.0.0.1:8000/analytics/system-health/

3. **Sales Metrics:**
   - http://127.0.0.1:8000/analytics/sales/metrics/

## 🔒 Security Testing

### Test Clearance Requirements

1. **Try accessing military robots without clearance:**
   - Login as regular user
   - Go to: http://127.0.0.1:8000/verification/military-robots/
   - Should redirect to verification request page

2. **Test clearance decorator:**
   - As admin (superuser), you should have access to everything
   - As regular user, restricted resources should require verification

3. **Test verification workflow:**
   - Submit verification request
   - As admin, approve it from review page
   - User should now have clearance

## 📋 Testing Checklist

### ✅ Basic Functionality
- [ ] Can access home page
- [ ] Can register new user
- [ ] Can login
- [ ] Can logout
- [ ] Can access admin panel
- [ ] Can view products
- [ ] Can view robots

### ✅ Product Management
- [ ] Can create product (as seller)
- [ ] Can edit product
- [ ] Can delete product
- [ ] Can add product gallery images
- [ ] Can create product variants
- [ ] Can add product reviews

### ✅ Verification System
- [ ] Can submit verification request
- [ ] Can view verification status
- [ ] Admin can review requests
- [ ] Admin can approve/reject requests
- [ ] Can view clearance levels
- [ ] Clearance restrictions work correctly

### ✅ Orders
- [ ] Can create purchase request
- [ ] Can view orders
- [ ] Can view order details
- [ ] Can view invoices
- [ ] Can track shipping

### ✅ Support
- [ ] Can create support ticket
- [ ] Can view tickets
- [ ] Can add responses to tickets
- [ ] Can view FAQs

### ✅ User Management
- [ ] Can view profile
- [ ] Can edit profile
- [ ] Can manage addresses
- [ ] Can view activity logs
- [ ] Can manage sessions

## 🐛 Troubleshooting

### If templates show errors:
- Views are functional but templates need to be created
- Most views will show "TemplateDoesNotExist" error
- This is expected - templates are placeholders for now

### If server is not running:
```bash
python manage.py runserver
```

### If migrations needed:
```bash
python manage.py makemigrations
python manage.py migrate
```

### To create additional test data:
1. Use admin panel to create test records
2. Or use Django shell:
```bash
python manage.py shell
```

## 🎯 Key URLs to Test

### Public Pages
- Home: `/`
- Products: `/products/`
- Categories: `/products/categories/`

### Authentication Required
- Login: `/users/login/`
- Register: `/users/register/`
- Profile: `/users/profile/`
- My Orders: `/orders/my-orders/`
- My Tickets: `/support/tickets/my/`

### Admin Only
- Admin Panel: `/admin/`
- Verification Review: `/verification/review/`
- Analytics Dashboard: `/analytics/dashboard/`
- Order Analytics: `/orders/analytics/`

### Restricted (Requires Clearance)
- Military Robots: `/verification/military-robots/`
- Classified Resources: (will depend on implementation)

## 📝 Notes

- All URLs follow the pattern: `/app-name/view-name/`
- Most views require authentication (`@login_required`)
- Some views require staff status (`request.user.is_staff`)
- Security decorators enforce clearance levels
- All models are registered in admin for easy testing

Happy Testing! 🚀









