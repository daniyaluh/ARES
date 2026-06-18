# ARES Security Layer Documentation

## Overview

The ARES platform implements a comprehensive security layer for military-grade robotics access control. This system ensures that the Trust & Verification engine is not just a database field, but a functional security layer that actively protects sensitive resources.

## Components

### 1. Custom Decorators (`verification/security.py`)

#### `@clearance_required(level='secret', redirect_url=None, api_response=False)`

The primary decorator for enforcing clearance requirements.

**Parameters:**
- `level`: Required clearance level (`'none'`, `'public'`, `'confidential'`, `'secret'`, `'top_secret'`, `'military'`, `'government'`, `'contractor'`)
- `redirect_url`: Custom redirect URL (default: verification request page)
- `api_response`: If `True`, returns JSON response instead of redirect (for API views)

**Usage:**
```python
from verification.security import clearance_required

@clearance_required(level='TOP_SECRET')
def classified_view(request):
    # Only users with TOP_SECRET or higher clearance can access
    return render(request, 'classified.html')
```

#### `@military_clearance_required(redirect_url=None, api_response=False)`

Shorthand for military-grade resources.

**Usage:**
```python
@military_clearance_required()
def military_robot_view(request, robot_id):
    # Only users with military clearance can access
    return render(request, 'military_robot.html')
```

#### `@top_secret_clearance_required(redirect_url=None, api_response=False)`

Shorthand for TOP_SECRET level resources.

**Usage:**
```python
@top_secret_clearance_required()
def top_secret_view(request):
    return render(request, 'top_secret.html')
```

#### `@restricted_access_required(api_response=False)`

Requires any clearance above 'none' (any verified user).

**Usage:**
```python
@restricted_access_required()
def restricted_view(request):
    return render(request, 'restricted.html')
```

#### `@can_access_military_robots`

Checks if user can access military-grade robots.

**Usage:**
```python
@can_access_military_robots
def military_robot_detail(request, robot_id):
    return render(request, 'military_detail.html')
```

#### `@can_access_export_controlled`

Checks if user can access export-controlled products.

**Usage:**
```python
@can_access_export_controlled
def export_controlled_view(request, product_id):
    return render(request, 'export_controlled.html')
```

### 2. Middleware (`verification/middleware.py`)

#### `ClearanceRequiredMiddleware`

Automatically enforces clearance requirements for configured URL patterns.

**Configuration in `settings.py`:**
```python
CLEARANCE_PROTECTED_PATHS = {
    '/verification/military-robots/': 'military',
    '/verification/review/': 'secret',
    '/analytics/system-health/': 'secret',
    '/orders/purchase-requests/': 'confidential',
}
```

#### `SecurityAuditMiddleware`

Logs security-relevant events for audit purposes.

#### `IPWhitelistMiddleware` (Optional)

Provides IP whitelisting for extra security.

**Configuration:**
```python
CLEARANCE_IP_WHITELIST = ['192.168.1.0/24', '10.0.0.0/8']
CLEARANCE_IP_WHITELIST_PATHS = ['/military-robots/', '/verification/review/']
```

### 3. Clearance Priority System

Clearance levels are prioritized numerically:

| Level | Priority | Description |
|-------|----------|-------------|
| `none` | 0 | No clearance |
| `public` | 1 | Public trust |
| `confidential` | 2 | Confidential |
| `secret` | 3 | Secret |
| `top_secret` | 4 | Top Secret |
| `military` | 5 | Military clearance |
| `government` | 5 | Government clearance |
| `contractor` | 4 | Defense contractor |

Users with higher priority can access resources requiring lower priority.

## Usage Examples

### Function-Based Views

```python
from verification.security import clearance_required, military_clearance_required

@clearance_required(level='TOP_SECRET')
def classified_documents(request):
    return render(request, 'documents/classified.html')

@military_clearance_required()
def military_robots_list(request):
    return render(request, 'robots/military_list.html')
```

### Class-Based Views

```python
from django.utils.decorators import method_decorator
from verification.security import clearance_required

@method_decorator(clearance_required(level='secret'), name='dispatch')
class SensitiveListView(ListView):
    model = SensitiveModel
    template_name = 'sensitive_list.html'
```

### API Endpoints

```python
@clearance_required(level='military', api_response=True)
def military_robots_api(request):
    from django.http import JsonResponse
    return JsonResponse({'robots': []})
```

## Security Features

### 1. Authentication Check
- All decorators verify user authentication
- Unauthenticated users are redirected to login

### 2. Clearance Verification
- Checks user's current active clearance level
- Validates clearance hasn't expired
- Compares clearance priority levels

### 3. Superuser Bypass
- Superusers automatically bypass all clearance checks
- Logged for audit purposes

### 4. Expiration Handling
- Automatically detects expired clearances
- Redirects to renewal page

### 5. Audit Logging
- All access attempts are logged
- Failed attempts include IP address
- Successful access is logged for compliance

### 6. Error Handling
- Clear error messages for users
- JSON responses for API endpoints
- Proper HTTP status codes (401, 403)

## Integration with Verification Engine

The security layer integrates seamlessly with the existing Trust & Verification engine:

1. **VerificationRequest Model**: Checks approved verification requests
2. **ClearanceLevel Model**: Validates clearance levels and permissions
3. **VerificationLog Model**: Logs all security events
4. **Utils Functions**: Uses `get_user_clearance()` and `has_clearance()`

## Best Practices

1. **Use Specific Clearance Levels**: Always specify the exact clearance level needed
2. **Combine with Authentication**: Use `@login_required` for extra security
3. **Log Security Events**: All sensitive operations should be logged
4. **Test Clearance Checks**: Ensure decorators work correctly in all scenarios
5. **Handle Expired Clearances**: Always check for expiration
6. **Use API Responses**: For API endpoints, use `api_response=True`

## Testing

Test clearance requirements:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from verification.security import clearance_required

class ClearanceTest(TestCase):
    def test_clearance_required(self):
        # Test that users without clearance are blocked
        # Test that users with sufficient clearance can access
        pass
```

## Security Considerations

1. **Never Bypass Checks**: Always use decorators for sensitive resources
2. **Regular Audits**: Review security logs regularly
3. **Clearance Expiration**: Monitor and handle expired clearances
4. **IP Whitelisting**: Use for extra-sensitive areas if needed
5. **Rate Limiting**: Consider adding rate limiting for failed attempts

## Troubleshooting

**Issue**: Decorator not working
- Check middleware is installed in `settings.py`
- Verify user has active clearance
- Check clearance hasn't expired

**Issue**: Redirect loops
- Ensure redirect URLs are accessible
- Check clearance requirements aren't too restrictive

**Issue**: API returning HTML
- Set `api_response=True` for API endpoints









