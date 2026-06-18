# ARES URL Patterns Summary

## Total URL Count: **230+ URLs**

### Breakdown by App:

1. **Users App** (`users/urls.py`): **31 URLs**
   - Authentication (login, logout, register, password reset)
   - User profile management
   - Address book CRUD
   - Role & permissions
   - Sessions & activity logs
   - Notification preferences
   - Security keys

2. **Products App** (`products/urls.py`): **49 URLs**
   - Product CRUD operations
   - Robot-specific URLs with specifications
   - Categories management
   - Product gallery
   - Variants management
   - Reviews & ratings
   - Tags & favorites
   - Search & filtering
   - Seller analytics

3. **Verification App** (`verification/urls.py`): **34 URLs**
   - Robot/product access with verification checks
   - Verification request management
   - Identity documents
   - Certifications
   - Military affiliation
   - Clearance levels
   - Review & approval workflow
   - Verification logs

4. **Orders App** (`orders/urls.py`): **46 URLs**
   - Purchase requests (non-direct buy)
   - Order CRUD operations
   - Order items management
   - Approval chain workflow
   - Transactions
   - Invoices & downloads
   - Shipping management
   - Status history
   - Filtering & search
   - Analytics & reports

5. **Support App** (`support/urls.py`): **35 URLs**
   - Support ticket management
   - Ticket responses
   - Ticket filtering & search
   - Technical manuals
   - FAQ management
   - Support analytics

6. **Analytics App** (`analytics/urls.py`): **35 URLs**
   - Dashboard & overview
   - System health monitoring
   - Sales metrics & analytics
   - User activity tracking
   - Inventory snapshots
   - Market trends
   - Platform configuration
   - Reports & exports

## Naming Convention

All URLs follow consistent naming:
- Format: `app-name:view-name` (using hyphens)
- Examples:
  - `products:robot-detail`
  - `orders:purchase-request-list`
  - `verification:request-detail`
  - `support:ticket-create`

## URL Structure Examples

### Product URLs:
```
/products/                                    → product-list
/products/robots/                             → robot-list
/products/robots/<uuid:robot_id>/             → robot-detail
/products/robots/<uuid:robot_id>/specifications/ → robot-specifications
/products/<uuid:product_id>/reviews/          → product-review-list
```

### Order URLs:
```
/orders/                                      → order-list
/orders/purchase-requests/                    → purchase-request-list
/orders/<uuid:order_id>/                      → order-detail
/orders/<uuid:order_id>/invoice/              → order-invoice
```

### Verification URLs:
```
/verification/robots/                         → robot-list (with access control)
/verification/military-robots/                → military-robots-list
/verification/request/                        → request (create)
/verification/request/<uuid:request_id>/      → request-detail
```

## Next Steps

1. **Implement Views**: Create corresponding view functions/classes in each app's `views.py`
2. **Create Templates**: Build templates for each view
3. **Add Authentication**: Ensure proper authentication/permissions for protected views
4. **API Endpoints**: Consider adding DRF API endpoints for REST API access

## Notes

- All URLs use UUID primary keys where applicable
- URL patterns include proper namespacing with `app_name`
- Consistent use of hyphens in URL names
- All major CRUD operations are covered
- Filtering, searching, and analytics views included
- Specialized views for workflows (approval chains, verification, etc.)









