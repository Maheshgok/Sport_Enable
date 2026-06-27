"""
Flask-compatible protocol routes (Sprint 1 & 2)
Wraps v1 models and schemas with Flask route handlers
"""

from flask import request, jsonify
import uuid
from datetime import datetime
from api.v1.models.protocol import ProtocolRepository, ProtocolStatus, ProtocolConfig
from api.v1.models.protocol_request import ProtocolRequestRepository, RequestStatus
from api.v1.schemas.protocol import (
    ProtocolCreateRequest,
    ProtocolUpdateRequest,
)
from api.v1.core.logging import logger


def register_protocol_routes(app, db):
    """
    Register protocol v1 endpoints on Flask app
    
    Args:
        app: Flask application instance
        db: Firestore database client
    """
    
    protocol_repo = ProtocolRepository(db)
    request_repo = ProtocolRequestRepository(db)
    
    def get_user_from_auth():
        """Extract user ID from Authorization header"""
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None
    
    # ============================================
    # PROTOCOL ENDPOINTS (Physiotherapist)
    # ============================================
    
    @app.route('/api/v1/protocols', methods=['POST'])
    def create_protocol():
        """Create a new protocol in draft state"""
        try:
            user_id = get_user_from_auth()
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            data = request.get_json()
            
            # Validate required fields
            required = ['protocol_name', 'description', 'sport_id', 'config']
            if not all(k in data for k in required):
                return jsonify({'error': 'Missing required fields'}), 400
            
            config_data = data['config']
            config = ProtocolConfig(
                joints_to_track=config_data.get('joints_to_track', []),
                angles_to_measure=config_data.get('angles_to_measure', []),
                metrics_to_calculate=config_data.get('metrics_to_calculate', []),
                baseline_metrics=config_data.get('baseline_metrics', {}),
                risk_factors=config_data.get('risk_factors', {}),
                report_template=config_data.get('report_template', {}),
                required_views=config_data.get('required_views', []),
                expected_duration_seconds=config_data.get('expected_duration_seconds', 30),
            )
            
            protocol = protocol_repo.create(
                user_id=user_id,
                protocol_name=data['protocol_name'],
                description=data['description'],
                sport_id=data['sport_id'],
                config=config,
            )
            
            return jsonify(protocol.to_dict()), 201
        
        except Exception as e:
            logger.error(
                'protocol.create_failed',
                user_id=get_user_from_auth(),
                error_code='CREATE_ERROR',
                message=str(e),
            )
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/v1/protocols/my-drafts', methods=['GET'])
    def list_my_drafts():
        """List user's draft protocols"""
        try:
            user_id = get_user_from_auth()
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            protocols = protocol_repo.list_by_user(user_id, status=ProtocolStatus.DRAFT)
            
            return jsonify({
                'protocols': [p.to_dict() for p in protocols],
                'count': len(protocols),
            }), 200
        
        except Exception as e:
            logger.error(
                'protocol.list_drafts_failed',
                user_id=get_user_from_auth(),
                error_code='LIST_ERROR',
                message=str(e),
            )
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/v1/protocols/<protocol_id>', methods=['GET'])
    def get_protocol(protocol_id):
        """Get protocol by ID"""
        try:
            user_id = get_user_from_auth()
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            protocol = protocol_repo.get_by_id(protocol_id)
            if not protocol:
                return jsonify({'error': 'Protocol not found'}), 404
            
            # Authorization: creator can view own protocols, others can only view APPROVED
            if protocol.created_by != user_id and protocol.status != ProtocolStatus.APPROVED:
                return jsonify({'error': 'Not authorized'}), 403
            
            return jsonify(protocol.to_dict()), 200
        
        except Exception as e:
            logger.error(
                'protocol.get_failed',
                user_id=get_user_from_auth(),
                entity_type='protocol',
                entity_id=protocol_id,
                error_code='GET_ERROR',
                message=str(e),
            )
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/v1/protocols/<protocol_id>', methods=['PUT'])
    def update_protocol(protocol_id):
        """Update draft protocol"""
        try:
            user_id = get_user_from_auth()
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            protocol = protocol_repo.get_by_id(protocol_id)
            if not protocol:
                return jsonify({'error': 'Protocol not found'}), 404
            
            # Authorization: only creator can edit
            if protocol.created_by != user_id:
                return jsonify({'error': 'Not authorized'}), 403
            
            # Can only edit drafts
            if protocol.status != ProtocolStatus.DRAFT:
                return jsonify({
                    'error': f'Can only edit draft protocols; this is {protocol.status}'
                }), 400
            
            data = request.get_json()
            updates = {}
            
            if 'protocol_name' in data:
                updates['protocol_name'] = data['protocol_name']
            if 'description' in data:
                updates['description'] = data['description']
            if 'config' in data:
                config_data = data['config']
                config = ProtocolConfig(
                    joints_to_track=config_data.get('joints_to_track', []),
                    angles_to_measure=config_data.get('angles_to_measure', []),
                    metrics_to_calculate=config_data.get('metrics_to_calculate', []),
                    baseline_metrics=config_data.get('baseline_metrics', {}),
                    risk_factors=config_data.get('risk_factors', {}),
                    report_template=config_data.get('report_template', {}),
                    required_views=config_data.get('required_views', []),
                    expected_duration_seconds=config_data.get('expected_duration_seconds', 30),
                )
                updates['config'] = config
            
            updated = protocol_repo.update(protocol_id, **updates)
            
            return jsonify(updated.to_dict()), 200
        
        except Exception as e:
            logger.error(
                'protocol.update_failed',
                user_id=get_user_from_auth(),
                entity_type='protocol',
                entity_id=protocol_id,
                error_code='UPDATE_ERROR',
                message=str(e),
            )
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/v1/protocols/<protocol_id>/submit', methods=['POST'])
    def submit_protocol(protocol_id):
        """Submit protocol for approval"""
        try:
            user_id = get_user_from_auth()
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            protocol = protocol_repo.get_by_id(protocol_id)
            if not protocol:
                return jsonify({'error': 'Protocol not found'}), 404
            
            # Authorization: only creator can submit
            if protocol.created_by != user_id:
                return jsonify({'error': 'Not authorized'}), 403
            
            # Can only submit drafts
            if protocol.status != ProtocolStatus.DRAFT:
                return jsonify({
                    'error': f'Can only submit draft protocols; this is {protocol.status}'
                }), 400
            
            # Submit protocol and create request
            updated = protocol_repo.submit(protocol_id, user_id)
            protocol_request = request_repo.create_from_submission(protocol_id, user_id)
            
            logger.info(
                'protocol.submitted',
                user_id=user_id,
                entity_type='protocol',
                entity_id=protocol_id,
                extra={'request_id': protocol_request.request_id},
                message='Protocol submitted for approval',
            )
            
            return jsonify(updated.to_dict()), 200
        
        except Exception as e:
            logger.error(
                'protocol.submit_failed',
                user_id=get_user_from_auth(),
                entity_type='protocol',
                entity_id=protocol_id,
                error_code='SUBMIT_ERROR',
                message=str(e),
            )
            return jsonify({'error': str(e)}), 500
    
    
    # ============================================
    # PROTOCOL REQUEST ENDPOINTS (Superadmin)
    # ============================================
    
    @app.route('/api/v1/protocol-requests/pending', methods=['GET'])
    def list_pending_requests():
        """List pending protocol requests (superadmin only)"""
        try:
            user_id = get_user_from_auth()
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            # TODO: Check superadmin role
            
            requests = request_repo.list_pending()
            
            return jsonify({
                'requests': [r.to_dict() for r in requests],
                'count': len(requests),
            }), 200
        
        except Exception as e:
            logger.error(
                'protocol_requests.list_failed',
                user_id=get_user_from_auth(),
                error_code='LIST_ERROR',
                message=str(e),
            )
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/v1/protocol-requests/<request_id>', methods=['GET'])
    def get_request(request_id):
        """Get protocol request by ID"""
        try:
            user_id = get_user_from_auth()
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            protocol_request = request_repo.get_by_id(request_id)
            if not protocol_request:
                return jsonify({'error': 'Request not found'}), 404
            
            return jsonify(protocol_request.to_dict()), 200
        
        except Exception as e:
            logger.error(
                'protocol_request.get_failed',
                user_id=get_user_from_auth(),
                entity_type='protocol_request',
                entity_id=request_id,
                error_code='GET_ERROR',
                message=str(e),
            )
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/v1/protocol-requests/<request_id>/approve', methods=['POST'])
    def approve_request(request_id):
        """Approve a protocol request"""
        try:
            user_id = get_user_from_auth()
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            protocol_request = request_repo.get_by_id(request_id)
            if not protocol_request:
                return jsonify({'error': 'Request not found'}), 404
            
            if protocol_request.status != RequestStatus.PENDING:
                return jsonify({
                    'error': f'Can only approve pending requests; this is {protocol_request.status}'
                }), 400
            
            data = request.get_json() or {}
            reason = data.get('reason')
            
            # Approve request
            updated_request = request_repo.approve(request_id, user_id, reason=reason)
            
            # Approve protocol
            protocol = protocol_repo.get_by_id(protocol_request.protocol_id)
            if protocol:
                protocol_repo.approve(protocol_request.protocol_id, user_id)
            
            logger.info(
                'protocol_request.approved',
                user_id=user_id,
                entity_type='protocol_request',
                entity_id=request_id,
                extra={'protocol_id': protocol_request.protocol_id},
                message='Protocol approved and published',
            )
            
            return jsonify(updated_request.to_dict()), 200
        
        except Exception as e:
            logger.error(
                'protocol_request.approve_failed',
                user_id=get_user_from_auth(),
                entity_type='protocol_request',
                entity_id=request_id,
                error_code='APPROVE_ERROR',
                message=str(e),
            )
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/v1/protocol-requests/<request_id>/reject', methods=['POST'])
    def reject_request(request_id):
        """Reject a protocol request"""
        try:
            user_id = get_user_from_auth()
            if not user_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            data = request.get_json()
            if not data or 'reason' not in data:
                return jsonify({'error': 'Reason required'}), 400
            
            protocol_request = request_repo.get_by_id(request_id)
            if not protocol_request:
                return jsonify({'error': 'Request not found'}), 404
            
            if protocol_request.status != RequestStatus.PENDING:
                return jsonify({
                    'error': f'Can only reject pending requests; this is {protocol_request.status}'
                }), 400
            
            updated_request = request_repo.reject(request_id, user_id, reason=data['reason'])
            
            logger.info(
                'protocol_request.rejected',
                user_id=user_id,
                entity_type='protocol_request',
                entity_id=request_id,
                extra={'reason': data['reason']},
                message='Protocol request rejected',
            )
            
            return jsonify(updated_request.to_dict()), 200
        
        except Exception as e:
            logger.error(
                'protocol_request.reject_failed',
                user_id=get_user_from_auth(),
                entity_type='protocol_request',
                entity_id=request_id,
                error_code='REJECT_ERROR',
                message=str(e),
            )
            return jsonify({'error': str(e)}), 500
