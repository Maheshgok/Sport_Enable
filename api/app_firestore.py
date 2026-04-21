"""
Flask API for Moove Platform
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

from video_annotation_tool import VideoAnnotationTool

# Import API modules with error handling
try:
    import auth
    import firestore_db as db
    import relationships_firestore as relationships
    import physio_requests
except ImportError as e:
    print(f"Import error: {e}")
    # Try importing with api. prefix
    from api import auth
    from api import firestore_db as db
    from api import relationships_firestore as relationships
    from api import physio_requests

# Import auth functions
hash_password = auth.hash_password
verify_password = auth.verify_password
generate_token = auth.generate_token
require_auth = auth.require_auth
is_super_user = auth.is_super_user

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
def register():
    """
    Register a new user
    
    Required fields:
        - email, password, first_name, last_name
        - roles: array of roles (athlete, coach, physiotherapist, parent)
    
    Role-specific required fields:
        - athlete: sport_id
        - parent: guardian_type
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'roles']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate email format
        email = data['email'].lower().strip()
        if '@' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        password = data['password']
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Validate roles
        valid_roles = ['athlete', 'physiotherapist', 'coach', 'parent', 'admin']
        roles = data['roles']
        if not isinstance(roles, list) or len(roles) == 0:
            return jsonify({'error': 'At least one role is required'}), 400
        
        for role in roles:
            if role not in valid_roles:
                return jsonify({'error': f'Invalid role: {role}. Valid roles: {", ".join(valid_roles)}'}), 400
        
        # Validate role-specific requirements
        if 'athlete' in roles and 'sport_id' not in data:
            return jsonify({'error': 'sport_id is required for athletes'}), 400
        
        if 'parent' in roles and 'guardian_type' not in data:
            return jsonify({'error': 'guardian_type is required for parents/guardians (parent, legal_guardian, manager, agent, family_member)'}), 400
        
        # Check if email already exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user in Firestore
        user = db.create_user(
            email=email,
            password_hash=password_hash,
            first_name=data['first_name'],
            last_name=data['last_name'],
            roles=roles
        )
        
        # Create role-specific profiles
        profile_data = {}
        
        # Create athlete profile if needed
        if 'athlete' in roles:
            athlete_profile = db.create_athlete_profile(
                user_id=user['id'],
                sport_id=data['sport_id'],
                sport_name=data.get('sport_name', data['sport_id']),
                position=data.get('position'),
                team=data.get('team'),
                custom_baselines=data.get('custom_baselines')
            )
            profile_data['athlete_profile'] = {
                'sport_id': data['sport_id'],
                'position': data.get('position')
            }
        
        # Create coach profile if needed
        if 'coach' in roles:
            coach_profile = db.create_coach_profile(
                user_id=user['id'],
                specialization=data.get('specialization'),
                years_of_experience=data.get('years_of_experience')
            )
            profile_data['coach_profile'] = {
                'specialization': data.get('specialization')
            }
        
        # Create physiotherapist profile if needed
        if 'physiotherapist' in roles:
            physio_profile = db.create_physiotherapist_profile(
                user_id=user['id'],
                specialization=data.get('specialization'),
                license_number=data.get('license_number')
            )
            profile_data['physiotherapist_profile'] = {
                'license_number': data.get('license_number')
            }
        
        # Create parent/guardian profile if needed
        if 'parent' in roles:
            guardian_profile = db.create_parent_guardian_profile(
                user_id=user['id'],
                guardian_type=data['guardian_type'],
                relationship_to_athlete=data.get('relationship_to_athlete'),
                permissions=data.get('permissions')
            )
            profile_data['guardian_profile'] = {
                'guardian_type': data['guardian_type'],
                'relationship_to_athlete': data.get('relationship_to_athlete')
            }
        
        # Generate JWT token
        token = generate_token(user['id'], user['email'], user['roles'])
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'user_id': user['id'],
                'email': user['email'],
                'roles': user['roles'],
                'first_name': user['firstName'],
                'last_name': user['lastName'],
                **profile_data  # Include any created profiles
            }
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login user
    
    Required fields:
        - email, password
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Get user from Firestore
        user = db.get_user_by_email(email)
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not verify_password(password, user['passwordHash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if account is active
        if user.get('status') != 'active':
            return jsonify({'error': 'Account is not active'}), 403
        
        # Update last login timestamp
        db.update_last_login(user['id'])
        
        # Generate JWT token
        token = generate_token(user['id'], user['email'], user['roles'])
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'user_id': user['id'],
                'email': user['email'],
                'roles': user['roles'],
                'first_name': user.get('firstName'),
                'last_name': user.get('lastName')
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@require_auth()
def get_current_user():
    """Get current user profile"""
    try:
        current_user = request.current_user
        user = db.get_user_by_id(current_user['user_id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get role-specific profiles
        profiles = {}
        
        if 'athlete' in user['roles']:
            athlete_profile = db.get_athlete_profile(user['id'])
            if athlete_profile:
                profiles['athlete_profile'] = athlete_profile
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user['id'],
                'email': user['email'],
                'roles': user['roles'],
                'first_name': user.get('firstName'),
                'last_name': user.get('lastName'),
                'status': user.get('status'),
                **profiles
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting user: {e}")
        return jsonify({'error': str(e)}), 500

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
