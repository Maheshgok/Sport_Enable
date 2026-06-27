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
"""
Firebase Authentication utilities for Moove API
Handles Firebase Auth token verification and user management
"""

import firebase_admin
from firebase_admin import auth, credentials, firestore
from functools import wraps
from flask import request, jsonify
import os

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        # For Cloud Run: Use Application Default Credentials (built-in)
        # For local: Requires GOOGLE_APPLICATION_CREDENTIALS env var
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': os.environ.get('FIREBASE_PROJECT_ID', 'watch-mail-trial')
        })
    except Exception as e:
        # Fallback: Try loading from file or env variables
        cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'service-account-key.json')
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Last resort: Build from environment variables
            cred_dict = {
                "type": "service_account",
                "project_id": os.environ.get('FIREBASE_PROJECT_ID', 'watch-mail-trial'),
                "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
                "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
                "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.environ.get('FIREBASE_CLIENT_EMAIL', '')}"
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def verify_firebase_token(token):
    """
    Verify Firebase Auth token

    Args:
        token: Firebase Auth ID token

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def get_token_from_request():
    """Extract Firebase token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None

    return parts[1]

def require_auth(roles=None):
    """
    Decorator to require Firebase authentication for routes

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
                return jsonify({'error': 'Authorization token required'}), 401

            decoded_token = verify_firebase_token(token)
            if not decoded_token:
                return jsonify({'error': 'Invalid or expired token'}), 401

            # Get user profile from Firestore
            user_id = decoded_token['uid']
            user_doc = db.collection('users').document(user_id).get()

            if not user_doc.exists:
                return jsonify({'error': 'User profile not found'}), 404

            user_data = user_doc.to_dict()
            user_data['user_id'] = user_id

            # Check roles if specified
            if roles:
                user_roles = user_data.get('roles', [])
                if not any(role in user_roles for role in roles):
                    return jsonify({'error': 'Insufficient permissions'}), 403

            # Attach user to request
            request.current_user = user_data

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def is_super_user(roles):
    """Check if user has super user privileges"""
    return 'admin' in roles or 'super_user' in roles

def create_user_profile(user_id, user_data):
    """
    Create user profile in Firestore

    Args:
        user_id: Firebase Auth UID
        user_data: User profile data
    """
    user_ref = db.collection('users').document(user_id)
    user_ref.set({
        'email': user_data.get('email'),
        'first_name': user_data.get('first_name', ''),
        'last_name': user_data.get('last_name', ''),
        'roles': user_data.get('roles', []),
        'phone': user_data.get('phone'),
        'date_of_birth': user_data.get('date_of_birth'),
        'gender': user_data.get('gender'),
        'avatar': user_data.get('avatar'),
        'organization_id': user_data.get('organization_id'),
        'status': 'active',
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP,
        'last_login_at': firestore.SERVER_TIMESTAMP
    })

def update_user_profile(user_id, updates):
    """
    Update user profile in Firestore

    Args:
        user_id: Firebase Auth UID
        updates: Fields to update
    """
    user_ref = db.collection('users').document(user_id)
    updates['updated_at'] = firestore.SERVER_TIMESTAMP
    user_ref.update(updates)

def get_user_profile(user_id):
    """
    Get user profile from Firestore

    Args:
        user_id: Firebase Auth UID

    Returns:
        User profile dict or None
    """
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        data = user_doc.to_dict()
        data['user_id'] = user_id
        return data
    return None

def is_super_user(user_roles):
    """Check if user has super user/admin role"""
    return 'admin' in user_roles or 'super_user' in user_roles
