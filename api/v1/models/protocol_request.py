"""
Protocol request and approval domain model
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from api.v1.core.logging import logger


class RequestStatus(str, Enum):
    """Request lifecycle states"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ApprovalDecision:
    """Record of an approval or rejection decision"""
    decided_by: str
    decision: RequestStatus
    reason: Optional[str]
    decided_at: datetime

    def to_dict(self) -> Dict:
        return {
            "decided_by": self.decided_by,
            "decision": self.decision.value,
            "reason": self.reason,
            "decided_at": self.decided_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ApprovalDecision":
        return cls(
            decided_by=data["decided_by"],
            decision=RequestStatus(data["decision"]),
            reason=data.get("reason"),
            decided_at=datetime.fromisoformat(data["decided_at"].replace("Z", "+00:00")),
        )


@dataclass
class ProtocolRequest:
    """Request to approve or reject a protocol"""
    request_id: str
    protocol_id: str
    requested_by: str
    status: RequestStatus
    created_at: datetime
    decision: Optional[ApprovalDecision] = None

    def to_dict(self) -> Dict:
        return {
            "request_id": self.request_id,
            "protocol_id": self.protocol_id,
            "requested_by": self.requested_by,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "decision": self.decision.to_dict() if self.decision else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ProtocolRequest":
        decision = None
        if data.get("decision"):
            decision = ApprovalDecision.from_dict(data["decision"])

        return cls(
            request_id=data["request_id"],
            protocol_id=data["protocol_id"],
            requested_by=data["requested_by"],
            status=RequestStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            decision=decision,
        )


class ProtocolRequestRepository:
    """
    Repository for protocol request persistence
    """

    COLLECTION = "protocol_requests_v1"

    def __init__(self, db):
        """
        Initialize repository

        Args:
            db: Firestore client
        """
        self.db = db
        self.collection_ref = db.collection(self.COLLECTION)

    def create_from_submission(self, protocol_id: str, requested_by: str) -> ProtocolRequest:
        """
        Create a request when a protocol is submitted

        Args:
            protocol_id: ID of protocol being requested
            requested_by: ID of user submitting the request

        Returns:
            Created ProtocolRequest
        """
        request_id = str(uuid.uuid4())
        now = datetime.utcnow()

        request = ProtocolRequest(
            request_id=request_id,
            protocol_id=protocol_id,
            requested_by=requested_by,
            status=RequestStatus.PENDING,
            created_at=now,
        )

        self.collection_ref.document(request_id).set(request.to_dict())

        logger.info(
            "protocol_request.created",
            user_id=requested_by,
            entity_type="protocol_request",
            entity_id=request_id,
            extra={"protocol_id": protocol_id},
            message="Protocol request created",
        )

        return request

    def get_by_id(self, request_id: str) -> Optional[ProtocolRequest]:
        """Get request by ID"""
        doc = self.collection_ref.document(request_id).get()
        if doc.exists:
            return ProtocolRequest.from_dict(doc.to_dict())
        return None

    def list_pending(self) -> List[ProtocolRequest]:
        """List all pending protocol requests"""
        docs = self.collection_ref.where("status", "==", RequestStatus.PENDING.value).stream()
        requests = [ProtocolRequest.from_dict(doc.to_dict()) for doc in docs]
        return sorted(requests, key=lambda r: r.created_at, reverse=True)

    def list_by_status(self, status: RequestStatus) -> List[ProtocolRequest]:
        """List requests by status"""
        docs = self.collection_ref.where("status", "==", status.value).stream()
        return [ProtocolRequest.from_dict(doc.to_dict()) for doc in docs]

    def approve(self, request_id: str, approver_id: str, reason: Optional[str] = None) -> ProtocolRequest:
        """
        Approve a protocol request

        Args:
            request_id: Request ID
            approver_id: ID of superadmin approving
            reason: Optional approval reason

        Returns:
            Updated ProtocolRequest
        """
        request = self.get_by_id(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")

        if request.status != RequestStatus.PENDING:
            raise ValueError(f"Can only approve pending requests; this is {request.status}")

        now = datetime.utcnow()
        decision = ApprovalDecision(
            decided_by=approver_id,
            decision=RequestStatus.APPROVED,
            reason=reason,
            decided_at=now,
        )

        self.collection_ref.document(request_id).update({
            "status": RequestStatus.APPROVED.value,
            "decision": decision.to_dict(),
        })

        logger.info(
            "protocol_request.approved",
            user_id=approver_id,
            entity_type="protocol_request",
            entity_id=request_id,
            message="Protocol request approved",
        )

        return self.get_by_id(request_id)

    def reject(self, request_id: str, approver_id: str, reason: str) -> ProtocolRequest:
        """
        Reject a protocol request

        Args:
            request_id: Request ID
            approver_id: ID of superadmin rejecting
            reason: Rejection reason

        Returns:
            Updated ProtocolRequest
        """
        request = self.get_by_id(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")

        if request.status != RequestStatus.PENDING:
            raise ValueError(f"Can only reject pending requests; this is {request.status}")

        now = datetime.utcnow()
        decision = ApprovalDecision(
            decided_by=approver_id,
            decision=RequestStatus.REJECTED,
            reason=reason,
            decided_at=now,
        )

        self.collection_ref.document(request_id).update({
            "status": RequestStatus.REJECTED.value,
            "decision": decision.to_dict(),
        })

        logger.info(
            "protocol_request.rejected",
            user_id=approver_id,
            entity_type="protocol_request",
            entity_id=request_id,
            message="Protocol request rejected",
        )

        return self.get_by_id(request_id)

    def get_by_protocol_id(self, protocol_id: str) -> Optional[ProtocolRequest]:
        """Get request by protocol ID (most recent)"""
        docs = self.collection_ref.where("protocol_id", "==", protocol_id).order_by("created_at", direction="DESCENDING").limit(1).stream()
        for doc in docs:
            return ProtocolRequest.from_dict(doc.to_dict())
        return None
