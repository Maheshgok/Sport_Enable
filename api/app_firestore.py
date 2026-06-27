"""
Flask API for Moove Platformsuch other
Provides REST endpoints for video processing, authentication, and relationship management
Uses Firebase/Firestore for data storage (serverless deployment)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from google.cloud import storage
import os
import sys
import uuid
import shutil
from datetime import datetime, timedelta
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory and parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Import API modules - use absolute imports
from api import auth
from api import firestore_db as db
from api import relationships_firestore as relationships
from api import physio_requests
from api.v1_routes_flask import register_protocol_routes

# Import error handling and validation modules
from api.error_handler import error_response, success_response, handle_errors, APIError, setup_logging
from api.validators import RegistrationValidator, LoginValidator
from api.profile_service import ProfileService
from api.schemas import REGISTER_SCHEMA, LOGIN_SCHEMA

# Import auth functions
hash_password = auth.hash_password
verify_password = auth.verify_password
generate_token = auth.generate_token
require_auth = auth.require_auth
is_super_user = auth.is_super_user

# Setup logging
setup_logging()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'video-analysis-storage')
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_FOLDER = '/tmp/outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize GCS client
storage_client = storage.Client()

# Create local temp folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_bucket():
    """Get or create GCS bucket"""
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        if not bucket.exists():
            bucket = storage_client.create_bucket(BUCKET_NAME, location='asia-south1')
            print(f"Created bucket: {BUCKET_NAME}")
        return bucket
    except Exception as e:
        print(f"Error accessing bucket: {e}")
        return storage_client.bucket(BUCKET_NAME)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================
# Register Sprint 1 & 2 Protocol Routes (v1)
# ============================================
try:
    register_protocol_routes(app, db.db)
    print("✓ Protocol v1 routes registered")
except Exception as e:
    print(f"⚠ Warning: Could not register protocol v1 routes: {e}")
    import traceback
    traceback.print_exc()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    firestore_healthy = db.test_connection()
    return jsonify({
        'status': 'healthy',
        'service': 'moove-api',
        'database': 'firestore',
        'database_status': 'connected' if firestore_healthy else 'disconnected',
        'timestamp': datetime.now().isoformat()
    })

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

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

@app.route('/api/auth/login', methods=['POST'])
@handle_errors
def login():
    """
    Login user
    
    POST /api/auth/login
    
    Request body (JSON):
        {
            "email": "user@moove.com",
            "password": "SecurePass123!"
        }
    
    Response (200):
        {
            "success": true,
            "data": {
                "user_id": "user_123",
                "email": "user@moove.com",
                "roles": ["athlete"],
                "token": "jwt_token_here"
            },
            "timestamp": "2026-06-27T10:30:00"
        }
    
    Error responses:
        - 400: INVALID_FORMAT - Validation failed
        - 401: INVALID_CREDENTIALS - Invalid email/password
        - 403: ACCOUNT_INACTIVE - Account not active
    """
    data = request.get_json()
    
    # Validate request data
    is_valid, errors = LoginValidator.validate(data)
    if not is_valid:
        return error_response(
            'INVALID_FORMAT',
            f'{len(errors)} validation error(s)',
            details={'errors': errors}
        )
    
    email = data['email'].lower().strip()
    password = data['password']
    
    # Get user from Firestore
    user = db.get_user_by_email(email)
    
    if not user:
        raise APIError('INVALID_CREDENTIALS')
    
    # Verify password
    if not verify_password(password, user['passwordHash']):
        raise APIError('INVALID_CREDENTIALS')
    
    # Check if account is active
    if user.get('status') != 'active':
        raise APIError('ACCOUNT_INACTIVE')
    
    # Update last login timestamp
    db.update_last_login(user['id'])
    
    # Generate JWT token
    token = generate_token(user['id'], user['email'], user['roles'])
    
    response_data = {
        'user_id': user['id'],
        'email': user['email'],
        'roles': user['roles'],
        'first_name': user.get('firstName'),
        'last_name': user.get('lastName'),
        'token': token
    }
    
    return success_response(response_data)

@app.route('/api/auth/me', methods=['GET'])
@require_auth()
@handle_errors
def get_current_user():
    """
    Get current user profile
    
    GET /api/auth/me
    
    Headers:
        Authorization: Bearer <token>
    
    Response (200):
        {
            "success": true,
            "data": {
                "user_id": "user_123",
                "email": "user@moove.com",
                "roles": ["athlete"],
                "first_name": "John",
                "last_name": "Doe",
                "status": "active"
            },
            "timestamp": "2026-06-27T10:30:00"
        }
    
    Error responses:
        - 401: UNAUTHORIZED - No valid token
        - 404: USER_NOT_FOUND - User doesn't exist
    """
    current_user = request.current_user
    user = db.get_user_by_id(current_user['user_id'])
    
    if not user:
        raise APIError('USER_NOT_FOUND')
    
    # Get role-specific profiles
    profiles = {}
    
    if 'athlete' in user['roles']:
        athlete_profile = db.get_athlete_profile(user['id'])
        if athlete_profile:
            profiles['athlete_profile'] = athlete_profile
    
    response_data = {
        'user_id': user['id'],
        'email': user['email'],
        'roles': user['roles'],
        'first_name': user.get('firstName'),
        'last_name': user.get('lastName'),
        'status': user.get('status'),
        **profiles
    }
    
    return success_response(response_data)

# ============================================
# RELATIONSHIP MANAGEMENT ENDPOINTS
# ============================================

@app.route('/api/invitations/send', methods=['POST'])
def send_invitation():
    """Send relationship invitation"""
    return relationships.send_invitation()

@app.route('/api/invitations/received', methods=['GET'])
def get_received_invitations():
    """Get invitations received by current user"""
    return relationships.get_received_invitations()

@app.route('/api/invitations/sent', methods=['GET'])
def get_sent_invitations():
    """Get invitations sent by current user"""
    return relationships.get_sent_invitations()

@app.route('/api/invitations/<token>', methods=['GET'])
def get_invitation_details(token):
    """Get public invitation details (no auth required)"""
    return relationships.get_invitation_details(token)

@app.route('/api/invitations/<token>/accept', methods=['POST'])
def accept_invitation(token):
    """Accept an invitation"""
    return relationships.accept_invitation(token)

@app.route('/api/invitations/<token>/reject', methods=['POST'])
def reject_invitation(token):
    """Reject an invitation"""
    return relationships.reject_invitation(token)

@app.route('/api/relationships/mine', methods=['GET'])
def get_my_relationships():
    """Get current user's active relationships"""
    return relationships.get_my_relationships()

# Admin endpoints
@app.route('/api/admin/relationship-requests', methods=['GET'])
def get_pending_requests():
    """Get all pending relationship change requests (admin only)"""
    return relationships.get_pending_requests()

@app.route('/api/admin/relationship-requests/<request_id>/approve', methods=['POST'])
def approve_request(request_id):
    """Approve a relationship change request (admin only)"""
    return relationships.approve_request(request_id)

@app.route('/api/admin/relationship-requests/<request_id>/reject', methods=['POST'])
def reject_relationship_request(request_id):
    """Reject a relationship change request (admin only)"""
    return relationships.reject_request(request_id)

# ============================================
# REQUEST SYSTEM ENDPOINTS (Exercise & Baseline Requests)
# ============================================

# Physiotherapist endpoints
@app.route('/api/physio/request-exercise', methods=['POST'])
def submit_exercise_request():
    """Submit new exercise request"""
    return physio_requests.submit_exercise_request()

@app.route('/api/physio/request-baseline', methods=['POST'])
def submit_baseline_request():
    """Submit new baseline measurement request"""
    return physio_requests.submit_baseline_request()

@app.route('/api/physio/my-requests', methods=['GET'])
def get_my_requests():
    """Get current user's requests"""
    return physio_requests.get_my_requests()

# Admin endpoints
@app.route('/api/admin/requests/pending', methods=['GET'])
def get_all_pending_requests():
    """Get all pending requests (admin only)"""
    return physio_requests.get_all_pending_requests()

@app.route('/api/admin/requests', methods=['GET'])
def get_all_requests_admin():
    """Get all requests with filters (admin only)"""
    return physio_requests.get_all_requests_admin()

@app.route('/api/admin/requests/exercise/<request_id>/approve', methods=['POST'])
def approve_exercise_request(request_id):
    """Approve exercise request (admin only)"""
    return physio_requests.approve_exercise_request(request_id)

@app.route('/api/admin/requests/baseline/<request_id>/approve', methods=['POST'])
def approve_baseline_request(request_id):
    """Approve baseline request (admin only)"""
    return physio_requests.approve_baseline_request(request_id)

@app.route('/api/admin/requests/<request_id>/reject', methods=['POST'])
def reject_admin_request(request_id):
    """Reject a request (admin only)"""
    return physio_requests.reject_request(request_id)

@app.route('/api/requests/<request_id>', methods=['GET'])
def get_request_details(request_id):
    """Get request details"""
    return physio_requests.get_request_details(request_id)

# ============================================
# VIDEO ANALYSIS ENDPOINTS (Existing functionality)
# ============================================

# ... Keep existing video endpoints unchanged ...

# ============================================
# ROOT REDIRECT
# ============================================

@app.route('/')
def root():
    """Root endpoint redirects to frontend"""
    frontend_url = os.environ.get('FRONTEND_URL', 'https://watch-mail-trial.web.app')
    return redirect(frontend_url)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
