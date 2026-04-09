"""
Relationship Management Endpoints
Handles invitations, relationships, and admin approvals
"""

from flask import request, jsonify
from auth import require_auth, is_super_user
from db import get_db_cursor, execute_query
import uuid
import secrets
from datetime import datetime, timedelta

# ============================================
# INVITATION ENDPOINTS
# ============================================

def send_invitation():
    """
    Send an invitation to establish a relationship
    
    POST /api/invitations/send
    Body: {
        "invitee_email": "user@example.com",
        "relationship_type": "coach_athlete",
        "athlete_id": "uuid",  // or coach_id, etc.
        "message": "Optional personal message"
    }
    
    Permission Rules:
    - Coaches can invite: athletes, parents, physiotherapists, other coaches
    - Athletes can invite: coaches, parents, physiotherapists
    - Physiotherapists can invite: athletes, coaches
    - Parents can ONLY accept invites (cannot send)
    - Admins can invite anyone
    """
    current_user = request.current_user
    data = request.get_json()
    
    # Validate required fields
    required = ['invitee_email', 'relationship_type']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    invitee_email = data['invitee_email'].lower().strip()
    relationship_type = data['relationship_type']
    
    # Validate relationship type
    valid_types = [
        'coach_athlete', 'coach_parent', 'coach_physiotherapist', 'coach_coach',
        'parent_athlete', 'guardian_athlete', 'manager_athlete',
        'physiotherapist_athlete', 'physiotherapist_coach'
    ]
    if relationship_type not in valid_types:
        return jsonify({'error': 'Invalid relationship type'}), 400
    
    # Check if current user has permission to send this type of invitation
    if not can_send_invitation(current_user['roles'], relationship_type):
        return jsonify({
            'error': 'You do not have permission to send this type of invitation',
            'detail': 'Parents can only accept invitations, not send them'
        }), 403
    
    # Check if invitee already has pending invitation
    existing = execute_query("""
        SELECT invitation_id FROM physio_app.relationship_invitations
        WHERE invitee_email = %s
          AND relationship_type = %s
          AND status = 'pending'
          AND expires_at > NOW()
    """, (invitee_email, relationship_type), fetch_one=True)
    
    if existing:
        return jsonify({'error': 'Invitation already pending for this user'}), 409
    
    # Check if invitee is already registered
    invitee = execute_query(
        "SELECT user_id FROM physio_app.users WHERE email = %s",
        (invitee_email,),
        fetch_one=True
    )
    invitee_id = invitee['user_id'] if invitee else None
    
    # Generate invitation token
    invitation_token = secrets.token_urlsafe(32)
    
    # Get profile IDs based on relationship type
    athlete_id = data.get('athlete_id')
    coach_id = data.get('coach_id')
    physiotherapist_id = data.get('physiotherapist_id')
    
    # Create invitation
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO physio_app.relationship_invitations
            (inviter_id, invitee_email, invitee_id, relationship_type,
             athlete_id, coach_id, physiotherapist_id,
             invitation_message, invitation_token, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING invitation_id, created_at, expires_at
        """, (
            current_user['user_id'],
            invitee_email,
            invitee_id,
            relationship_type,
            athlete_id,
            coach_id,
            physiotherapist_id,
            data.get('message'),
            invitation_token,
            datetime.now() + timedelta(days=7)
        ))
        
        invitation = cur.fetchone()
    
    # TODO: Send email notification
    send_invitation_email(
        invitee_email=invitee_email,
        inviter_name=f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}",
        relationship_type=relationship_type,
        invitation_token=invitation_token,
        message=data.get('message')
    )
    
    return jsonify({
        'success': True,
        'invitation_id': str(invitation['invitation_id']),
        'expires_at': invitation['expires_at'].isoformat(),
        'message': 'Invitation sent successfully'
    }), 201


def get_received_invitations():
    """
    Get invitations received by current user
    
    GET /api/invitations/received
    """
    current_user = request.current_user
    
    invitations = execute_query("""
        SELECT 
            i.invitation_id,
            i.relationship_type,
            i.invitation_message,
            i.created_at,
            i.expires_at,
            i.invitation_token,
            u.first_name || ' ' || u.last_name as inviter_name,
            u.email as inviter_email,
            u.avatar as inviter_avatar
        FROM physio_app.relationship_invitations i
        JOIN physio_app.users u ON i.inviter_id = u.user_id
        WHERE (i.invitee_email = %s OR i.invitee_id = %s)
          AND i.status = 'pending'
          AND i.expires_at > NOW()
        ORDER BY i.created_at DESC
    """, (current_user['email'], current_user['user_id']), fetch_all=True)
    
    result = []
    for inv in invitations:
        result.append({
            'invitation_id': str(inv['invitation_id']),
            'relationship_type': inv['relationship_type'],
            'message': inv['invitation_message'],
            'inviter': {
                'name': inv['inviter_name'],
                'email': inv['inviter_email'],
                'avatar': inv['inviter_avatar']
            },
            'created_at': inv['created_at'].isoformat(),
            'expires_at': inv['expires_at'].isoformat(),
            'token': inv['invitation_token']
        })
    
    return jsonify({
        'success': True,
        'invitations': result,
        'count': len(result)
    })


def get_sent_invitations():
    """
    Get invitations sent by current user
    
    GET /api/invitations/sent
    """
    current_user = request.current_user
    
    invitations = execute_query("""
        SELECT 
            i.invitation_id,
            i.relationship_type,
            i.invitee_email,
            i.invitation_message,
            i.status,
            i.created_at,
            i.expires_at,
            i.responded_at
        FROM physio_app.relationship_invitations i
        WHERE i.inviter_id = %s
        ORDER BY i.created_at DESC
        LIMIT 50
    """, (current_user['user_id'],), fetch_all=True)
    
    result = []
    for inv in invitations:
        result.append({
            'invitation_id': str(inv['invitation_id']),
            'relationship_type': inv['relationship_type'],
            'invitee_email': inv['invitee_email'],
            'message': inv['invitation_message'],
            'status': inv['status'],
            'created_at': inv['created_at'].isoformat(),
            'expires_at': inv['expires_at'].isoformat() if inv['expires_at'] else None,
            'responded_at': inv['responded_at'].isoformat() if inv['responded_at'] else None
        })
    
    return jsonify({
        'success': True,
        'invitations': result,
        'count': len(result)
    })


def accept_invitation(token):
    """
    Accept an invitation
    
    POST /api/invitations/{token}/accept
    Body: {
        "response_message": "Optional message"
    }
    """
    current_user = request.current_user
    data = request.get_json() or {}
    
    # Get invitation
    invitation = execute_query("""
        SELECT *
        FROM physio_app.relationship_invitations
        WHERE invitation_token = %s
          AND status = 'pending'
          AND expires_at > NOW()
    """, (token,), fetch_one=True)
    
    if not invitation:
        return jsonify({'error': 'Invitation not found or expired'}), 404
    
    # Verify this is for the current user
    if invitation['invitee_email'] != current_user['email'] and \
       invitation['invitee_id'] != current_user['user_id']:
        return jsonify({'error': 'This invitation is not for you'}), 403
    
    # Update invitation status
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE physio_app.relationship_invitations
            SET status = 'accepted',
                invitee_id = %s,
                response_message = %s,
                responded_at = NOW()
            WHERE invitation_id = %s
            RETURNING invitation_id
        """, (
            current_user['user_id'],
            data.get('response_message'),
            invitation['invitation_id']
        ))
    
    # Create change request for admin approval
    request_id = create_relationship_change_request(
        requested_by=current_user['user_id'],
        request_type='add_relationship',
        relationship_type=invitation['relationship_type'],
        user_a_id=invitation['inviter_id'],
        user_b_id=current_user['user_id'],
        invitation_id=invitation['invitation_id'],
        reason=f"Accepted invitation from {invitation['inviter_id']}"
    )
    
    # Send email to admin
    send_admin_approval_email(request_id)
    
    return jsonify({
        'success': True,
        'message': 'Invitation accepted. Pending admin approval.',
        'request_id': request_id
    })


def reject_invitation(token):
    """
    Reject an invitation
    
    POST /api/invitations/{token}/reject
    Body: {
        "response_message": "Optional reason"
    }
    """
    current_user = request.current_user
    data = request.get_json() or {}
    
    # Get invitation
    invitation = execute_query("""
        SELECT *
        FROM physio_app.relationship_invitations
        WHERE invitation_token = %s
          AND status = 'pending'
    """, (token,), fetch_one=True)
    
    if not invitation:
        return jsonify({'error': 'Invitation not found'}), 404
    
    # Verify this is for the current user
    if invitation['invitee_email'] != current_user['email']:
        return jsonify({'error': 'This invitation is not for you'}), 403
    
    # Update invitation status
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE physio_app.relationship_invitations
            SET status = 'rejected',
                invitee_id = %s,
                response_message = %s,
                responded_at = NOW()
            WHERE invitation_id = %s
        """, (
            current_user['user_id'],
            data.get('response_message'),
            invitation['invitation_id']
        ))
    
    # Notify inviter
    # TODO: Send email to inviter
    
    return jsonify({
        'success': True,
        'message': 'Invitation rejected'
    })


def get_invitation_details(token):
    """
    Get invitation details by token (public access for accepting)
    
    GET /api/invitations/{token}/details
    """
    invitation = execute_query("""
        SELECT 
            i.invitation_id,
            i.relationship_type,
            i.invitation_message,
            i.created_at,
            i.expires_at,
            i.status,
            u.first_name || ' ' || u.last_name as inviter_name,
            u.avatar as inviter_avatar
        FROM physio_app.relationship_invitations i
        JOIN physio_app.users u ON i.inviter_id = u.user_id
        WHERE i.invitation_token = %s
    """, (token,), fetch_one=True)
    
    if not invitation:
        return jsonify({'error': 'Invitation not found'}), 404
    
    return jsonify({
        'success': True,
        'invitation': {
            'invitation_id': str(invitation['invitation_id']),
            'relationship_type': invitation['relationship_type'],
            'message': invitation['invitation_message'],
            'inviter_name': invitation['inviter_name'],
            'inviter_avatar': invitation['inviter_avatar'],
            'status': invitation['status'],
            'created_at': invitation['created_at'].isoformat(),
            'expires_at': invitation['expires_at'].isoformat() if invitation['expires_at'] else None,
            'is_expired': invitation['expires_at'] < datetime.now() if invitation['expires_at'] else False
        }
    })


# ============================================
# RELATIONSHIP ENDPOINTS
# ============================================

def get_my_relationships():
    """
    Get current user's active relationships
    
    GET /api/relationships/mine
    """
    current_user = request.current_user
    
    relationships = execute_query("""
        SELECT * FROM physio_app.get_user_relationships(%s)
    """, (current_user['user_id'],), fetch_all=True)
    
    result = []
    for rel in relationships:
        result.append({
            'relationship_id': str(rel['relationship_id']),
            'relationship_type': rel['relationship_type'],
            'other_user': {
                'user_id': str(rel['other_user_id']),
                'name': rel['other_user_name'],
                'email': rel['other_user_email']
            },
            'status': rel['status'],
            'created_at': rel['created_at'].isoformat()
        })
    
    return jsonify({
        'success': True,
        'relationships': result,
        'count': len(result)
    })


def request_relationship_change():
    """
    Request a relationship change (termination, permission modification)
    
    POST /api/relationships/request-change
    Body: {
        "request_type": "remove_relationship",
        "relationship_id": "uuid",
        "reason": "Reason for change"
    }
    """
    current_user = request.current_user
    data = request.get_json()
    
    # Validate
    if 'request_type' not in data or 'relationship_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get relationship
    relationship = execute_query("""
        SELECT * FROM physio_app.relationships
        WHERE relationship_id = %s
          AND (primary_user_id = %s OR secondary_user_id = %s)
    """, (data['relationship_id'], current_user['user_id'], current_user['user_id']), fetch_one=True)
    
    if not relationship:
        return jsonify({'error': 'Relationship not found or access denied'}), 404
    
    # Create change request
    request_id = create_relationship_change_request(
        requested_by=current_user['user_id'],
        request_type=data['request_type'],
        relationship_type=relationship['relationship_type'],
        user_a_id=relationship['primary_user_id'],
        user_b_id=relationship['secondary_user_id'],
        reason=data.get('reason'),
        request_data=data.get('additional_data')
    )
    
    # Send email to admin
    send_admin_approval_email(request_id)
    
    return jsonify({
        'success': True,
        'request_id': request_id,
        'message': 'Change request submitted for admin approval'
    }), 202


# ============================================
# ADMIN ENDPOINTS
# ============================================

def get_pending_requests():
    """
    Get all pending relationship change requests (admin only)
    
    GET /api/admin/relationship-requests
    """
    requests = execute_query("""
        SELECT * FROM physio_app.v_admin_pending_requests
        ORDER BY priority, created_at
        LIMIT 100
    """, fetch_all=True)
    
    result =[{
            'request_id': str(req['request_id']),
            'request_type': req['request_type'],
            'relationship_type': req['relationship_type'],
            'requester': {
                'name': req['requester_name'],
                'email': req['requester_email']
            },
            'users': {
                'user_a': req['user_a_name'],
                'user_b': req['user_b_name']
            },
            'reason': req['reason'],
            'priority': req['priority'],
            'created_at': req['created_at'].isoformat(),
            'notification_count': req['notification_count']
        } for req in requests]
    
    return jsonify({
        'success': True,
        'requests': result,
        'count': len(result)
    })


def approve_request(request_id):
    """
    Approve a relationship change request (admin only)
    
    POST /api/admin/relationship-requests/{request_id}/approve
    Body: {
        "admin_notes": "Optional notes"
    }
    """
    current_user = request.current_user
    data = request.get_json() or {}
    
    # Get request
    change_request = execute_query("""
        SELECT * FROM physio_app.relationship_change_requests
        WHERE request_id = %s AND status = 'pending_admin'
    """, (request_id,), fetch_one=True)
    
    if not change_request:
        return jsonify({'error': 'Request not found'}), 404
    
    # Process based on request type
    if change_request['request_type'] == 'add_relationship':
        # Create relationship
        relationship_id = create_relationship(
            relationship_type=change_request['relationship_type'],
            user_a_id=change_request['user_a_id'],
            user_b_id=change_request['user_b_id'],
            approved_by=current_user['user_id'],
            invitation_id=change_request['invitation_id'],
            request_id=request_id
        )
        result_message = f'Relationship created: {relationship_id}'
    
    elif change_request['request_type'] == 'remove_relationship':
        # Terminate relationship
        execute_query("""
            UPDATE physio_app.relationships
            SET status = 'terminated',
                terminated_at = NOW(),
                terminated_reason = %s
            WHERE primary_user_id = %s
              AND secondary_user_id = %s
              AND relationship_type = %s
        """, (
            data.get('admin_notes', 'Admin approved termination'),
            change_request['user_a_id'],
            change_request['user_b_id'],
            change_request['relationship_type']
        ))
        result_message = 'Relationship terminated'
    
    # Update request status
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE physio_app.relationship_change_requests
            SET status = 'approved',
                reviewed_by = %s,
                reviewed_at = NOW(),
                admin_notes = %s
            WHERE request_id = %s
        """, (current_user['user_id'], data.get('admin_notes'), request_id))
    
    # TODO: Notify users
    
    return jsonify({
        'success': True,
        'message': result_message
    })


def reject_request(request_id):
    """
    Reject a relationship change request (admin only)
    
    POST /api/admin/relationship-requests/{request_id}/reject
    Body: {
        "rejection_reason": "Reason for rejection",
        "admin_notes": "Optional notes"
    }
    """
    current_user = request.current_user
    data = request.get_json()
    
    if 'rejection_reason' not in data:
        return jsonify({'error': 'Rejection reason required'}), 400
    
    # Update request
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE physio_app.relationship_change_requests
            SET status = 'rejected',
                reviewed_by = %s,
                reviewed_at = NOW(),
                rejection_reason = %s,
                admin_notes = %s
            WHERE request_id = %s AND status = 'pending_admin'
            RETURNING request_id
        """, (
            current_user['user_id'],
            data['rejection_reason'],
            data.get('admin_notes'),
            request_id
        ))
        
        result = cur.fetchone()
    
    if not result:
        return jsonify({'error': 'Request not found'}), 404
    
    # TODO: Notify requester
    
    return jsonify({
        'success': True,
        'message': 'Request rejected'
    })


# ============================================
# HELPER FUNCTIONS
# ============================================

def create_relationship_change_request(requested_by, request_type, relationship_type,
                                      user_a_id, user_b_id, invitation_id=None,
                                      reason=None, request_data=None):
    """Create a relationship change request"""
    request_id = str(uuid.uuid4())
    
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO physio_app.relationship_change_requests
            (request_id, requested_by, request_type, relationship_type,
             user_a_id, user_b_id, invitation_id, reason, request_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING request_id
        """, (
            request_id, requested_by, request_type, relationship_type,
            user_a_id, user_b_id, invitation_id, reason, request_data
        ))
    
    return request_id


def create_relationship(relationship_type, user_a_id, user_b_id, approved_by,
                       invitation_id=None, request_id=None):
    """Create an active relationship"""
    relationship_id = str(uuid.uuid4())
    
    # Determine which profiles to link
    athlete_id = coach_id = physiotherapist_id = guardian_id = None
    
    # TODO: Get appropriate profile IDs based on relationship type
    
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO physio_app.relationships
            (relationship_id, relationship_type, primary_user_id, secondary_user_id,
             athlete_id, coach_id, physiotherapist_id, guardian_id,
             established_via, approved_by, approval_request_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
            RETURNING relationship_id
        """, (
            relationship_id, relationship_type, user_a_id, user_b_id,
            athlete_id, coach_id, physiotherapist_id, guardian_id,
            invitation_id, approved_by, request_id
        ))
    
    return relationship_id


def send_invitation_email(invitee_email, inviter_name, relationship_type, 
                         invitation_token, message=None):
    """Send invitation email (placeholder)"""
    # TODO: Implement email sending
    print(f"Email to {invitee_email}: Invitation from {inviter_name}")
    pass


def send_admin_approval_email(request_id):
    """Send email to admins for approval (placeholder)"""
    # TODO: Implement email sending to all super admins
    print(f"Email to admins: New approval request {request_id}")
    pass


def can_send_invitation(user_roles, relationship_type):
    """
    Check if user with given roles can send a specific type of invitation
    
    Permission Matrix:
    - Coach: Can invite athletes, parents, physiotherapists, other coaches
    - Athlete: Can invite coaches, parents, physiotherapists
    - Physiotherapist: Can invite athletes, coaches
    - Parent/Guardian: CANNOT send invites (can only accept)
    - Admin: Can invite anyone
    """
    # Admins can do anything
    if 'admin' in user_roles or 'super_user' in user_roles:
        return True
    
    # Parents cannot send invitations
    if 'parent' in user_roles:
        return False
    
    # Define what each role can invite
    invitation_permissions = {
        'coach': [
            'coach_athlete', 'coach_parent', 'coach_physiotherapist', 'coach_coach'
        ],
        'athlete': [
            'coach_athlete',  # Athlete inviting a coach (reverse)
            'parent_athlete', 'guardian_athlete', 'manager_athlete',  # Athlete inviting parent
            'physiotherapist_athlete'  # Athlete inviting physio
        ],
        'physiotherapist': [
            'physiotherapist_athlete',
            'physiotherapist_coach',
            'coach_physiotherapist'  # Physio inviting coach (reverse)
        ]
    }
    
    # Check if any of user's roles allow this invitation type
    for role in user_roles:
        if role in invitation_permissions:
            if relationship_type in invitation_permissions[role]:
                return True
    
    return False
