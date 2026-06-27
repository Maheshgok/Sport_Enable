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
