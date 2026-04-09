"""
Relationship Management API - Firestore Version
Handles invite-based relationships between users (coaches, athletes, parents, physios)
"""

from flask import request, jsonify
from auth import require_auth, is_super_user
import firestore_db as db
from datetime import datetime
import secrets

# Valid relationship types
VALID_RELATIONSHIP_TYPES = [
    'coach_athlete',
    'coach_parent',
    'coach_physiotherapist',
    'coach_coach',
    'parent_athlete',
    'guardian_athlete',
    'manager_athlete',
    'physiotherapist_athlete',
    'physiotherapist_coach'
]

def can_send_invitation(user_roles, relationship_type):
    """
    Check if user has permission to send this type of invitation
    
    Permission Matrix:
    - Admins: Can invite anyone
    - Parents: CANNOT send invitations (can only accept)
    - Coaches: Can invite athletes, parents, physios, coaches
    - Athletes: Can invite coaches, parents, physios (not other athletes)
    - Physios: Can invite athletes, coaches (not parents, not other physios)
    """
    # Admins can do anything
    if 'admin' in user_roles or 'super_user' in user_roles:
        return True
    
    # Parents CANNOT send invitations
    if 'parent' in user_roles:
        return False
    
    # Define allowed invitations per role
    invitation_permissions = {
        'coach': [
            'coach_athlete',
            'coach_parent',
            'coach_physiotherapist',
            'coach_coach'
        ],
        'athlete': [
            'coach_athlete',  # Athletes can invite coaches
            'parent_athlete',
            'guardian_athlete',
            'manager_athlete',
            'physiotherapist_athlete'
        ],
        'physiotherapist': [
            'physiotherapist_athlete',
            'physiotherapist_coach',
            'coach_physiotherapist'  # Can accept coach invitations
        ]
    }
    
    # Check if any of user's roles allow this invitation type
    for role in user_roles:
        if role in invitation_permissions:
            if relationship_type in invitation_permissions[role]:
                return True
    
    return False

@require_auth()
def send_invitation():
    """
   Send an invitation to establish a relationship
    
    POST /api/invitations/send
    Body: {
        "invitee_email": "user@example.com",
        "relationship_type": "coach_athlete",
        "message": "Optional message"
    }
    """
    try:
        data = request.get_json()
        current_user = request.current_user
        
        invitee_email = data.get('invitee_email')
        relationship_type = data.get('relationship_type')
        message = data.get('message', '')
        
        # Validate inputs
        if not invitee_email or not relationship_type:
            return jsonify({'error': 'invitee_email and relationship_type are required'}), 400
        
        if relationship_type not in VALID_RELATIONSHIP_TYPES:
            return jsonify({'error': f'Invalid relationship_type. Must be one of: {", ".join(VALID_RELATIONSHIP_TYPES)}'}), 400
        
        # Check permissions
        if not can_send_invitation(current_user['roles'], relationship_type):
            return jsonify({
                'error': 'You do not have permission to send this type of invitation',
                'detail': 'Parents can only accept invitations, not send them' if 'parent' in current_user['roles'] else 'Insufficient permissions'
            }), 403
        
        # Check for duplicate pending invitation
        if db.check_duplicate_invitation(current_user['user_id'], invitee_email, relationship_type):
            return jsonify({'error': 'A pending invitation already exists for this relationship'}), 409
        
        # Check if invitee exists and if relationship already exists
        invitee = db.get_user_by_email(invitee_email)
        if invitee:
            if db.check_existing_relationship(current_user['user_id'], invitee['id'], relationship_type):
                return jsonify({'error': 'This relationship already exists'}), 409
        
        # Create invitation
        invitation = db.create_invitation(
            inviter_id=current_user['user_id'],
            invitee_email=invitee_email,
            relationship_type=relationship_type,
            message=message
        )
        
        # Create audit log
        db.create_audit_log(
            action='invitation_sent',
            actor_id=current_user['user_id'],
            target_user_id=invitee['id'] if invitee else None,
            invitation_id=invitation['id'],
            relationship_type=relationship_type
        )
        
        # TODO: Send email notification to invitee
        
        return jsonify({
            'success': True,
            'invitation': {
                'id': invitation['id'],
                'invitee_email': invitation['inviteeEmail'],
                'relationship_type': invitation['relationshipType'],
                'expires_at': invitation['expiresAt'].isoformat() if invitation['expiresAt'] else None,
                'status': invitation['status']
            }
        }), 201
        
    except Exception as e:
        print(f"Error sending invitation: {e}")
        return jsonify({'error': 'Failed to send invitation', 'detail': str(e)}), 500

@require_auth()
def get_received_invitations():
    """
    Get invitations received by current user
    
    GET /api/invitations/received
    """
    try:
        current_user = request.current_user
        
        invitations = db.get_user_invitations(
            user_id=current_user['user_id'],
            email=current_user['email'],
            status='pending'
        )
        
        # Format response
        formatted = []
        for inv in invitations.get('received', []) if isinstance(invitations, dict) else invitations:
            formatted.append({
                'id': inv['id'],
                'inviter_name': inv.get('inviterName'),
                'inviter_email': inv.get('inviterEmail'),
                'relationship_type': inv.get('relationshipType'),
                'message': inv.get('message'),
                'created_at': inv.get('createdAt'),
                'expires_at': inv.get('expiresAt'),
                'invitation_token': inv.get('invitationToken')
            })
        
        return jsonify({
            'success': True,
            'invitations': formatted
        }), 200
        
    except Exception as e:
        print(f"Error getting received invitations: {e}")
        return jsonify({'error': 'Failed to get invitations', 'detail': str(e)}), 500

@require_auth()
def get_sent_invitations():
    """
    Get invitations sent by current user
    
    GET /api/invitations/sent
    """
    try:
        current_user = request.current_user
        
        invitations = db.get_user_invitations(
            user_id=current_user['user_id'],
            status='pending'
        )
        
        # Format response
        formatted = []
        for inv in invitations.get('sent', []) if isinstance(invitations, dict) else []:
            formatted.append({
                'id': inv['id'],
                'invitee_email': inv.get('inviteeEmail'),
                'invitee_name': inv.get('inviteeName'),
                'relationship_type': inv.get('relationshipType'),
                'message': inv.get('message'),
                'created_at': inv.get('createdAt'),
                'expires_at': inv.get('expiresAt'),
                'status': inv.get('status')
            })
        
        return jsonify({
            'success': True,
            'invitations': formatted
        }), 200
        
    except Exception as e:
        print(f"Error getting sent invitations: {e}")
        return jsonify({'error': 'Failed to get invitations', 'detail': str(e)}), 500

@require_auth()
def accept_invitation(token):
    """
    Accept an invitation
    
    POST /api/invitations/{token}/accept
    """
    try:
        current_user = request.current_user
        
        # Get invitation
        invitation = db.get_invitation_by_token(token)
        if not invitation:
            return jsonify({'error': 'Invitation not found or expired'}), 404
        
        # Verify invitation is for this user
        if invitation['inviteeEmail'].lower() != current_user['email'].lower():
            return jsonify({'error': 'This invitation is not for you'}), 403
        
        # Check invitation status
        if invitation['status'] != 'pending':
            return jsonify({'error': f'Invitation is {invitation["status"]}'}), 400
        
        # Check expiration
        if invitation.get('expiresAt') and invitation['expiresAt'] < datetime.utcnow():
            db.update_invitation_status(invitation['id'], 'expired')
            return jsonify({'error': 'Invitation has expired'}), 400
        
        # Update invitation status
        db.update_invitation_status(
            invitation_id=invitation['id'],
            status='accepted',
            invitee_id=current_user['user_id']
        )
        
        # Create relationship change request for admin approval
        change_request = db.create_change_request(
            request_type='add_relationship',
            requested_by=current_user['user_id'],
            invitation_id=invitation['id'],
            user1_id=invitation['inviterId'],
            user2_id=current_user['user_id'],
            relationship_type=invitation['relationshipType']
        )
        
        # Create audit log
        db.create_audit_log(
            action='invitation_accepted',
            actor_id=current_user['user_id'],
            target_user_id=invitation['inviterId'],
            invitation_id=invitation['id'],
            relationship_type=invitation['relationshipType']
        )
        
        # TODO: Send email notification to admin for approval
        # TODO: Send email notification to inviter
        
        return jsonify({
            'success': True,
            'message': 'Invitation accepted. Awaiting admin approval.',
            'change_request_id': change_request['id']
        }), 200
        
    except Exception as e:
        print(f"Error accepting invitation: {e}")
        return jsonify({'error': 'Failed to accept invitation', 'detail': str(e)}), 500

@require_auth()
def reject_invitation(token):
    """
    Reject an invitation
    
    POST /api/invitations/{token}/reject
    Body: {
        "reason": "Optional reason"
    }
    """
    try:
        current_user = request.current_user
        data = request.get_json() or {}
        reason = data.get('reason')
        
        # Get invitation
        invitation = db.get_invitation_by_token(token)
        if not invitation:
            return jsonify({'error': 'Invitation not found'}), 404
        
        # Verify invitation is for this user
        if invitation['inviteeEmail'].lower() != current_user['email'].lower():
            return jsonify({'error': 'This invitation is not for you'}), 403
        
        # Check invitation status
        if invitation['status'] != 'pending':
            return jsonify({'error': f'Invitation is {invitation["status"]}'}), 400
        
        # Update invitation status
        db.update_invitation_status(
            invitation_id=invitation['id'],
            status='rejected',
            invitee_id=current_user['user_id'],
            rejection_reason=reason
        )
        
        # Create audit log
        db.create_audit_log(
            action='invitation_rejected',
            actor_id=current_user['user_id'],
            target_user_id=invitation['inviterId'],
            invitation_id=invitation['id'],
            relationship_type=invitation['relationshipType'],
            change_details={'reason': reason} if reason else None
        )
        
        # TODO: Send email notification to inviter
        
        return jsonify({
            'success': True,
            'message': 'Invitation rejected'
        }), 200
        
    except Exception as e:
        print(f"Error rejecting invitation: {e}")
        return jsonify({'error': 'Failed to reject invitation', 'detail': str(e)}), 500

def get_invitation_details(token):
    """
    Get public invitation details (no auth required)
    
    GET /api/invitations/{token}
    """
    try:
        invitation = db.get_invitation_by_token(token)
        if not invitation:
            return jsonify({'error': 'Invitation not found'}), 404
        
        # Check expiration
        if invitation.get('expiresAt') and invitation['expiresAt'] < datetime.utcnow():
            db.update_invitation_status(invitation['id'], 'expired')
            return jsonify({'error': 'Invitation has expired'}), 400
        
        # Return only public information
        return jsonify({
            'success': True,
            'invitation': {
                'inviter_name': invitation.get('inviterName'),
                'relationship_type': invitation.get('relationshipType'),
                'message': invitation.get('message'),
                'status': invitation.get('status'),
                'created_at': invitation.get('createdAt'),
                'expires_at': invitation.get('expiresAt')
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting invitation details: {e}")
        return jsonify({'error': 'Failed to get invitation details', 'detail': str(e)}), 500

@require_auth()
def get_my_relationships():
    """
    Get current user's active relationships
    
    GET /api/relationships/mine
    """
    try:
        current_user = request.current_user
        
        relationships = db.get_user_relationships(current_user['user_id'], status='active')
        
        # Format response
        formatted = []
        for rel in relationships:
            # Determine if current user is user1 or user2
            is_user1 = rel['user1Id'] == current_user['user_id']
            other_user_id = rel['user2Id'] if is_user1 else rel['user1Id']
            other_user_name = rel['user2Name'] if is_user1 else rel['user1Name']
            other_user_roles = rel['user2Roles'] if is_user1 else rel['user1Roles']
            
            formatted.append({
                'id': rel['id'],
                'other_user_id': other_user_id,
                'other_user_name': other_user_name,
                'other_user_roles': other_user_roles,
                'relationship_type': rel.get('relationshipType'),
                'status': rel.get('status'),
                'established_at': rel.get('acceptedAt'),
                'permissions': rel.get('permissions', {})
            })
        
        return jsonify({
            'success': True,
            'relationships': formatted
        }), 200
        
    except Exception as e:
        print(f"Error getting relationships: {e}")
        return jsonify({'error': 'Failed to get relationships', 'detail': str(e)}), 500

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@require_auth(roles=['admin', 'super_user'])
def get_pending_requests():
    """
    Get all pending relationship change requests (admin only)
    
    GET /api/admin/relationship-requests
    """
    try:
        requests = db.get_pending_change_requests()
        
        return jsonify({
            'success': True,
            'requests': requests
        }), 200
        
    except Exception as e:
        print(f"Error getting pending requests: {e}")
        return jsonify({'error': 'Failed to get pending requests', 'detail': str(e)}), 500

@require_auth(roles=['admin', 'super_user'])
def approve_request(request_id):
    """
    Approve a relationship change request (admin only)
    
    POST /api/admin/relationship-requests/{request_id}/approve
    Body: {
        "notes": "Optional approval notes"
    }
    """
    try:
        current_user = request.current_user
        data = request.get_json() or {}
        notes = data.get('notes')
        
        # TODO: Implement logic to get request details and create/modify relationship
        # For now, just update status
        
        db.update_change_request_status(
            request_id=request_id,
            status='approved',
            reviewed_by=current_user['user_id'],
            approval_notes=notes
        )
        
        return jsonify({
            'success': True,
            'message': 'Request approved'
        }), 200
        
    except Exception as e:
        print(f"Error approving request: {e}")
        return jsonify({'error': 'Failed to approve request', 'detail': str(e)}), 500

@require_auth(roles=['admin', 'super_user'])
def reject_request(request_id):
    """
    Reject a relationship change request (admin only)
    
    POST /api/admin/relationship-requests/{request_id}/reject
    Body: {
        "reason": "Rejection reason"
    }
    """
    try:
        current_user = request.current_user
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        db.update_change_request_status(
            request_id=request_id,
            status='rejected',
            reviewed_by=current_user['user_id'],
            rejection_reason=reason
        )
        
        return jsonify({
            'success': True,
            'message': 'Request rejected'
        }), 200
        
    except Exception as e:
        print(f"Error rejecting request: {e}")
        return jsonify({'error': 'Failed to reject request', 'detail': str(e)}), 500
