"""
Centralized error handling for Moove API
Provides consistent error responses, logging, and tracking
"""

from flask import jsonify
import os
from datetime import datetime
import logging
from functools import wraps

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
