"""
Authentication utilities for Moove API
Handles JWT tokens, password hashing, and user verification
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import os

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_token(user_id, email, roles):
    """
    Generate a JWT token for a user
    
    Args:
        user_id: User's UUID
        email: User's email
        roles: List of user roles
        
    Returns:
        JWT token string
    """
    payload = {
        'user_id': str(user_id),
        'email': email,
        'roles': roles,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token):
    """
    Decode and verify a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_from_request():
    """Extract JWT token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    return parts[1]

def require_auth(roles=None):
    """
    Decorator to require authentication for routes
    
    Args:
        roles: List of allowed roles (None = any authenticated user)
        
    Usage:
        @app.route('/protected')
        @require_auth()
        def protected_route():
            user = request.current_user
            ...
            
        @app.route('/admin')
        @require_auth(roles=['admin'])
        def admin_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = get_token_from_request()
            if not token:
                return jsonify({'error': 'No authentication token provided'}), 401
            
            payload = decode_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Check role requirements
            if roles:
                user_roles = payload.get('roles', [])
                if not any(role in user_roles for role in roles):
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Attach user info to request
            request.current_user = payload
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def is_super_user(user_roles):
    """Check if user has super user/admin role"""
    return 'admin' in user_roles or 'super_user' in user_roles
