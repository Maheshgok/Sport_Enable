# 🔧 API Improvements - Quick Developer Guide

## What Changed

Your API just got **6 critical improvements** that make it production-ready. Here's how to use them:

---

## 1️⃣ Error Handling - Use `@handle_errors` Decorator

### Before
```python
@app.route('/api/endpoint', methods=['POST'])
def endpoint():
    try:
        # ... code ...
        if error:
            return jsonify({'error': 'Something broke'}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
```

### After
```python
from api.error_handler import handle_errors, error_response, success_response, APIError

@app.route('/api/endpoint', methods=['POST'])
@handle_errors  # ← Automatic error catching!
def endpoint():
    # ... code ...
    if error:
        raise APIError('INVALID_FORMAT', details={'field': 'value'})
    
    return success_response({'result': data})
```

**Benefits:**
- ✅ No try/except boilerplate
- ✅ Consistent error format
- ✅ Automatic logging
- ✅ No internal errors exposed

---

## 2️⃣ Validation - Reuse Validators

### Create New Validator (2 seconds)
```python
from api.validators import FieldValidator

# Validate email
is_valid, error = FieldValidator.email(email_value)
if not is_valid:
    return error_response('INVALID_EMAIL', error)

# Validate string
is_valid, error = FieldValidator.string_field(name, 'name', min_length=1, max_length=50)
```

### Use Existing Validators
```python
from api.validators import RegistrationValidator, LoginValidator

# Validate registration
is_valid, errors = RegistrationValidator.validate(request.get_json())
if not is_valid:
    return error_response('INVALID_FORMAT', errors=errors)

# Validate login
is_valid, errors = LoginValidator.validate(request.get_json())
```

**Benefits:**
- ✅ No repeated validation code
- ✅ Consistent error messages
- ✅ Easy to maintain

---

## 3️⃣ Response Format - Use Response Helpers

### Success Response
```python
from api.error_handler import success_response

return success_response(
    data={'user_id': '123', 'email': 'test@moove.com'},
    message='User created successfully',
    status=201
)
```

Response:
```json
{
  "success": true,
  "data": {
    "user_id": "123",
    "email": "test@moove.com"
  },
  "message": "User created successfully",
  "timestamp": "2026-06-27T10:30:00"
}
```

### Error Response
```python
from api.error_handler import error_response

return error_response(
    error_code='EMAIL_ALREADY_REGISTERED',
    message='Custom message (optional)',
    details={'email': 'test@moove.com'},
    status=409
)
```

Response:
```json
{
  "success": false,
  "error_code": "EMAIL_ALREADY_REGISTERED",
  "message": "Email is already registered",
  "details": {"email": "test@moove.com"},
  "timestamp": "2026-06-27T10:30:00"
}
```

**Benefits:**
- ✅ Consistent format everywhere
- ✅ Clients know what to expect
- ✅ Easy error handling in frontend

---

## 4️⃣ Profiles - Use ProfileService

### Create Profiles (Old Way - 30+ lines)
```python
# Create athlete profile if needed
if 'athlete' in roles:
    athlete_profile = db.create_athlete_profile(...)
    profile_data['athlete_profile'] = {...}

# Create coach profile if needed
if 'coach' in roles:
    coach_profile = db.create_coach_profile(...)
    profile_data['coach_profile'] = {...}

# ... repeat for each role ...
```

### Create Profiles (New Way - 1 line!)
```python
from api.profile_service import ProfileService

profile_data = ProfileService.create_profiles_for_roles(
    user_id=user['id'],
    roles=data['roles'],
    data=data
)
```

**Benefits:**
- ✅ 30 lines → 1 line
- ✅ Easy to add new roles
- ✅ No repeated logic

---

## 5️⃣ Schemas - Use for Documentation

### Define Request Schema
```python
from api import schemas

PAYMENT_SCHEMA = {
    'type': 'object',
    'required': ['amount', 'currency'],
    'properties': {
        'amount': {
            'type': 'number',
            'minimum': 0.01,
            'description': 'Payment amount',
            'example': 99.99
        },
        'currency': {
            'type': 'string',
            'enum': ['USD', 'EUR', 'GBP'],
            'description': 'Currency code'
        }
    }
}
```

**Benefits:**
- ✅ Self-documenting
- ✅ Can generate API docs
- ✅ IDE support
- ✅ Client code generation

---

## 6️⃣ Error Codes - Use Predefined Codes

### Available Error Codes
```python
from api.error_handler import ERROR_CODES

# Validation
'MISSING_FIELD'
'INVALID_FORMAT'
'INVALID_EMAIL'
'WEAK_PASSWORD'

# Authentication
'UNAUTHORIZED'
'INVALID_CREDENTIALS'
'INVALID_TOKEN'

# Permission
'FORBIDDEN'
'ACCOUNT_INACTIVE'

# Not Found
'NOT_FOUND'
'USER_NOT_FOUND'

# Conflict
'CONFLICT'
'EMAIL_ALREADY_REGISTERED'

# Server
'INTERNAL_ERROR'
'DATABASE_ERROR'
```

### Use in Endpoint
```python
@handle_errors
def my_endpoint():
    raise APIError('EMAIL_ALREADY_REGISTERED', 
        details={'email': user_email})
```

**Benefits:**
- ✅ Consistent error codes
- ✅ Client can handle programmatically
- ✅ Frontend knows how to respond

---

## Common Patterns

### Pattern 1: Add New Endpoint (5 minutes)
```python
from api.error_handler import handle_errors, error_response, success_response, APIError
from api.validators import FieldValidator

@app.route('/api/my/endpoint', methods=['POST'])
@handle_errors
def my_endpoint():
    data = request.get_json()
    
    # Validate
    is_valid, error = FieldValidator.string_field(data.get('name'), 'name')
    if not is_valid:
        return error_response('INVALID_FORMAT', errors=[error])
    
    # Business logic
    result = db.do_something(data)
    
    # Return
    return success_response({'id': result['id']}, status=201)
```

### Pattern 2: Add New Validator (2 minutes)
```python
# In validators.py
class MyValidator:
    @staticmethod
    def validate(data):
        errors = []
        is_valid, error = FieldValidator.email(data.get('email'))
        if not is_valid:
            errors.append(error)
        # ... more validations ...
        return len(errors) == 0, errors

# In endpoint.py
is_valid, errors = MyValidator.validate(data)
if not is_valid:
    return error_response('INVALID_FORMAT', errors=errors)
```

### Pattern 3: Add New Error Type (1 minute)
```python
# In error_handler.py
ERROR_CODES = {
    # ... existing codes ...
    'MY_ERROR': (400, 'My error message'),
}

# In endpoint.py
raise APIError('MY_ERROR', details={'field': 'value'})
```

---

## Testing Guide

### Test Success Response
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@moove.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "roles": ["athlete"],
    "sport_id": "football"
  }'

# Expected:
# {
#   "success": true,
#   "data": {...},
#   "message": "User registered successfully",
#   "timestamp": "..."
# }
```

### Test Validation Error
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid"}'

# Expected:
# {
#   "success": false,
#   "error_code": "INVALID_FORMAT",
#   "message": "4 validation error(s)",
#   "details": {
#     "errors": [
#       "email: Invalid format (must be valid email address)",
#       "password: Required field",
#       ...
#     ]
#   },
#   "timestamp": "..."
# }
```

### Test Error Handling
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@moove.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "roles": ["athlete"],
    "sport_id": "football"
  }'

# Register again with same email
# Expected:
# {
#   "success": false,
#   "error_code": "EMAIL_ALREADY_REGISTERED",
#   "message": "Email is already registered",
#   "timestamp": "..."
# }
```

---

## Migration Checklist

If you're updating existing endpoints:

- [ ] Add `@handle_errors` decorator
- [ ] Replace try/except blocks with `APIError` raises
- [ ] Replace `return jsonify({'error': ...})` with `error_response(...)`
- [ ] Replace `return jsonify({'success': True, ...})` with `success_response(...)`
- [ ] Extract validation to validator class if needed
- [ ] Remove `traceback.format_exc()` from responses
- [ ] Remove `print()` statements (use logging instead)
- [ ] Test all error cases
- [ ] Update API documentation

---

## Module Map

```
Import Error Handling:
  from api.error_handler import (
    handle_errors,          # Decorator
    error_response,         # Function
    success_response,       # Function
    APIError,              # Exception class
  )

Import Validators:
  from api.validators import (
    FieldValidator,        # Reusable fields
    RegistrationValidator, # Full registration
    LoginValidator,        # Login
  )

Import Services:
  from api.profile_service import ProfileService

Import Schemas:
  from api.schemas import (
    REGISTER_SCHEMA,
    LOGIN_SCHEMA,
  )
```

---

## Performance

All improvements are **zero-overhead**:
- ✅ No additional database calls
- ✅ No additional network requests
- ✅ No performance degradation
- ✅ Actually *faster* due to reduced code

---

## Questions?

Check the documentation files:
- `API_USABILITY_AUDIT.md` - Detailed issues found
- `API_USABILITY_FIXES_IMPLEMENTATION.md` - Full code examples
- `API_FIXES_COMPLETE.md` - Implementation summary

---

**You're ready to build awesome features!** 🚀
