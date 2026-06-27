"""
Validation utilities for API requests
Provides reusable validators with clear error messages
"""

from datetime import datetime
import re
from typing import Tuple, List, Dict, Optional

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
    def email(email: str) -> Tuple[bool, Optional[str]]:
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
    def password(password: str) -> Tuple[bool, Optional[str]]:
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
    def string_field(value: str, field_name: str, min_length: int = 1, max_length: int = 256) -> Tuple[bool, Optional[str]]:
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
    def enum_field(value: str, field_name: str, allowed_values: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate enum field"""
        if not value:
            return False, f'{field_name}: Required field'
        
        if value not in allowed_values:
            return False, f'{field_name}: Invalid value. Allowed: {", ".join(allowed_values)}'
        
        return True, None
    
    @staticmethod
    def array_field(value: list, field_name: str, min_items: int = 1, allowed_items: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
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
            'description': 'Sport athlete account'
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
    def validate(cls, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate full registration data
        
        Args:
            data: Registration data dictionary
        
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
            
            if guardian_type and guardian_type not in valid_types:
                errors.append(f'guardian_type: Invalid value. Allowed: {", ".join(valid_types)}')
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_requirements_for_roles(cls, roles: List[str]) -> Dict:
        """Get all field requirements for given roles"""
        requirements = {}
        for role in roles:
            if role in cls.ROLE_REQUIREMENTS:
                requirements[role] = cls.ROLE_REQUIREMENTS[role]
        return requirements


# ============================================
# LOGIN VALIDATOR
# ============================================

class LoginValidator:
    """Validates login request data"""
    
    @staticmethod
    def validate(data: Dict) -> Tuple[bool, List[str]]:
        """Validate login data"""
        errors = []
        
        is_valid, error = FieldValidator.email(data.get('email'))
        if not is_valid:
            errors.append(error)
        
        if not data.get('password'):
            errors.append('password: Required field')
        
        return len(errors) == 0, errors
