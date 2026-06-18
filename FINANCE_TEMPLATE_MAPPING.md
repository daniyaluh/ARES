# Finance System Template Mapping

## Complete URL to Template Reference

This document shows the mapping between finance URLs and their corresponding templates for the ARES platform.

---

## Admin Finance URLs

### 1. Finance Dashboard
- **URL**: `/orders/finance/admin/dashboard/`
- **URL Name**: `orders:admin-finance-dashboard`
- **View**: `admin_finance_dashboard`
- **Template**: `templates/orders/finance/admin_dashboard.html`
- **Access**: Staff only
- **Description**: Overview of platform revenue, earnings, and financial metrics

### 2. Revenue List
- **URL**: `/orders/finance/admin/revenue/`
- **URL Name**: `orders:admin-revenue-list`
- **View**: `admin_revenue_list`
- **Template**: `templates/orders/finance/admin_revenue_list.html`
- **Access**: Staff only
- **Description**: Detailed list of all platform revenue entries with filtering

### 3. Seller Earnings
- **URL**: `/orders/finance/admin/earnings/`
- **URL Name**: `orders:admin-seller-earnings`
- **View**: `admin_seller_earnings`
- **Template**: `templates/orders/finance/admin_seller_earnings.html`
- **Access**: Staff only
- **Description**: View all seller earnings across the platform

### 4. Payouts List
- **URL**: `/orders/finance/admin/payouts/`
- **URL Name**: `orders:admin-payouts-list`
- **View**: `admin_payouts_list`
- **Template**: `templates/orders/finance/admin_payouts.html`
- **Access**: Staff only
- **Description**: Manage seller payout requests (pending/approved/rejected)

### 5. Payout Detail
- **URL**: `/orders/finance/admin/payouts/<uuid:payout_id>/`
- **URL Name**: `orders:admin-payout-detail`
- **View**: `admin_payout_detail`
- **Template**: `templates/orders/finance/admin_payout_detail.html`
- **Access**: Staff only
- **Description**: Review and approve/reject specific payout request

### 6. All Transactions
- **URL**: `/orders/finance/admin/transactions/`
- **URL Name**: `orders:admin-all-transactions`
- **View**: `admin_all_transactions`
- **Template**: `templates/orders/finance/admin_transactions.html`
- **Access**: Staff only
- **Description**: View all wallet transactions across all users

### 7. Analytics Dashboard
- **URL**: `/orders/finance/admin/analytics/`
- **URL Name**: `orders:admin-finance-analytics`
- **View**: `admin_finance_analytics`
- **Template**: `templates/orders/finance/admin_analytics.html`
- **Access**: Staff only
- **Description**: Charts and graphs for revenue trends and analytics

---

## Seller Finance URLs

### 8. Seller Dashboard
- **URL**: `/orders/finance/seller/dashboard/`
- **URL Name**: `orders:seller-finance-dashboard`
- **View**: `seller_finance_dashboard`
- **Template**: `templates/orders/finance/seller_dashboard.html`
- **Access**: Sellers only
- **Description**: Seller's personal finance overview with earnings

### 9. Seller Earnings
- **URL**: `/orders/finance/seller/earnings/`
- **URL Name**: `orders:seller-earnings`
- **View**: `seller_earnings`
- **Template**: `templates/orders/finance/seller_earnings.html`
- **Access**: Sellers only
- **Description**: Detailed list of seller's individual earnings by sale

### 10. Seller Payouts
- **URL**: `/orders/finance/seller/payouts/`
- **URL Name**: `orders:seller-payouts`
- **View**: `seller_payouts`
- **Template**: `templates/orders/finance/seller_payouts.html`
- **Access**: Sellers only
- **Description**: Seller's payout history and request new payouts

### 11. Seller Payout Detail
- **URL**: `/orders/finance/seller/payouts/<uuid:payout_id>/`
- **URL Name**: `orders:seller-payout-detail`
- **View**: `seller_payout_detail`
- **Template**: `templates/orders/finance/seller_payout_detail.html`
- **Access**: Sellers only
- **Description**: View specific payout request details and status

---

## User Finance URLs

### 12. User Wallet
- **URL**: `/orders/finance/user/wallet/`
- **URL Name**: `orders:user-wallet`
- **View**: `user_wallet`
- **Template**: `templates/orders/finance/user_wallet.html`
- **Access**: Authenticated users
- **Description**: User's wallet balance and transaction overview

### 13. Payment History
- **URL**: `/orders/finance/user/payments/`
- **URL Name**: `orders:user-payment-history`
- **View**: `user_payment_history`
- **Template**: `templates/orders/finance/user_payment_history.html`
- **Access**: Authenticated users
- **Description**: Complete payment and transaction history

### 14. Purchased Products
- **URL**: `/orders/finance/user/purchases/`
- **URL Name**: `orders:user-purchased-products`
- **View**: `user_purchased_products`
- **Template**: `templates/orders/finance/user_purchased_products.html`
- **Access**: Authenticated users
- **Description**: List of all products/robots purchased by user

---

## Complete Template List

All templates are located in: `templates/orders/finance/`

1. ✅ `admin_dashboard.html` - Admin finance overview
2. ✅ `admin_revenue_list.html` - Platform revenue tracking
3. ✅ `admin_seller_earnings.html` - All seller earnings
4. ✅ `admin_payouts.html` - Payout requests management
5. ✅ `admin_payout_detail.html` - Individual payout approval
6. ✅ `admin_transactions.html` - All user transactions
7. ✅ `admin_analytics.html` - Financial analytics (NEEDS CREATION)
8. ✅ `seller_dashboard.html` - Seller finance overview
9. ✅ `seller_earnings.html` - Seller earnings list
10. ✅ `seller_payouts.html` - Seller payout history
11. ✅ `seller_payout_detail.html` - Seller payout details
12. ✅ `user_wallet.html` - User wallet interface
13. ✅ `user_payment_history.html` - User transaction history
14. ✅ `user_purchased_products.html` - User's purchased items

---

## Quick Access Guide

### For Admin Staff:
```
/orders/finance/admin/dashboard/     → Financial overview
/orders/finance/admin/revenue/       → Platform revenue details
/orders/finance/admin/payouts/       → Approve seller payouts
/orders/finance/admin/analytics/     → Revenue analytics
```

### For Sellers:
```
/orders/finance/seller/dashboard/    → Your earnings overview
/orders/finance/seller/earnings/     → Your sales breakdown
/orders/finance/seller/payouts/      → Request & track payouts
```

### For Users:
```
/orders/finance/user/wallet/         → Your wallet balance
/orders/finance/user/payments/       → Your payment history
/orders/finance/user/purchases/      → Your purchased robots
```

---

## Testing Checklist

- [ ] All admin URLs load correctly with staff account
- [ ] All seller URLs load correctly with seller account
- [ ] All user URLs load correctly with regular user account
- [ ] Pagination works on list views
- [ ] Filters work on revenue/earnings lists
- [ ] Payout approval flow works
- [ ] Transaction history displays correctly
- [ ] All templates extend base.html properly
- [ ] Tailwind styling renders correctly
- [ ] Mobile responsive design works

---

## Database Requirements

Before testing, ensure these migrations are applied:
```bash
python manage.py migrate orders 0007_sellerpayout_sellerearnings_platformrevenue_and_more
```

## Next Steps

1. Create `admin_analytics.html` template (only remaining template)
2. Test all URL endpoints
3. Verify permissions are enforced
4. Test payout approval workflow
5. Check mobile responsiveness
6. Add any missing error handling

---

*Last Updated: Today*
*Total URLs: 14*
*Total Templates: 14*
*Status: 13/14 Complete (93%)*
