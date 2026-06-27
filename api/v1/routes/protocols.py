"""
Protocol API routes
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from api.v1.models.protocol import ProtocolRepository, ProtocolConfig, ProtocolStatus
from api.v1.models.protocol_request import ProtocolRequestRepository
from api.v1.schemas.protocol import (
    ProtocolCreateRequest,
    ProtocolUpdateRequest,
    ProtocolResponse,
    ProtocolListResponse,
    ProtocolSubmitRequest,
    ErrorResponse,
)
from api.v1.core.logging import logger
import uuid


router = APIRouter(prefix="/api/v1/protocols", tags=["protocols"])


def get_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Extract user ID from token or session"""
    # TODO: Implement proper token validation
    # For now, extract from Authorization header or use a default
    if authorization:
        # Bearer token format: "Bearer user_id" for demo
        try:
            parts = authorization.split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                return parts[1]
        except:
            pass
    raise HTTPException(status_code=401, detail="Unauthorized")


def get_protocol_repository(db=Depends()) -> ProtocolRepository:
    """Get protocol repository with database client"""
    # TODO: Inject real Firestore or PostgreSQL client
    from api.firestore_db import get_db
    firestore_db = get_db()
    return ProtocolRepository(firestore_db)

def get_protocol_request_repository() -> ProtocolRequestRepository:
    """Get protocol request repository with database client"""
    from api.firestore_db import get_db
    firestore_db = get_db()
    return ProtocolRequestRepository(firestore_db)

@router.post("", response_model=ProtocolResponse)
async def create_protocol(
    request: ProtocolCreateRequest,
    user_id: str = Depends(get_user_id),
    repo: ProtocolRepository = Depends(get_protocol_repository),
):
    """
    Create a new protocol in draft state

    The created protocol starts in draft state and can be edited.
    Once ready, it can be submitted for superadmin approval.
    """
    try:
        correlation_id = logger.info(
            "protocol.create_requested",
            user_id=user_id,
            message=f"Creating protocol: {request.protocol_name}",
        )

        config = ProtocolConfig(
            joints_to_track=request.config.joints_to_track,
            angles_to_measure=request.config.angles_to_measure,
            metrics_to_calculate=request.config.metrics_to_calculate,
            baseline_metrics=request.config.baseline_metrics,
            risk_factors=request.config.risk_factors,
            report_template=request.config.report_template,
            required_views=request.config.required_views,
            expected_duration_seconds=request.config.expected_duration_seconds,
        )

        protocol = repo.create(
            user_id=user_id,
            protocol_name=request.protocol_name,
            description=request.description,
            sport_id=request.sport_id,
            config=config,
        )

        logger.info(
            "protocol.created",
            user_id=user_id,
            entity_type="protocol",
            entity_id=protocol.protocol_id,
            message="Protocol created successfully",
            extra={"correlation_id": correlation_id},
        )

        return ProtocolResponse(**protocol.to_dict())

    except Exception as e:
        logger.error(
            "protocol.create_failed",
            user_id=user_id,
            error_code="CREATE_ERROR",
            message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-drafts", response_model=ProtocolListResponse)
async def list_my_drafts(
    user_id: str = Depends(get_user_id),
    repo: ProtocolRepository = Depends(get_protocol_repository),
):
    """List draft protocols created by the current user"""
    try:
        protocols = repo.list_by_user(user_id, status=ProtocolStatus.DRAFT)
        responses = [ProtocolResponse(**p.to_dict()) for p in protocols]
        return ProtocolListResponse(protocols=responses, count=len(responses))

    except Exception as e:
        logger.error(
            "protocol.list_failed",
            user_id=user_id,
            error_code="LIST_ERROR",
            message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{protocol_id}", response_model=ProtocolResponse)
async def get_protocol(
    protocol_id: str,
    user_id: str = Depends(get_user_id),
    repo: ProtocolRepository = Depends(get_protocol_repository),
):
    """Get protocol by ID"""
    try:
        protocol = repo.get_by_id(protocol_id)
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")

        # Authorization: user can see their own protocols or any approved protocol
        if protocol.created_by != user_id and protocol.status != ProtocolStatus.APPROVED:
            logger.warning(
                "protocol.access_denied",
                user_id=user_id,
                entity_type="protocol",
                entity_id=protocol_id,
                message="User not authorized to view this protocol",
            )
            raise HTTPException(status_code=403, detail="Not authorized to view this protocol")

        return ProtocolResponse(**protocol.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "protocol.get_failed",
            user_id=user_id,
            entity_type="protocol",
            entity_id=protocol_id,
            error_code="GET_ERROR",
            message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{protocol_id}", response_model=ProtocolResponse)
async def update_protocol(
    protocol_id: str,
    request: ProtocolUpdateRequest,
    user_id: str = Depends(get_user_id),
    repo: ProtocolRepository = Depends(get_protocol_repository),
):
    """
    Update a draft protocol

    Only the creator can update the protocol, and only while it is in draft state.
    """
    try:
        protocol = repo.get_by_id(protocol_id)
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")

        if protocol.created_by != user_id:
            logger.warning(
                "protocol.update_denied",
                user_id=user_id,
                entity_type="protocol",
                entity_id=protocol_id,
                message="User not authorized to update this protocol",
            )
            raise HTTPException(status_code=403, detail="Not authorized to update this protocol")

        if protocol.status != ProtocolStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail="Can only update draft protocols",
            )

        updates = {}
        if request.protocol_name:
            updates["protocol_name"] = request.protocol_name
        if request.description:
            updates["description"] = request.description
        if request.config:
            updates["config"] = request.config.dict()

        updated = repo.update(protocol_id, **updates)

        logger.info(
            "protocol.updated",
            user_id=user_id,
            entity_type="protocol",
            entity_id=protocol_id,
            message="Protocol updated",
        )

        return ProtocolResponse(**updated.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "protocol.update_failed",
            user_id=user_id,
            entity_type="protocol",
            entity_id=protocol_id,
            error_code="UPDATE_ERROR",
            message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{protocol_id}/submit", response_model=ProtocolResponse)
async def submit_protocol(
    protocol_id: str,
    request: ProtocolSubmitRequest,
    user_id: str = Depends(get_user_id),
    repo: ProtocolRepository = Depends(get_protocol_repository),
    request_repo: ProtocolRequestRepository = Depends(get_protocol_request_repository),
):
    """
    Submit a draft protocol for superadmin approval

    This transitions the protocol from DRAFT to SUBMITTED state.
    Once submitted, only a superadmin can approve or reject it.
    """
    try:
        protocol = repo.get_by_id(protocol_id)
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")

        if protocol.created_by != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to submit this protocol")

        if protocol.status != ProtocolStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail=f"Can only submit draft protocols; this is {protocol.status}",
            )

        updated = repo.submit(protocol_id, user_id)

        # Create a protocol request for superadmin review
        protocol_request = request_repo.create_from_submission(protocol_id, user_id)

        # TODO: Emit event for superadmin notification
        logger.info(
            "protocol.submitted",
            user_id=user_id,
            entity_type="protocol",
            entity_id=protocol_id,
            extra={"request_id": protocol_request.request_id},
            message="Protocol submitted for approval",
        )

        return ProtocolResponse(**updated.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "protocol.submit_failed",
            user_id=user_id,
            entity_type="protocol",
            entity_id=protocol_id,
            error_code="SUBMIT_ERROR",
            message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))
