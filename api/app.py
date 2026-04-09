"""
Flask API for Video Annotation Tool  
Provides REST endpoints for video upload and processing
Uses Google Cloud Storage for persistent video and results storage
Includes authentication and user management
"""

from flask import Flask, request, jsonify, redirect
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

# Add parent directory to path to import video_annotation_tool
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from video_annotation_tool import VideoAnnotationTool

# Import authentication and database modules
from auth import hash_password, verify_password, generate_token, require_auth, is_super_user
from db import get_db_cursor, execute_query, test_connection

# Import relationship management
import relationships

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
    db_healthy = test_connection()
    return jsonify({
        'status': 'healthy',
        'service': 'video-annotation-api',
        'database': 'connected' if db_healthy else 'disconnected',
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
        - roles: array of roles (athlete, physiotherapist, coach, caretaker)
    
    Optional fields:
        - phone, date_of_birth, gender, organization_id
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
        valid_roles = ['athlete', 'physiotherapist', 'coach', 'caretaker', 'parent', 'admin', 'super_user']
        roles = data['roles']
        if not isinstance(roles, list) or len(roles) == 0:
            return jsonify({'error': 'At least one role is required'}), 400
        
        for role in roles:
            if role not in valid_roles:
                return jsonify({'error': f'Invalid role: {role}'}), 400
        
        # Validate role-specific requirements
        if 'athlete' in roles:
            if 'sport_id' not in data:
                return jsonify({'error': 'sport_id is required for athletes'}), 400
        
        if 'parent' in roles:
            if 'guardian_type' not in data:
                return jsonify({'error': 'guardian_type is required for parents/guardians'}), 400
        
        # Check if email already exists
        existing_user = execute_query(
            "SELECT user_id FROM physio_app.users WHERE email = %s",
            (email,),
            fetch_one=True
        )
        
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert user into database
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO physio_app.users 
                (email, password_hash, roles, first_name, last_name, phone, date_of_birth, gender, organization_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING user_id, email, roles, first_name, last_name, created_at
            """, (
                email,
                password_hash,
                roles,
                data['first_name'],
                data['last_name'],
                data.get('phone'),
                data.get('date_of_birth'),
                data.get('gender'),
                data.get('organization_id')
            ))
            
            user = cur.fetchone()
        
        # Create role-specific profiles
        profile_data = {}
        
        with get_db_cursor() as cur:
            # Create athlete profile if needed
            if 'athlete' in roles:
                cur.execute("""
                    INSERT INTO physio_app.athlete_profiles
                    (user_id, sport_id, position, custom_baselines)
                    VALUES (%s, %s, %s, %s)
                    RETURNING athlete_id
                """, (
                    user['user_id'],
                    data.get('sport_id'),
                    data.get('position'),
                    data.get('custom_baselines', {})
                ))
                athlete_profile = cur.fetchone()
                profile_data['athlete_profile'] = {
                    'athlete_id': str(athlete_profile['athlete_id']),
                    'sport_id': data.get('sport_id'),
                    'position': data.get('position')
                }
            
            # Create coach profile if needed
            if 'coach' in roles:
                cur.execute("""
                    INSERT INTO physio_app.coach_profiles
                    (user_id, specialization, years_of_experience)
                    VALUES (%s, %s, %s)
                    RETURNING coach_id
                """, (
                    user['user_id'],
                    data.get('specialization'),
                    data.get('years_of_experience', 0)
                ))
                coach_profile = cur.fetchone()
                profile_data['coach_profile'] = {
                    'coach_id': str(coach_profile['coach_id'])
                }
            
            # Create physiotherapist profile if needed
            if 'physiotherapist' in roles:
                cur.execute("""
                    INSERT INTO physio_app.physiotherapist_profiles
                    (user_id, specialization, license_number)
                    VALUES (%s, %s, %s)
                    RETURNING physiotherapist_id
                """, (
                    user['user_id'],
                    data.get('specialization'),
                    data.get('license_number')
                ))
                physio_profile = cur.fetchone()
                profile_data['physiotherapist_profile'] = {
                    'physiotherapist_id': str(physio_profile['physiotherapist_id'])
                }
            
            # Create parent/guardian profile if needed
            if 'parent' in roles:
                cur.execute("""
                    INSERT INTO physio_app.parent_guardian_profiles
                    (user_id, guardian_type, relationship_to_athlete, can_view_medical, can_view_videos, can_view_reports)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING guardian_id
                """, (
                    user['user_id'],
                    data.get('guardian_type', 'parent'),
                    data.get('relationship_to_athlete'),
                    data.get('can_view_medical', False),
                    data.get('can_view_videos', True),
                    data.get('can_view_reports', True)
                ))
                guardian_profile = cur.fetchone()
                profile_data['guardian_profile'] = {
                    'guardian_id': str(guardian_profile['guardian_id']),
                    'guardian_type': data.get('guardian_type'),
                    'relationship_to_athlete': data.get('relationship_to_athlete')
                }
        
        # Generate JWT token
        token = generate_token(user['user_id'], user['email'], user['roles'])
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'user_id': str(user['user_id']),
                'email': user['email'],
                'roles': user['roles'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'created_at': user['created_at'].isoformat(),
                **profile_data  # Include any created profiles
            }
        }), 201
        
    except Exception as e:
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
        
        # Get user from database
        user = execute_query(
            """
            SELECT user_id, email, password_hash, roles, first_name, last_name, 
                   status, avatar, phone, date_of_birth, gender
            FROM physio_app.users 
            WHERE email = %s
            """,
            (email,),
            fetch_one=True
        )
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if account is active
        if user['status'] != 'active':
            return jsonify({'error': f'Account is {user["status"]}'}), 403
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login timestamp
        execute_query(
            "UPDATE physio_app.users SET last_login_at = NOW() WHERE user_id = %s",
            (user['user_id'],)
        )
        
        # Generate JWT token
        token = generate_token(user['user_id'], user['email'], user['roles'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'user_id': str(user['user_id']),
                'email': user['email'],
                'roles': user['roles'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'avatar': user['avatar'],
                'phone': user['phone'],
                'date_of_birth': user['date_of_birth'].isoformat() if user['date_of_birth'] else None,
                'gender': user['gender']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/auth/me', methods=['GET'])
@require_auth()
def get_current_user():
    """Get current authenticated user's information"""
    try:
        current_user = request.current_user
        user_id = current_user['user_id']
        
        # Get full user details
        user = execute_query(
            """
            SELECT user_id, email, roles, first_name, last_name, avatar, 
                   phone, date_of_birth, gender, organization_id, status, 
                   created_at, last_login_at
            FROM physio_app.users 
            WHERE user_id = %s
            """,
            (user_id,),
            fetch_one=True
        )
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': str(user['user_id']),
                'email': user['email'],
                'roles': user['roles'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'avatar': user['avatar'],
                'phone': user['phone'],
                'date_of_birth': user['date_of_birth'].isoformat() if user['date_of_birth'] else None,
                'gender': user['gender'],
                'organization_id': str(user['organization_id']) if user['organization_id'] else None,
                'status': user['status'],
                'created_at': user['created_at'].isoformat(),
                'last_login_at': user['last_login_at'].isoformat() if user['last_login_at'] else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/change-password', methods=['POST'])
@require_auth()
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        current_user = request.current_user
        
        if 'current_password' not in data or 'new_password' not in data:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Validate new password strength
        if len(data['new_password']) < 8:
            return jsonify({'error': 'New password must be at least 8 characters'}), 400
        
        # Get current password hash
        user = execute_query(
            "SELECT password_hash FROM physio_app.users WHERE user_id = %s",
            (current_user['user_id'],),
            fetch_one=True
        )
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not verify_password(data['current_password'], user['password_hash']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        new_password_hash = hash_password(data['new_password'])
        execute_query(
            "UPDATE physio_app.users SET password_hash = %s, updated_at = NOW() WHERE user_id = %s",
            (new_password_hash, current_user['user_id'])
        )
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# USER MANAGEMENT ENDPOINTS (Admin/Super User)
# ============================================

@app.route('/api/users', methods=['GET'])
@require_auth(roles=['admin', 'super_user'])
def list_users():
    """List all users (admin only)"""
    try:
        # Get query parameters
        role = request.args.get('role')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = """
            SELECT user_id, email, roles, first_name, last_name, avatar, 
                   phone, status, created_at, last_login_at
            FROM physio_app.users 
            WHERE 1=1
        """
        params = []
        
        if role:
            query += " AND %s = ANY(roles)"
            params.append(role)
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        users = execute_query(query, tuple(params), fetch_all=True)
        
        # Convert to JSON-serializable format
        users_list = []
        for user in users:
            users_list.append({
                'user_id': str(user['user_id']),
                'email': user['email'],
                'roles': user['roles'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'avatar': user['avatar'],
                'phone': user['phone'],
                'status': user['status'],
                'created_at': user['created_at'].isoformat(),
                'last_login_at': user['last_login_at'].isoformat() if user['last_login_at'] else None
            })
        
        return jsonify({
            'success': True,
            'users': users_list,
            'count': len(users_list),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
@require_auth()
def get_user(user_id):
    """Get user by ID (own profile or admin)"""
    try:
        current_user = request.current_user
        
        # Check permission: own profile or admin
        if str(current_user['user_id']) != user_id and not is_super_user(current_user['roles']):
            return jsonify({'error': 'Unauthorized'}), 403
        
        user = execute_query(
            """
            SELECT user_id, email, roles, first_name, last_name, avatar, 
                   phone, date_of_birth, gender, organization_id, status, 
                   created_at, updated_at, last_login_at
            FROM physio_app.users 
            WHERE user_id = %s
            """,
            (user_id,),
            fetch_one=True
        )
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': str(user['user_id']),
                'email': user['email'],
                'roles': user['roles'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'avatar': user['avatar'],
                'phone': user['phone'],
                'date_of_birth': user['date_of_birth'].isoformat() if user['date_of_birth'] else None,
                'gender': user['gender'],
                'organization_id': str(user['organization_id']) if user['organization_id'] else None,
                'status': user['status'],
                'created_at': user['created_at'].isoformat(),
                'updated_at': user['updated_at'].isoformat() if user['updated_at'] else None,
                'last_login_at': user['last_login_at'].isoformat() if user['last_login_at'] else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['PATCH'])
@require_auth()
def update_user(user_id):
    """Update user information (own profile or admin)"""
    try:
        current_user = request.current_user
        data = request.get_json()
        
        # Check permission: own profile or admin
        if str(current_user['user_id']) != user_id and not is_super_user(current_user['roles']):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Build update query dynamically
        allowed_fields = ['first_name', 'last_name', 'phone', 'date_of_birth', 'gender', 'avatar']
        
        # Only admins can update these fields
        if is_super_user(current_user['roles']):
            allowed_fields.extend(['roles', 'status', 'organization_id'])
        
        update_fields = []
        params = []
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        update_fields.append("updated_at = NOW()")
        params.append(user_id)
        
        query = f"""
            UPDATE physio_app.users 
            SET {', '.join(update_fields)}
            WHERE user_id = %s
            RETURNING user_id, email, roles, first_name, last_name, updated_at
        """
        
        with get_db_cursor() as cur:
            cur.execute(query, tuple(params))
            updated_user = cur.fetchone()
        
        if not updated_user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': {
                'user_id': str(updated_user['user_id']),
                'email': updated_user['email'],
                'roles': updated_user['roles'],
                'first_name': updated_user['first_name'],
                'last_name': updated_user['last_name'],
                'updated_at': updated_user['updated_at'].isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['DELETE'])
@require_auth(roles=['admin', 'super_user'])
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        current_user = request.current_user
        
        # Prevent self-deletion
        if str(current_user['user_id']) == user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        # Delete user (cascade will handle related records)
        with get_db_cursor() as cur:
            cur.execute(
                "DELETE FROM physio_app.users WHERE user_id = %s RETURNING user_id",
                (user_id,)
            )
            deleted = cur.fetchone()
        
        if not deleted:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RELATIONSHIP MANAGEMENT ENDPOINTS
# ============================================

@app.route('/api/invitations/send', methods=['POST'])
@require_auth()
def send_invitation():
    """Send an invitation to establish a relationship"""
    return relationships.send_invitation()

@app.route('/api/invitations/received', methods=['GET'])
@require_auth()
def get_received_invitations():
    """Get invitations received by current user"""
    return relationships.get_received_invitations()

@app.route('/api/invitations/sent', methods=['GET'])
@require_auth()
def get_sent_invitations():
    """Get invitations sent by current user"""
    return relationships.get_sent_invitations()

@app.route('/api/invitations/<token>/accept', methods=['POST'])
@require_auth()
def accept_invitation(token):
    """Accept an invitation"""
    return relationships.accept_invitation(token)

@app.route('/api/invitations/<token>/reject', methods=['POST'])
@require_auth()
def reject_invitation(token):
    """Reject an invitation"""
    return relationships.reject_invitation(token)

@app.route('/api/invitations/<token>/details', methods=['GET'])
def get_invitation_details(token):
    """Get invitation details (public)"""
    return relationships.get_invitation_details(token)

@app.route('/api/relationships/mine', methods=['GET'])
@require_auth()
def get_my_relationships():
    """Get current user's relationships"""
    return relationships.get_my_relationships()

@app.route('/api/relationships/request-change', methods=['POST'])
@require_auth()
def request_relationship_change():
    """Request a relationship change"""
    return relationships.request_relationship_change()

@app.route('/api/admin/relationship-requests', methods=['GET'])
@require_auth(roles=['admin', 'super_user'])
def get_pending_requests():
    """Get pending relationship change requests (admin only)"""
    return relationships.get_pending_requests()

@app.route('/api/admin/relationship-requests/<request_id>/approve', methods=['POST'])
@require_auth(roles=['admin', 'super_user'])
def approve_request(request_id):
    """Approve a relationship change request (admin only)"""
    return relationships.approve_request(request_id)

@app.route('/api/admin/relationship-requests/<request_id>/reject', methods=['POST'])
@require_auth(roles=['admin', 'super_user'])
def reject_request(request_id):
    """Reject a relationship change request (admin only)"""
    return relationships.reject_request(request_id)

# ============================================
# VIDEO ENDPOINTS
# ============================================


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload video(s) and athlete info to Google Cloud Storage"""
    try:
        # Check for required front video
        if 'front_video' not in request.files:
            return jsonify({'error': 'Front view video is required'}), 400
        
        # Get athlete height
        athlete_height = request.form.get('athlete_height')
        if not athlete_height:
            return jsonify({'error': 'Athlete height is required'}), 400
        
        try:
            athlete_height = float(athlete_height)
            if athlete_height <= 0 or athlete_height > 300:
                return jsonify({'error': 'Athlete height must be between 0 and 300 cm'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid athlete height value'}), 400
        
        front_file = request.files['front_video']
        side_file = request.files.get('side_video')  # Optional
        
        if front_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(front_file.filename):
            return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Check side video if provided
        if side_file and side_file.filename != '' and not allowed_file(side_file.filename):
            return jsonify({'error': f'Side video type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        job_id = str(uuid.uuid4())
        bucket = get_bucket()
        
        # Upload front video
        front_filename = secure_filename(front_file.filename)
        front_temp_path = os.path.join(UPLOAD_FOLDER, f'{job_id}_front_{front_filename}')
        front_file.save(front_temp_path)
        
        front_blob = bucket.blob(f'uploads/{job_id}/front_{front_filename}')
        front_blob.upload_from_filename(front_temp_path)
        os.remove(front_temp_path)
        
        uploaded_files = {'front': f'front_{front_filename}'}
        
        # Upload side video if provided
        if side_file and side_file.filename != '':
            side_filename = secure_filename(side_file.filename)
            side_temp_path = os.path.join(UPLOAD_FOLDER, f'{job_id}_side_{side_filename}')
            side_file.save(side_temp_path)
            
            side_blob = bucket.blob(f'uploads/{job_id}/side_{side_filename}')
            side_blob.upload_from_filename(side_temp_path)
            os.remove(side_temp_path)
            
            uploaded_files['side'] = f'side_{side_filename}'
        
        # Store athlete height as metadata
        metadata_blob = bucket.blob(f'uploads/{job_id}/metadata.txt')
        metadata_blob.upload_from_string(f'athlete_height_cm={athlete_height}')
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'files': uploaded_files,
            'athlete_height': athlete_height,
            'message': 'Video(s) uploaded successfully. Use /api/process endpoint to start processing.'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/process/<job_id>', methods=['POST'])
def process_video(job_id):
    """Process video(s) from GCS, upload results back to GCS"""
    try:
        bucket = get_bucket()
        blobs = list(bucket.list_blobs(prefix=f'uploads/{job_id}/'))
        if not blobs:
            return jsonify({'error': 'Job not found'}), 404
        
        # Find metadata and videos
        athlete_height = 50  # Default fallback
        front_video_blob = None
        side_video_blob = None
        
        for blob in blobs:
            filename = blob.name.split('/')[-1]
            if filename == 'metadata.txt':
                metadata = blob.download_as_text()
                for line in metadata.split('\n'):
                    if line.startswith('athlete_height_cm='):
                        athlete_height = float(line.split('=')[1])
            elif filename.startswith('front_'):
                front_video_blob = blob
            elif filename.startswith('side_'):
                side_video_blob = blob
        
        if not front_video_blob:
            return jsonify({'error': 'Front video not found'}), 404
        
        # Download front video
        front_video_path = os.path.join(UPLOAD_FOLDER, f'{job_id}_front.mp4')
        front_video_blob.download_to_filename(front_video_path)
        
        # Download side video if exists
        side_video_path = None
        if side_video_blob:
            side_video_path = os.path.join(UPLOAD_FOLDER, f'{job_id}_side.mp4')
            side_video_blob.download_to_filename(side_video_path)
        
        output_folder = os.path.join(OUTPUT_FOLDER, job_id)
        os.makedirs(output_folder, exist_ok=True)
        
        # Process videos with athlete height
        tool = VideoAnnotationTool()
        timestamp = tool.process_video(
            front_video_path, 
            output_folder,
            athlete_height_cm=athlete_height,
            side_video_path=side_video_path
        )
        analysis = tool.analyze_movements(
            output_folder, 
            timestamp,
            athlete_height_cm=athlete_height
        )
        
        # Save analytics as JSON for API access
        import json
        analytics_data = tool.get_analytics_json()
        analytics_json_path = os.path.join(output_folder, f'analytics_{timestamp}.json')
        with open(analytics_json_path, 'w') as f:
            json.dump(analytics_data, f, indent=2)
        
        # Upload results to GCS
        output_files = []
        for filename in os.listdir(output_folder):
            local_path = os.path.join(output_folder, filename)
            result_blob = bucket.blob(f'results/{job_id}/{filename}')
            result_blob.upload_from_filename(local_path)
            output_files.append(filename)
        
        # Clean up local files
        os.remove(front_video_path)
        if side_video_path and os.path.exists(side_video_path):
            os.remove(side_video_path)
        shutil.rmtree(output_folder)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'timestamp': timestamp,
            'files': output_files,
            'athlete_height': athlete_height,
            'videos_processed': 2 if side_video_path else 1,
            'has_analytics': True,
            'message': 'Video(s) processed successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/results/<job_id>', methods=['GET'])
def get_results(job_id):
    """Get list of result files for a job from GCS"""
    try:
        bucket = get_bucket()
        blobs = list(bucket.list_blobs(prefix=f'results/{job_id}/'))
        if not blobs:
            return jsonify({'error': 'Job not found or not processed'}), 404
        
        file_info = []
        for blob in blobs:
            filename = blob.name.split('/')[-1]
            if filename:
                file_info.append({
                    'filename': filename,
                    'size': blob.size,
                    'type': filename.split('.')[-1] if '.' in filename else 'unknown',
                    'updated': blob.updated.isoformat() if blob.updated else None
                })
        
        return jsonify({'job_id': job_id, 'files': file_info}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<job_id>/<filename>', methods=['GET'])
def download_file(job_id, filename):
    """Stream file directly from GCS"""
    try:
        bucket = get_bucket()
        blob = bucket.blob(f'results/{job_id}/{filename}')
        if not blob.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Stream file directly
        file_data = blob.download_as_bytes()
        
        # Determine content type
        content_type = 'application/octet-stream'
        if filename.endswith('.mp4'):
            content_type = 'video/mp4'
        elif filename.endswith('.csv'):
            content_type = 'text/csv'
        elif filename.endswith('.txt'):
            content_type = 'text/plain'
        
        from flask import Response
        return Response(
            file_data,
            mimetype=content_type,
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/<job_id>', methods=['GET'])
def get_analytics(job_id):
    """Get processed analytics data as JSON from GCS"""
    try:
        bucket = get_bucket()
        
        # Find analytics JSON file
        blobs = list(bucket.list_blobs(prefix=f'results/{job_id}/analytics_'))
        if not blobs:
            return jsonify({'error': 'Analytics not found for this job'}), 404
        
        # Get the first analytics file (there should only be one)
        analytics_blob = blobs[0]
        analytics_json = analytics_blob.download_as_text()
        
        import json
        analytics_data = json.loads(analytics_json)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'analytics': analytics_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get processing status for a job from GCS"""
    try:
        bucket = get_bucket()
        upload_blobs = list(bucket.list_blobs(prefix=f'uploads/{job_id}/', max_results=1))
        if not upload_blobs:
            return jsonify({'job_id': job_id, 'status': 'not_found'}), 404
        
        result_blobs = list(bucket.list_blobs(prefix=f'results/{job_id}/'))
        if result_blobs:
            return jsonify({'job_id': job_id, 'status': 'completed', 'files_count': len(result_blobs)}), 200
        else:
            return jsonify({'job_id': job_id, 'status': 'uploaded'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
