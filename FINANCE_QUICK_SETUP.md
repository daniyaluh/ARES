# Finance System - Quick Setup

## Run These Commands Now:

### 1. Create Migrations
```powershell
python manage.py makemigrations orders
```

### 2. Apply Migrations
```powershell
python manage.py migrate orders
```

### 3. Verify Installation
```powershell
python manage.py shell
```
Then in shell:
```python
from orders.models import PlatformRevenue, SellerEarnings, SellerPayout, WalletTransaction
print("✓ All financial models imported successfully!")
exit()
```

## Access Your Finance Dashboards:

### Admin/Staff:
```
http://127.0.0.1:8000/orders/finance/admin/dashboard/
```

### Sellers:
```
http://127.0.0.1:8000/orders/finance/seller/dashboard/
```

### Users:
```
http://127.0.0.1:8000/orders/finance/user/wallet/
http://127.0.0.1:8000/orders/finance/user/payments/
```

## Admin Panel (New Models):
```
http://127.0.0.1:8000/admin/orders/platformrevenue/
http://127.0.0.1:8000/admin/orders/sellerearnings/
http://127.0.0.1:8000/admin/orders/sellerpayout/
http://127.0.0.1:8000/admin/orders/wallettransaction/
```

## That's It! 🎉

Your finance system is ready to track:
- Platform revenue & commissions
- Seller earnings & payouts
- User payments & wallet balance
- All transactions across the platform
