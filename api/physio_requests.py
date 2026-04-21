"""
Physiotherapist Request System API Endpoints
Handles exercise and baseline measurement requests that require admin approval
"""

from flask import request, jsonify
from auth import require_auth, is_super_user
import firestore_db as db

# ============================================================================
# PHYSIOTHERAPIST ENDPOINTS
# ============================================================================

@require_auth(roles=['physiotherapist', 'admin'])
def submit_exercise_request():
    """
    Submit a new exercise request
    POST /api/physio/request-exercise
    """
    try:
        data = request.json
        user_id = request.current_user['user_id']
        
        # Validate required fields
        required_fields = ['exerciseName', 'description', 'category', 'instructions']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create request
        request_doc = db.create_exercise_request(user_id, data)
        
        return jsonify({
            'success': True,
            'requestId': request_doc['requestId'],
            'status': 'pending',
            'message': 'Exercise request submitted successfully. An admin will review it soon.'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error submitting exercise request: {e}")
        return jsonify({'error': 'Failed to submit request'}), 500

@require_auth(roles=['physiotherapist', 'admin'])
def submit_baseline_request():
    """
    Submit a new baseline measurement request
    POST /api/physio/request-baseline
    """
    try:
        data = request.json
        user_id = request.current_user['user_id']
        
        # Validate required fields
        required_fields = ['measurementName', 'measurementType', 'unit', 'sportId', 'sportName']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create request
        request_doc = db.create_baseline_request(user_id, data)
        
        return jsonify({
            'success': True,
            'requestId': request_doc['requestId'],
            'status': 'pending',
            'message': 'Baseline measurement request submitted successfully. An admin will review it soon.'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error submitting baseline request: {e}")
        return jsonify({'error': 'Failed to submit request'}), 500

@require_auth(roles=['physiotherapist', 'admin'])
def get_my_requests():
    """
    Get all requests submitted by the current user
    GET /api/physio/my-requests?type=all|exercise|baseline&status=pending|approved|rejected
    """
    try:
        user_id = request.current_user['user_id']
        request_type = request.args.get('type', 'all')
        status = request.args.get('status', None)
        
        # Validate request type
        if request_type not in ['all', 'exercise', 'baseline']:
            return jsonify({'error': 'Invalid request type'}), 400
        
        # Get requests
        requests = db.get_user_requests(user_id, request_type, status)
        
        return jsonify({
            'success': True,
            'exerciseRequests': requests['exerciseRequests'],
            'baselineRequests': requests['baselineRequests'],
            'totalCount': len(requests['exerciseRequests']) + len(requests['baselineRequests'])
        }), 200
        
    except Exception as e:
        print(f"Error getting user requests: {e}")
        return jsonify({'error': 'Failed to retrieve requests'}), 500

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@require_auth(roles=['admin'])
def get_all_pending_requests():
    """
    Get all pending requests (admin only)
    GET /api/admin/requests/pending?type=all|exercise|baseline
    """
    try:
        request_type = request.args.get('type', 'all')
        
        # Validate request type
        if request_type not in ['all', 'exercise', 'baseline']:
            return jsonify({'error': 'Invalid request type'}), 400
        
        # Get pending requests
        requests = db.get_all_requests(request_type, status='pending')
        
        return jsonify({
            'success': True,
            'exerciseRequests': requests['exerciseRequests'],
            'baselineRequests': requests['baselineRequests'],
            'totalCount': len(requests['exerciseRequests']) + len(requests['baselineRequests'])
        }), 200
        
    except Exception as e:
        print(f"Error getting pending requests: {e}")
        return jsonify({'error': 'Failed to retrieve requests'}), 500

@require_auth(roles=['admin'])
def get_all_requests_admin():
    """
    Get all requests with optional filters (admin only)
    GET /api/admin/requests?type=all|exercise|baseline&status=all|pending|approved|rejected
    """
    try:
        request_type = request.args.get('type', 'all')
        status = request.args.get('status', None)
        
        # Validate request type
        if request_type not in ['all', 'exercise', 'baseline']:
            return jsonify({'error': 'Invalid request type'}), 400
        
        # If status is 'all', set to None to get all statuses
        if status == 'all':
            status = None
        
        # Get requests
        requests = db.get_all_requests(request_type, status)
        
        return jsonify({
            'success': True,
            'exerciseRequests': requests['exerciseRequests'],
            'baselineRequests': requests['baselineRequests'],
            'totalCount': len(requests['exerciseRequests']) + len(requests['baselineRequests'])
        }), 200
        
    except Exception as e:
        print(f"Error getting all requests: {e}")
        return jsonify({'error': 'Failed to retrieve requests'}), 500

@require_auth(roles=['admin'])
def approve_exercise_request(request_id):
    """
    Approve an exercise request
    POST /api/admin/requests/exercise/<request_id>/approve
    """
    try:
        data = request.json or {}
        admin_id = request.current_user['user_id']
        
        review_notes = data.get('reviewNotes', '')
        add_to_library = data.get('addToLibrary', True)
        
        # Get the request details
        request_doc = db.get_request_by_id(request_id, 'exercise')
        if not request_doc:
            return jsonify({'error': 'Request not found'}), 404
        
        if request_doc['status'] != 'pending':
            return jsonify({'error': f'Request already {request_doc["status"]}'}), 400
        
        # TODO: If addToLibrary is True, create exercise in library
        # For now, we'll just approve the request without adding to library
        approved_exercise_id = None
        if add_to_library:
            # Future: Create exercise in exercise library collection
            # approved_exercise_id = create_exercise_in_library(request_doc)
            review_notes += " [Note: Exercise library integration pending]"
        
        # Update request status
        success = db.update_exercise_request_status(
            request_id, 
            'approved', 
            admin_id, 
            review_notes,
            approved_exercise_id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Exercise request approved',
                'exerciseId': approved_exercise_id
            }), 200
        else:
            return jsonify({'error': 'Failed to update request'}), 500
        
    except Exception as e:
        print(f"Error approving exercise request: {e}")
        return jsonify({'error': 'Failed to approve request'}), 500

@require_auth(roles=['admin'])
def approve_baseline_request(request_id):
    """
    Approve a baseline measurement request
    POST /api/admin/requests/baseline/<request_id>/approve
    """
    try:
        data = request.json or {}
        admin_id = request.current_user['user_id']
        
        review_notes = data.get('reviewNotes', '')
        
        # Get the request details
        request_doc = db.get_request_by_id(request_id, 'baseline')
        if not request_doc:
            return jsonify({'error': 'Request not found'}), 404
        
        if request_doc['status'] != 'pending':
            return jsonify({'error': f'Request already {request_doc["status"]}'}), 400
        
        # TODO: Add baseline to sports_config.py or Firestore
        # For now, just approve the request
        review_notes += " [Note: Baseline integration with sports config pending]"
        
        # Update request status
        success = db.update_baseline_request_status(
            request_id, 
            'approved', 
            admin_id, 
            review_notes
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Baseline measurement request approved'
            }), 200
        else:
            return jsonify({'error': 'Failed to update request'}), 500
        
    except Exception as e:
        print(f"Error approving baseline request: {e}")
        return jsonify({'error': 'Failed to approve request'}), 500

@require_auth(roles=['admin'])
def reject_request(request_id):
    """
    Reject a request (exercise or baseline)
    POST /api/admin/requests/<request_id>/reject
    Body: { requestType: 'exercise'|'baseline', reviewNotes: 'reason' }
    """
    try:
        data = request.json
        admin_id = request.current_user['user_id']
        
        if not data.get('requestType'):
            return jsonify({'error': 'requestType is required'}), 400
        
        if not data.get('reviewNotes'):
            return jsonify({'error': 'reviewNotes is required for rejection'}), 400
        
        request_type = data['requestType']
        review_notes = data['reviewNotes']
        
        # Validate request type
        if request_type not in ['exercise', 'baseline']:
            return jsonify({'error': 'Invalid request type'}), 400
        
        # Get the request to verify it exists
        request_doc = db.get_request_by_id(request_id, request_type)
        if not request_doc:
            return jsonify({'error': 'Request not found'}), 404
        
        if request_doc['status'] != 'pending':
            return jsonify({'error': f'Request already {request_doc["status"]}'}), 400
        
        # Update request status
        if request_type == 'exercise':
            success = db.update_exercise_request_status(
                request_id, 
                'rejected', 
                admin_id, 
                review_notes
            )
        else:
            success = db.update_baseline_request_status(
                request_id, 
                'rejected', 
                admin_id, 
                review_notes
            )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Request rejected'
            }), 200
        else:
            return jsonify({'error': 'Failed to update request'}), 500
        
    except Exception as e:
        print(f"Error rejecting request: {e}")
        return jsonify({'error': 'Failed to reject request'}), 500

@require_auth()
def get_request_details(request_id):
    """
    Get details of a specific request
    GET /api/requests/<request_id>?type=exercise|baseline
    """
    try:
        request_type = request.args.get('type')
        
        if not request_type or request_type not in ['exercise', 'baseline']:
            return jsonify({'error': 'Valid request type parameter is required'}), 400
        
        # Get request
        request_doc = db.get_request_by_id(request_id, request_type)
        
        if not request_doc:
            return jsonify({'error': 'Request not found'}), 404
        
        # Check permissions: user can see their own requests, admins can see all
        user_id = request.current_user['user_id']
        user_roles = request.current_user.get('roles', [])
        
        if request_doc['requestedBy'] != user_id and not is_super_user(user_roles):
            return jsonify({'error': 'Permission denied'}), 403
        
        return jsonify({
            'success': True,
            'request': request_doc
        }), 200
        
    except Exception as e:
        print(f"Error getting request details: {e}")
        return jsonify({'error': 'Failed to retrieve request'}), 500
