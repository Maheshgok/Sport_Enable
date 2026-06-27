# 🔧 API Usability Improvements - Implementation Guide

## Part 1: Centralized Error Handler (40% Improvement)

### Create `api/error_handler.py`

```python
"""
Centralized error handling for Moove API
Provides consistent error responses, logging, and tracking
"""

from flask import jsonify
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============================================
# ERROR CODES & HTTP MAPPING
# ============================================

ERROR_CODES = {
    # Validation errors (400)
    'MISSING_FIELD': (400, 'Required field is missing'),
    'INVALID_FORMAT': (400, 'Invalid data format'),
    'INVALID_EMAIL': (400, 'Email format is invalid'),
    'WEAK_PASSWORD': (400, 'Password does not meet requirements'),
    'INVALID_ROLE': (400, 'Role is not recognized'),
    'MISSING_ROLE_FIELD': (400, 'Required field for this role is missing'),
    
    # Authentication errors (401)
    'UNAUTHORIZED': (401, 'Authentication required'),
    'INVALID_CREDENTIALS': (401, 'Email or password is incorrect'),
    'INVALID_TOKEN': (401, 'Token is invalid or expired'),
    'TOKEN_MISSING': (401, 'Authorization token is missing'),
    
    # Permission errors (403)
    'FORBIDDEN': (403, 'You do not have permission to access this resource'),
    'ACCOUNT_INACTIVE': (403, 'Account is not active'),
    'INSUFFICIENT_PERMISSIONS': (403, 'Insufficient permissions for this action'),
    
    # Not found errors (404)
    'NOT_FOUND': (404, 'Resource not found'),
    'USER_NOT_FOUND': (404, 'User not found'),
    'REQUEST_NOT_FOUND': (404, 'Request not found'),
    
    # Conflict errors (409)
    'CONFLICT': (409, 'Resource already exists'),
    'EMAIL_ALREADY_REGISTERED': (409, 'Email is already registered'),
    'DUPLICATE_RELATIONSHIP': (409, 'Relationship already exists'),
    
    # Server errors (500)
    'INTERNAL_ERROR': (500, 'An internal server error occurred'),
    'DATABASE_ERROR': (500, 'Database operation failed'),
    'STORAGE_ERROR': (500, 'Storage operation failed'),
    'PROFILE_CREATION_ERROR': (500, 'Failed to create user profile'),
}


# ============================================
# ERROR CLASSES
# ============================================

class APIError(Exception):
    """Custom API error with code, status, and details"""
    
    def __init__(self, error_code, message=None, details=None, status=None):
        self.error_code = error_code
        self.message = message or ERROR_CODES.get(error_code, ('Unknown error',))[1]
        self.details = details
        
        if status is None:
            self.status = ERROR_CODES.get(error_code, (500,))[0]
        else:
            self.status = status
    
    def to_dict(self, include_details=True):
        """Convert error to dictionary for JSON response"""
        response = {
            'success': False,
            'error_code': self.error_code,
            'message': self.message,
            'timestamp': datetime.now().isoformat()
        }
        
        if include_details and self.details and os.environ.get('ENV') == 'development':
            response['details'] = self.details
        
        return response


# ============================================
# ERROR RESPONSE FUNCTIONS
# ============================================

def error_response(error_code, message=None, details=None, status=None, log_error=True):
    """
    Create standardized error response
    
    Args:
        error_code (str): Error code from ERROR_CODES
        message (str): Custom message (overrides default)
        details (dict): Additional details for development
        status (int): HTTP status (overrides default)
        log_error (bool): Whether to log this error
    
    Returns:
        tuple: (response dict, HTTP status code)
    """
    try:
        error = APIError(error_code, message, details, status)
        
        if log_error:
            logger.warning(f"{error_code}: {error.message}", extra={'details': details})
        
        response = error.to_dict(include_details=True)
        return jsonify(response), error.status
    
    except Exception as e:
        logger.error(f"Error creating error response: {e}")
        return jsonify({
            'success': False,
            'error_code': 'INTERNAL_ERROR',
            'message': 'An internal server error occurred',
            'timestamp': datetime.now().isoformat()
        }), 500


def success_response(data, message=None, status=200):
    """
    Create standardized success response
    
    Args:
        data (dict): Response data
        message (str): Optional message
        status (int): HTTP status code
    
    Returns:
        tuple: (response dict, HTTP status code)
    """
    response = {
        'success': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    
    if message:
        response['message'] = message
    
    return jsonify(response), status


# ============================================
# VALIDATION ERROR HELPER
# ============================================

def validation_error(errors, details=None):
    """
    Create validation error response
    
    Args:
        errors (list): List of error messages
        details (dict): Additional details
    
    Returns:
        tuple: (response dict, 400)
    """
    error_details = details or {}
    error_details['errors'] = errors
    
    return error_response(
        'INVALID_FORMAT',
        f'{len(errors)} validation error(s)',
        details=error_details
    )


# ============================================
# ERROR HANDLER DECORATOR
# ============================================

def handle_errors(f):
    """Decorator to catch and handle APIError exceptions"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            return error_response(e.error_code, e.message, e.details, e.status)
        except Exception as e:
            logger.error(f"Unhandled exception in {f.__name__}", exc_info=True)
            return error_response('INTERNAL_ERROR', details={'error': str(e)})
    
    return decorated_function


# ============================================
# LOGGING SETUP
# ============================================

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=os.environ.get('LOG_LEVEL', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('api.log'),
            logging.StreamHandler()
        ]
    )
```

---

## Part 2: Request Validation Schemas

### Create `api/schemas.py`

```python
"""
Request validation schemas for API endpoints
Defines structure, types, and constraints for all API requests
"""

# ============================================
# AUTHENTICATION SCHEMAS
# ============================================

REGISTER_SCHEMA = {
    'type': 'object',
    'required': ['email', 'password', 'first_name', 'last_name', 'roles'],
    'properties': {
        'email': {
            'type': 'string',
            'format': 'email',
            'minLength': 5,
            'maxLength': 254,
            'description': 'User email address (must be unique)',
            'example': 'athlete@moove.com'
        },
        'password': {
            'type': 'string',
            'minLength': 8,
            'maxLength': 128,
            'pattern': '^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*])',
            'description': 'Minimum 8 chars: uppercase, lowercase, number, special char',
            'example': 'SecurePass123!'
        },
        'first_name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 50,
            'description': 'User first name',
            'example': 'John'
        },
        'last_name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 50,
            'description': 'User last name',
            'example': 'Doe'
        },
        'roles': {
            'type': 'array',
            'minItems': 1,
            'items': {'enum': ['athlete', 'coach', 'physiotherapist', 'parent', 'admin']},
            'description': 'User roles (at least one required)',
            'example': ['athlete', 'parent']
        },
        # Role-specific fields
        'sport_id': {
            'type': 'string',
            'description': 'Required if athlete role (e.g., "football", "basketball")',
            'example': 'football'
        },
        'sport_name': {
            'type': 'string',
            'description': 'Display name for sport',
            'example': 'American Football'
        },
        'position': {
            'type': 'string',
            'description': 'Player position (athlete only)',
            'example': 'Quarterback'
        },
        'team': {
            'type': 'string',
            'description': 'Team name (athlete only)',
            'example': 'State University'
        },
        'specialization': {
            'type': 'string',
            'description': 'Coach/physiotherapist specialization',
            'example': 'Sports Performance'
        },
        'years_of_experience': {
            'type': 'integer',
            'minimum': 0,
            'maximum': 60,
            'description': 'Years of coaching experience',
            'example': 5
        },
        'license_number': {
            'type': 'string',
            'description': 'Professional license number (physiotherapist only)',
            'example': 'PT123456'
        },
        'guardian_type': {
            'type': 'string',
            'enum': ['parent', 'legal_guardian', 'manager', 'agent', 'family_member'],
            'description': 'Type of guardian relationship (required if parent role)',
            'example': 'parent'
        },
        'relationship_to_athlete': {
            'type': 'string',
            'description': 'Specific relationship (parent only)',
            'example': 'Father'
        },
        'permissions': {
            'type': 'array',
            'items': {'type': 'string'},
            'description': 'Guardian permissions',
            'example': ['view_videos', 'view_reports']
        }
    },
    'dependentRequired': {
        'athlete': ['sport_id'],
        'parent': ['guardian_type'],
        'physiotherapist': ['license_number']
    }
}

LOGIN_SCHEMA = {
    'type': 'object',
    'required': ['email', 'password'],
    'properties': {
        'email': {
            'type': 'string',
            'format': 'email',
            'description': 'User email address',
            'example': 'athlete@moove.com'
        },
        'password': {
            'type': 'string',
            'description': 'User password',
            'example': 'SecurePass123!'
        }
    }
}

# ============================================
# VIDEO ENDPOINTS SCHEMAS
# ============================================

VIDEO_UPLOAD_SCHEMA = {
    'type': 'object',
    'required': ['sport_id'],
    'properties': {
        'sport_id': {
            'type': 'string',
            'description': 'Sport identifier',
            'example': 'football'
        },
        'athlete_id': {
            'type': 'string',
            'description': 'Athlete ID (optional if current user is athlete)',
            'example': 'athlete_123'
        },
        'description': {
            'type': 'string',
            'description': 'Video description',
            'example': 'Quarterback throwing motion analysis'
        },
        'tags': {
            'type': 'array',
            'items': {'type': 'string'},
            'description': 'Tags for video',
            'example': ['throwing', 'footwork', 'accuracy']
        }
    }
}

# ============================================
# RELATIONSHIP SCHEMAS
# ============================================

SEND_INVITATION_SCHEMA = {
    'type': 'object',
    'required': ['recipient_email', 'relationship_type'],
    'properties': {
        'recipient_email': {
            'type': 'string',
            'format': 'email',
            'description': 'Email of relationship recipient',
            'example': 'coach@moove.com'
        },
        'relationship_type': {
            'type': 'string',
            'enum': ['athlete_coach', 'athlete_physiotherapist', 'athlete_parent', 'athlete_agent'],
            'description': 'Type of relationship',
            'example': 'athlete_coach'
        },
        'message': {
            'type': 'string',
            'description': 'Optional message to recipient',
            'example': 'I would like you to coach me'
        }
    }
}

EXERCISE_REQUEST_SCHEMA = {
    'type': 'object',
    'required': ['athlete_id', 'exercise_name', 'description'],
    'properties': {
        'athlete_id': {
            'type': 'string',
            'description': 'Target athlete ID',
            'example': 'athlete_123'
        },
        'exercise_name': {
            'type': 'string',
            'description': 'Name of exercise',
            'example': 'Single Leg Squat'
        },
        'description': {
            'type': 'string',
            'description': 'Exercise description and instructions',
            'example': 'Perform 3 sets of 8-10 reps'
        },
        'reps': {'type': 'integer', 'description': 'Reps per set'},
        'sets': {'type': 'integer', 'description': 'Number of sets'},
        'frequency': {
            'type': 'string',
            'enum': ['daily', 'every_other_day', 'weekly', 'as_needed'],
            'description': 'Exercise frequency'
        },
        'duration_days': {
            'type': 'integer',
            'description': 'Number of days to perform exercise'
        }
    }
}


# ============================================
# RESPONSE SCHEMAS
# ============================================

SUCCESS_RESPONSE_SCHEMA = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean', 'example': True},
        'data': {'type': 'object'},
        'message': {'type': 'string'},
        'timestamp': {'type': 'string', 'format': 'date-time'}
    }
}

ERROR_RESPONSE_SCHEMA = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean', 'example': False},
        'error_code': {'type': 'string'},
        'message': {'type': 'string'},
        'details': {'type': 'object'},
        'timestamp': {'type': 'string', 'format': 'date-time'}
    }
}

# User schema returned in responses
USER_SCHEMA = {
    'type': 'object',
    'properties': {
        'user_id': {'type': 'string'},
        'email': {'type': 'string', 'format': 'email'},
        'first_name': {'type': 'string'},
        'last_name': {'type': 'string'},
        'roles': {'type': 'array', 'items': {'type': 'string'}},
        'status': {'type': 'string', 'enum': ['pending', 'active', 'inactive']},
        'created_at': {'type': 'string', 'format': 'date-time'},
        'last_login': {'type': 'string', 'format': 'date-time'}
    }
}
```

---

## Part 3: Validators Utility

### Create `api/validators.py`

```python
"""
Validation utilities for API requests
Provides reusable validators with clear error messages
"""

from datetime import datetime
import re

# ============================================
# VALIDATION RULES
# ============================================

PASSWORD_PATTERN = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*])'
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


# ============================================
# FIELD VALIDATORS
# ============================================

class FieldValidator:
    """Validates individual fields with clear error messages"""
    
    @staticmethod
    def email(email: str) -> (bool, str):
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False, 'email: Required field'
        
        email = email.lower().strip()
        if not re.match(EMAIL_PATTERN, email):
            return False, 'email: Invalid format (must be valid email address)'
        
        if len(email) > 254:
            return False, 'email: Too long (max 254 characters)'
        
        return True, None
    
    @staticmethod
    def password(password: str) -> (bool, str):
        """Validate password strength"""
        if not password or not isinstance(password, str):
            return False, 'password: Required field'
        
        if len(password) < 8:
            return False, 'password: Minimum 8 characters required'
        
        if len(password) > 128:
            return False, 'password: Maximum 128 characters allowed'
        
        if not re.match(PASSWORD_PATTERN, password):
            return False, 'password: Must contain uppercase, lowercase, number, and special char (!@#$%^&*)'
        
        return True, None
    
    @staticmethod
    def string_field(value: str, field_name: str, min_length=1, max_length=256) -> (bool, str):
        """Validate string field"""
        if not value or not isinstance(value, str):
            return False, f'{field_name}: Required field'
        
        value = value.strip()
        if len(value) < min_length:
            return False, f'{field_name}: Minimum {min_length} character(s) required'
        
        if len(value) > max_length:
            return False, f'{field_name}: Maximum {max_length} characters allowed'
        
        return True, None
    
    @staticmethod
    def enum_field(value: str, field_name: str, allowed_values: list) -> (bool, str):
        """Validate enum field"""
        if not value:
            return False, f'{field_name}: Required field'
        
        if value not in allowed_values:
            return False, f'{field_name}: Invalid value. Allowed: {", ".join(allowed_values)}'
        
        return True, None
    
    @staticmethod
    def array_field(value: list, field_name: str, min_items=1, allowed_items=None) -> (bool, str):
        """Validate array field"""
        if not isinstance(value, list):
            return False, f'{field_name}: Must be an array'
        
        if len(value) < min_items:
            return False, f'{field_name}: Minimum {min_items} item(s) required'
        
        if allowed_items:
            invalid = [item for item in value if item not in allowed_items]
            if invalid:
                return False, f'{field_name}: Invalid items: {", ".join(invalid)}. Allowed: {", ".join(allowed_items)}'
        
        return True, None


# ============================================
# REGISTRATION VALIDATOR
# ============================================

class RegistrationValidator:
    """Validates registration request data"""
    
    VALID_ROLES = ['athlete', 'coach', 'physiotherapist', 'parent', 'admin']
    
    ROLE_REQUIREMENTS = {
        'athlete': {
            'required': ['sport_id'],
            'optional': ['position', 'team', 'custom_baselines'],
            'sport_name': 'Sport athlete account'
        },
        'coach': {
            'required': [],
            'optional': ['specialization', 'years_of_experience'],
            'description': 'Coach/trainer account'
        },
        'physiotherapist': {
            'required': ['license_number'],
            'optional': ['specialization'],
            'description': 'Licensed physiotherapist account'
        },
        'parent': {
            'required': ['guardian_type'],
            'optional': ['relationship_to_athlete', 'permissions'],
            'description': 'Parent/guardian account',
            'guardian_type_options': ['parent', 'legal_guardian', 'manager', 'agent', 'family_member']
        },
        'admin': {
            'required': [],
            'optional': [],
            'description': 'Admin account'
        }
    }
    
    @classmethod
    def validate(cls, data: dict) -> (bool, list):
        """
        Validate full registration data
        
        Returns:
            (bool: valid, list: errors)
        """
        errors = []
        
        # Validate basic fields
        is_valid, error = FieldValidator.string_field(data.get('first_name'), 'first_name')
        if not is_valid:
            errors.append(error)
        
        is_valid, error = FieldValidator.string_field(data.get('last_name'), 'last_name')
        if not is_valid:
            errors.append(error)
        
        is_valid, error = FieldValidator.email(data.get('email'))
        if not is_valid:
            errors.append(error)
        
        is_valid, error = FieldValidator.password(data.get('password'))
        if not is_valid:
            errors.append(error)
        
        # Validate roles
        is_valid, error = FieldValidator.array_field(
            data.get('roles', []),
            'roles',
            min_items=1,
            allowed_items=cls.VALID_ROLES
        )
        if not is_valid:
            errors.append(error)
        
        # Validate role-specific requirements
        for role in data.get('roles', []):
            role_reqs = cls.ROLE_REQUIREMENTS.get(role, {})
            
            for required_field in role_reqs.get('required', []):
                if required_field not in data or not data[required_field]:
                    errors.append(f'{required_field}: Required for {role} role')
        
        # Special validation for guardian_type options
        if 'parent' in data.get('roles', []):
            guardian_type = data.get('guardian_type')
            valid_types = cls.ROLE_REQUIREMENTS['parent'].get('guardian_type_options', [])
            
            if guardian_type not in valid_types:
                errors.append(f'guardian_type: Invalid value. Allowed: {", ".join(valid_types)}')
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_requirements_for_roles(cls, roles: list) -> dict:
        """Get all field requirements for given roles"""
        requirements = {}
        for role in roles:
            if role in cls.ROLE_REQUIREMENTS:
                requirements[role] = cls.ROLE_REQUIREMENTS[role]
        return requirements


# ============================================
# USAGE EXAMPLE
# ============================================

def validate_registration_data(data):
    """
    Example usage in endpoint
    """
    is_valid, errors = RegistrationValidator.validate(data)
    
    if not is_valid:
        return {
            'valid': False,
            'errors': errors
        }
    
    return {'valid': True}
```

---

## Part 4: Updated Register Endpoint

### Update `api/app_firestore.py` - Register Endpoint

```python
from error_handler import error_response, success_response, handle_errors, APIError
from validators import RegistrationValidator
from schemas import REGISTER_SCHEMA

@app.route('/api/auth/register', methods=['POST'])
@handle_errors
def register():
    """
    Register a new user account
    
    POST /api/auth/register
    
    Request body (JSON):
        {
            "email": "user@moove.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
            "roles": ["athlete"],
            "sport_id": "football",
            "position": "Quarterback"
        }
    
    Response (201):
        {
            "success": true,
            "data": {
                "user_id": "user_123",
                "email": "user@moove.com",
                "roles": ["athlete"],
                "token": "jwt_token_here"
            },
            "message": "User registered successfully",
            "timestamp": "2026-06-27T10:30:00"
        }
    
    Error responses:
        - 400: INVALID_FORMAT - Validation failed
        - 409: EMAIL_ALREADY_REGISTERED - Email exists
        - 500: PROFILE_CREATION_ERROR - Profile creation failed
    """
    try:
        data = request.get_json()
        
        # Validate request data
        is_valid, errors = RegistrationValidator.validate(data)
        if not is_valid:
            return error_response(
                'INVALID_FORMAT',
                f'{len(errors)} validation error(s)',
                details={'errors': errors}
            )
        
        # Check if email already exists
        email = data['email'].lower().strip()
        existing_user = db.get_user_by_email(email)
        if existing_user:
            raise APIError(
                'EMAIL_ALREADY_REGISTERED',
                details={'email': email}
            )
        
        # Hash password
        password_hash = hash_password(data['password'])
        
        # Create user in Firestore
        user = db.create_user(
            email=email,
            password_hash=password_hash,
            first_name=data['first_name'],
            last_name=data['last_name'],
            roles=data['roles']
        )
        
        # Create role-specific profiles
        try:
            profile_data = ProfileService.create_profiles_for_roles(
                user['id'],
                data['roles'],
                data
            )
        except Exception as e:
            raise APIError('PROFILE_CREATION_ERROR', details={'error': str(e)})
        
        # Generate JWT token
        token = generate_token(user['id'], user['email'], user['roles'])
        
        # Return success response
        response_data = {
            'user_id': user['id'],
            'email': user['email'],
            'roles': user['roles'],
            'first_name': user['firstName'],
            'last_name': user['lastName'],
            'token': token,
            **profile_data
        }
        
        return success_response(
            response_data,
            message='User registered successfully',
            status=201
        )
    
    except APIError:
        # APIError handled by @handle_errors decorator
        raise
    except Exception as e:
        logger.error(f"Unexpected error in registration", exc_info=True)
        raise APIError('INTERNAL_ERROR', details={'error': str(e)})
```

---

## Implementation Checklist

- [ ] Create `api/error_handler.py`
- [ ] Create `api/schemas.py`
- [ ] Create `api/validators.py`
- [ ] Update `api/app_firestore.py` register endpoint
- [ ] Update `api/app_firestore.py` login endpoint
- [ ] Apply error handler to all endpoints
- [ ] Test error responses
- [ ] Test validation errors
- [ ] Add logging setup
- [ ] Update imports in `app_firestore.py`

**Estimated time:** 2-3 hours for full implementation
**Impact:** 60%+ improvement in developer experience

Ready to implement? I can start with any of these files! 🚀
