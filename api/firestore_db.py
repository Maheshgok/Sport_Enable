"""
Firestore Database Client for Moove API
Replaces PostgreSQL with Firestore for serverless deployment
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
from datetime import datetime, timedelta
import secrets
import hashlib

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    # For local development, use service account key
    # For Cloud Run, authentication is automatic via Application Default Credentials
    cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Use Application Default Credentials (works on Cloud Run)
        firebase_admin.initialize_app()

# Get Firestore client
db = firestore.client()

# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def get_user_by_email(email):
    """Get user document by email"""
    try:
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email.lower()).limit(1)
        results = query.stream()
        
        for doc in results:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            return user_data
        
        return None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def get_user_by_id(user_id):
    """Get user document by ID"""
    try:
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        
        if doc.exists:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            return user_data
        
        return None
    except Exception as e:
        print(f"Error getting user by ID: {e}")
        return None

def create_user(email, password_hash, first_name, last_name, roles):
    """Create new user document"""
    try:
        user_data = {
            'email': email.lower(),
            'passwordHash': password_hash,
            'firstName': first_name,
            'lastName': last_name,
            'roles': roles if isinstance(roles, list) else [roles],
            'status': 'active',
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP,
            'lastLoginAt': None
        }
        
        # Create document with auto-generated ID
        doc_ref = db.collection('users').document()
        doc_ref.set(user_data)
        
        user_data['id'] = doc_ref.id
        return user_data
    except Exception as e:
        print(f"Error creating user: {e}")
        raise

def update_last_login(user_id):
    """Update user's last login timestamp"""
    try:
        doc_ref = db.collection('users').document(user_id)
        doc_ref.update({
            'lastLoginAt': firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        print(f"Error updating last login: {e}")

# ============================================================================
# PROFILE FUNCTIONS
# ============================================================================

def create_athlete_profile(user_id, sport_id, sport_name, position=None, team=None, custom_baselines=None):
    """Create athlete profile"""
    try:
        profile_data = {
            'userId': user_id,
            'sportId': sport_id,
            'sportName': sport_name,
            'position': position,
            'team': team,
            'level': 'amateur',  # Default
            'customBaselines': custom_baselines or {},
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Use userId as document ID for easy lookup
        doc_ref = db.collection('athleteProfiles').document(user_id)
        doc_ref.set(profile_data)
        
        return profile_data
    except Exception as e:
        print(f"Error creating athlete profile: {e}")
        raise

def create_coach_profile(user_id, specialization=None, years_of_experience=None):
    """Create coach profile"""
    try:
        profile_data = {
            'userId': user_id,
            'specialization': specialization,
            'yearsOfExperience': years_of_experience or 0,
            'certifications': [],
            'sportsSpecialty': [],
            'athletesCoached': 0,
            'activePlayers': 0,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('coachProfiles').document(user_id)
        doc_ref.set(profile_data)
        
        return profile_data
    except Exception as e:
        print(f"Error creating coach profile: {e}")
        raise

def create_physiotherapist_profile(user_id, specialization=None, license_number=None):
    """Create physiotherapist profile"""
    try:
        profile_data = {
            'userId': user_id,
            'specialization': specialization,
            'licenseNumber': license_number,
            'certifications': [],
            'sportsSpecialty': [],
            'activePatients': 0,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('physiotherapistProfiles').document(user_id)
        doc_ref.set(profile_data)
        
        return profile_data
    except Exception as e:
        print(f"Error creating physiotherapist profile: {e}")
        raise

def create_parent_guardian_profile(user_id, guardian_type, relationship_to_athlete=None, permissions=None):
    """Create parent/guardian profile"""
    try:
        default_permissions = {
            'canViewMedical': False,
            'canViewVideos': True,
            'canViewReports': True,
            'canUploadVideos': False,
            'canScheduleSessions': False
        }
        
        if permissions:
            default_permissions.update(permissions)
        
        profile_data = {
            'userId': user_id,
            'guardianType': guardian_type,
            'relationshipToAthlete': relationship_to_athlete,
            'permissions': default_permissions,
            'maxAthletes': 3,
            'currentAthletes': 0,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('parentGuardianProfiles').document(user_id)
        doc_ref.set(profile_data)
        
        return profile_data
    except Exception as e:
        print(f"Error creating parent/guardian profile: {e}")
        raise

def get_athlete_profile(user_id):
    """Get athlete profile by user ID"""
    try:
        doc_ref = db.collection('athleteProfiles').document(user_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error getting athlete profile: {e}")
        return None

# ============================================================================
# INVITATION FUNCTIONS
# ============================================================================

def generate_invitation_token():
    """Generate secure random token for invitations"""
    return secrets.token_urlsafe(32)

def create_invitation(inviter_id, invitee_email, relationship_type, message=None):
    """Create new invitation"""
    try:
        # Get inviter details
        inviter = get_user_by_id(inviter_id)
        if not inviter:
            raise ValueError("Inviter not found")
        
        invitation_data = {
            'inviterId': inviter_id,
            'inviterEmail': inviter['email'],
            'inviterName': f"{inviter['firstName']} {inviter['lastName']}",
            'inviterRoles': inviter['roles'],
            'inviteeEmail': invitee_email.lower(),
            'inviteeId': None,
            'inviteeName': None,
            'relationshipType': relationship_type,
            'invitationToken': generate_invitation_token(),
            'message': message,
            'status': 'pending',
            'createdAt': firestore.SERVER_TIMESTAMP,
            'expiresAt': datetime.utcnow() + timedelta(days=7),
            'respondedAt': None,
            'rejectionReason': None,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Create document with auto-generated ID
        doc_ref = db.collection('relationshipInvitations').document()
        doc_ref.set(invitation_data)
        
        invitation_data['id'] = doc_ref.id
        return invitation_data
    except Exception as e:
        print(f"Error creating invitation: {e}")
        raise

def get_invitation_by_token(token):
    """Get invitation by token"""
    try:
        invitations_ref = db.collection('relationshipInvitations')
        query = invitations_ref.where('invitationToken', '==', token).limit(1)
        results = query.stream()
        
        for doc in results:
            invitation_data = doc.to_dict()
            invitation_data['id'] = doc.id
            return invitation_data
        
        return None
    except Exception as e:
        print(f"Error getting invitation by token: {e}")
        return None

def get_user_invitations(user_id=None, email=None, status='pending'):
    """Get invitations for a user (by ID or email)"""
    try:
        invitations_ref = db.collection('relationshipInvitations')
        
        if user_id:
            # Get invitations where user is inviter or invitee
            sent_query = invitations_ref.where('inviterId', '==', user_id).where('status', '==', status)
            received_query = invitations_ref.where('inviteeId', '==', user_id).where('status', '==', status)
            
            sent_invitations = [doc.to_dict() | {'id': doc.id} for doc in sent_query.stream()]
            received_invitations = [doc.to_dict() | {'id': doc.id} for doc in received_query.stream()]
            
            return {
                'sent': sent_invitations,
                'received': received_invitations
            }
        
        if email:
            # Get invitations sent to this email
            query = invitations_ref.where('inviteeEmail', '==', email.lower()).where('status', '==', status)
            invitations = [doc.to_dict() | {'id': doc.id} for doc in query.stream()]
            return invitations
        
        return []
    except Exception as e:
        print(f"Error getting user invitations: {e}")
        return []

def update_invitation_status(invitation_id, status, invitee_id=None, rejection_reason=None):
    """Update invitation status"""
    try:
        doc_ref = db.collection('relationshipInvitations').document(invitation_id)
        
        update_data = {
            'status': status,
            'respondedAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        if invitee_id:
            invitee = get_user_by_id(invitee_id)
            if invitee:
                update_data['inviteeId'] = invitee_id
                update_data['inviteeName'] = f"{invitee['firstName']} {invitee['lastName']}"
        
        if rejection_reason:
            update_data['rejectionReason'] = rejection_reason
        
        doc_ref.update(update_data)
        return True
    except Exception as e:
        print(f"Error updating invitation status: {e}")
        return False

# ============================================================================
# RELATIONSHIP FUNCTIONS
# ============================================================================

def create_relationship(user1_id, user2_id, relationship_type, invitation_id, approved_by, permissions=None):
    """Create active relationship"""
    try:
        user1 = get_user_by_id(user1_id)
        user2 = get_user_by_id(user2_id)
        
        if not user1 or not user2:
            raise ValueError("Users not found")
        
        default_permissions = {
            'canViewMedical': True,
            'canViewVideos': True,
            'canEditPrescriptions': False,
            'customPermissions': {}
        }
        
        if permissions:
            default_permissions.update(permissions)
        
        relationship_data = {
            'user1Id': user1_id,
            'user1Name': f"{user1['firstName']} {user1['lastName']}",
            'user1Roles': user1['roles'],
            'user2Id': user2_id,
            'user2Name': f"{user2['firstName']} {user2['lastName']}",
            'user2Roles': user2['roles'],
            'relationshipType': relationship_type,
            'status': 'active',
            'permissions': default_permissions,
            'establishedVia': invitation_id,
            'invitationId': invitation_id,
            'acceptedAt': firestore.SERVER_TIMESTAMP,
            'approvedBy': approved_by,
            'approvedAt': firestore.SERVER_TIMESTAMP,
            'terminatedAt': None,
            'terminatedBy': None,
            'terminationReason': None,
            'notes': '',
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Create document with auto-generated ID
        doc_ref = db.collection('relationships').document()
        doc_ref.set(relationship_data)
        
        relationship_data['id'] = doc_ref.id
        return relationship_data
    except Exception as e:
        print(f"Error creating relationship: {e}")
        raise

def get_user_relationships(user_id, status='active'):
    """Get all relationships for a user"""
    try:
        relationships_ref = db.collection('relationships')
        
        # Query relationships where user is either user1 or user2
        query1 = relationships_ref.where('user1Id', '==', user_id).where('status', '==', status)
        query2 = relationships_ref.where('user2Id', '==', user_id).where('status', '==', status)
        
        relationships = []
        for doc in query1.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            relationships.append(data)
        
        for doc in query2.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            relationships.append(data)
        
        return relationships
    except Exception as e:
        print(f"Error getting user relationships: {e}")
        return []

# ============================================================================
# CHANGE REQUEST FUNCTIONS
# ============================================================================

def create_change_request(request_type, requested_by, invitation_id=None, relationship_id=None, 
                         user1_id=None, user2_id=None, relationship_type=None, requested_changes=None):
    """Create relationship change request for admin approval"""
    try:
        requester = get_user_by_id(requested_by)
        if not requester:
            raise ValueError("Requester not found")
        
        request_data = {
            'requestType': request_type,
            'requestedBy': requested_by,
            'requestedByName': f"{requester['firstName']} {requester['lastName']}",
            'invitationId': invitation_id,
            'relationshipId': relationship_id,
            'user1Id': user1_id,
            'user2Id': user2_id,
            'relationshipType': relationship_type,
            'requestedChanges': requested_changes or {},
            'status': 'pending_admin',
            'priority': 'normal',
            'reviewedBy': None,
            'reviewedByName': None,
            'reviewedAt': None,
            'approvalNotes': None,
            'rejectionReason': None,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Create document with auto-generated ID
        doc_ref = db.collection('relationshipChangeRequests').document()
        doc_ref.set(request_data)
        
        request_data['id'] = doc_ref.id
        return request_data
    except Exception as e:
        print(f"Error creating change request: {e}")
        raise

def get_pending_change_requests():
    """Get all pending change requests for admin review"""
    try:
        requests_ref = db.collection('relationshipChangeRequests')
        query = requests_ref.where('status', '==', 'pending_admin').order_by('createdAt', direction=firestore.Query.DESCENDING)
        
        requests = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            requests.append(data)
        
        return requests
    except Exception as e:
        print(f"Error getting pending change requests: {e}")
        return []

def update_change_request_status(request_id, status, reviewed_by, approval_notes=None, rejection_reason=None):
    """Update change request status"""
    try:
        reviewer = get_user_by_id(reviewed_by)
        if not reviewer:
            raise ValueError("Reviewer not found")
        
        doc_ref = db.collection('relationshipChangeRequests').document(request_id)
        
        update_data = {
            'status': status,
            'reviewedBy': reviewed_by,
            'reviewedByName': f"{reviewer['firstName']} {reviewer['lastName']}",
            'reviewedAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        if approval_notes:
            update_data['approvalNotes'] = approval_notes
        
        if rejection_reason:
            update_data['rejectionReason'] = rejection_reason
        
        doc_ref.update(update_data)
        return True
    except Exception as e:
        print(f"Error updating change request status: {e}")
        return False

# ============================================================================
# AUDIT LOG FUNCTIONS
# ============================================================================

def create_audit_log(action, actor_id, target_user_id=None, invitation_id=None, 
                    relationship_id=None, relationship_type=None, change_details=None,
                    ip_address=None, user_agent=None):
    """Create audit log entry"""
    try:
        actor = get_user_by_id(actor_id)
        if not actor:
            raise ValueError("Actor not found")
        
        log_data = {
            'action': action,
            'actorId': actor_id,
            'actorName': f"{actor['firstName']} {actor['lastName']}",
            'actorRoles': actor['roles'],
            'targetUserId': target_user_id,
            'targetUserName': None,
            'invitationId': invitation_id,
            'relationshipId': relationship_id,
            'relationshipType': relationship_type,
            'changeDetails': change_details or {},
            'ipAddress': ip_address,
            'userAgent': user_agent,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'adminOverride': False,
            'adminNotes': None
        }
        
        if target_user_id:
            target = get_user_by_id(target_user_id)
            if target:
                log_data['targetUserName'] = f"{target['firstName']} {target['lastName']}"
        
        # Create document with auto-generated ID
        doc_ref = db.collection('relationshipAuditLog').document()
        doc_ref.set(log_data)
        
        return log_data
    except Exception as e:
        print(f"Error creating audit log: {e}")
        return None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def test_connection():
    """Test Firestore connection"""
    try:
        # Try to read from users collection
        users_ref = db.collection('users')
        query = users_ref.limit(1)
        list(query.stream())
        return True
    except Exception as e:
        print(f"Firestore connection test failed: {e}")
        return False

def check_duplicate_invitation(inviter_id, invitee_email, relationship_type):
    """Check if a pending invitation already exists"""
    try:
        invitations_ref = db.collection('relationshipInvitations')
        query = invitations_ref\
            .where('inviterId', '==', inviter_id)\
            .where('inviteeEmail', '==', invitee_email.lower())\
            .where('relationshipType', '==', relationship_type)\
            .where('status', '==', 'pending')\
            .limit(1)
        
        results = list(query.stream())
        return len(results) > 0
    except Exception as e:
        print(f"Error checking duplicate invitation: {e}")
        return False

def check_existing_relationship(user1_id, user2_id, relationship_type):
    """Check if an active relationship already exists"""
    try:
        relationships_ref = db.collection('relationships')
        
        # Check both directions (user1->user2 and user2->user1)
        query1 = relationships_ref\
            .where('user1Id', '==', user1_id)\
            .where('user2Id', '==', user2_id)\
            .where('relationshipType', '==', relationship_type)\
            .where('status', '==', 'active')\
            .limit(1)
        
        query2 = relationships_ref\
            .where('user1Id', '==', user2_id)\
            .where('user2Id', '==', user1_id)\
            .where('relationshipType', '==', relationship_type)\
            .where('status', '==', 'active')\
            .limit(1)
        
        results1 = list(query1.stream())
        results2 = list(query2.stream())
        
        return len(results1) > 0 or len(results2) > 0
    except Exception as e:
        print(f"Error checking existing relationship: {e}")
        return False
