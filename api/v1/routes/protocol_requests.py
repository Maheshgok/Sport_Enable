"""
Protocol request API routes for superadmin approval workflow
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from api.v1.models.protocol import ProtocolRepository, ProtocolStatus
from api.v1.models.protocol_request import ProtocolRequestRepository, RequestStatus
from api.v1.schemas.protocol_request import (
    ProtocolRequestListResponse,
    ProtocolRequestResponse,
    ApprovalDecisionSchema,
    ApproveRequest,
    RejectRequest,
)
from api.v1.core.logging import logger


router = APIRouter(prefix="/api/v1/protocol-requests", tags=["protocol-requests"])


def get_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Extract user ID from token"""
    if authorization:
        try:
            parts = authorization.split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                return parts[1]
        except:
            pass
    raise HTTPException(status_code=401, detail="Unauthorized")


def get_request_repository(db=Depends()) -> ProtocolRequestRepository:
    """Get protocol request repository"""
    from api.firestore_db import get_db
    firestore_db = get_db()
    return ProtocolRequestRepository(firestore_db)


def get_protocol_repository(db=Depends()) -> ProtocolRepository:
    """Get protocol repository"""
    from api.firestore_db import get_db
    firestore_db = get_db()
    return ProtocolRepository(firestore_db)


def require_superadmin(user_id: str = Depends(get_user_id)):
    """Require superadmin role"""
    # TODO: Implement proper role checking
    # For now, just require a user ID
    return user_id


@router.get("/pending", response_model=ProtocolRequestListResponse)
async def list_pending_requests(
    user_id: str = Depends(require_superadmin),
    repo: ProtocolRequestRepository = Depends(get_request_repository),
):
    """
    List all pending protocol requests

    Only superadmins can view this.
    """
    try:
        logger.info(
            "protocol_requests.list_pending",
            user_id=user_id,
            message="Fetching pending protocol requests",
        )

        requests = repo.list_pending()
        responses = [
            ProtocolRequestResponse(
                request_id=r.request_id,
                protocol_id=r.protocol_id,
                requested_by=r.requested_by,
                status=r.status.value,
                created_at=r.created_at.isoformat(),
                decision=ApprovalDecisionSchema(**r.decision.to_dict()) if r.decision else None,
            )
            for r in requests
        ]

        return ProtocolRequestListResponse(requests=responses, count=len(responses))

    except Exception as e:
        logger.error(
            "protocol_requests.list_failed",
            user_id=user_id,
            error_code="LIST_ERROR",
            message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{request_id}", response_model=ProtocolRequestResponse)
async def get_request(
    request_id: str,
    user_id: str = Depends(require_superadmin),
    repo: ProtocolRequestRepository = Depends(get_request_repository),
):
    """Get protocol request by ID"""
    try:
        request = repo.get_by_id(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        return ProtocolRequestResponse(
            request_id=request.request_id,
            protocol_id=request.protocol_id,
            requested_by=request.requested_by,
            status=request.status.value,
            created_at=request.created_at.isoformat(),
            decision=ApprovalDecisionSchema(**request.decision.to_dict()) if request.decision else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "protocol_request.get_failed",
            user_id=user_id,
            entity_type="protocol_request",
            entity_id=request_id,
            error_code="GET_ERROR",
            message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{request_id}/approve", response_model=ProtocolRequestResponse)
async def approve_request(
    request_id: str,
    body: ApproveRequest,
    user_id: str = Depends(require_superadmin),
    request_repo: ProtocolRequestRepository = Depends(get_request_repository),
    protocol_repo: ProtocolRepository = Depends(get_protocol_repository),
):
    """
    Approve a protocol request

    This:
    1. Approves the request
    2. Updates the protocol status to APPROVED
    3. Makes the protocol visible to coaches and athletes
    """
    try:
        protocol_request = request_repo.get_by_id(request_id)
        if not protocol_request:
            raise HTTPException(status_code=404, detail="Request not found")

        if protocol_request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Can only approve pending requests; this is {protocol_request.status}",
            )

        # Approve the request
        updated_request = request_repo.approve(request_id, user_id, reason=body.reason)

        # Update protocol status to APPROVED
        protocol = protocol_repo.get_by_id(protocol_request.protocol_id)
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")

        protocol_repo.approve(protocol_request.protocol_id, user_id)

        # TODO: Emit notification event for physiotherapist

        logger.info(
            "protocol_request.approved",
            user_id=user_id,
            entity_type="protocol_request",
            entity_id=request_id,
            extra={"protocol_id": protocol_request.protocol_id},
            message="Protocol approved and published",
        )

        return ProtocolRequestResponse(
            request_id=updated_request.request_id,
            protocol_id=updated_request.protocol_id,
            requested_by=updated_request.requested_by,
            status=updated_request.status.value,
            created_at=updated_request.created_at.isoformat(),
            decision=ApprovalDecisionSchema(**updated_request.decision.to_dict()) if updated_request.decision else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "protocol_request.approve_failed",
            user_id=user_id,
            entity_type="protocol_request",
            entity_id=request_id,
            error_code="APPROVE_ERROR",
            message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{request_id}/reject", response_model=ProtocolRequestResponse)
async def reject_request(
    request_id: str,
    body: RejectRequest,
    user_id: str = Depends(require_superadmin),
    request_repo: ProtocolRequestRepository = Depends(get_request_repository),
):
    """
    Reject a protocol request

    The protocol remains in SUBMITTED state and is not published.
    The physiotherapist can edit and resubmit.
    """
    try:
        protocol_request = request_repo.get_by_id(request_id)
        if not protocol_request:
            raise HTTPException(status_code=404, detail="Request not found")

        if protocol_request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Can only reject pending requests; this is {protocol_request.status}",
            )

        updated_request = request_repo.reject(request_id, user_id, reason=body.reason)

        # TODO: Emit notification event for physiotherapist

        logger.info(
            "protocol_request.rejected",
            user_id=user_id,
            entity_type="protocol_request",
            entity_id=request_id,
            extra={"reason": body.reason},
            message="Protocol request rejected",
        )

        return ProtocolRequestResponse(
            request_id=updated_request.request_id,
            protocol_id=updated_request.protocol_id,
            requested_by=updated_request.requested_by,
            status=updated_request.status.value,
            created_at=updated_request.created_at.isoformat(),
            decision=ApprovalDecisionSchema(**updated_request.decision.to_dict()) if updated_request.decision else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "protocol_request.reject_failed",
            user_id=user_id,
            entity_type="protocol_request",
            entity_id=request_id,
            error_code="REJECT_ERROR",
            message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))
