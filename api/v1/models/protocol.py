"""
Protocol domain model and data layer
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from api.v1.core.logging import logger


class ProtocolStatus(str, Enum):
    """Protocol lifecycle states"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ARCHIVED = "archived"


@dataclass
class ProtocolConfig:
    """Analysis configuration for a protocol"""
    joints_to_track: List[str]
    angles_to_measure: List[str]
    metrics_to_calculate: List[str]
    baseline_metrics: Dict[str, Any]
    risk_factors: Dict[str, Any]
    report_template: Dict[str, Any]
    required_views: List[str] = None
    expected_duration_seconds: int = 30

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ProtocolConfig":
        return cls(**data)


@dataclass
class Protocol:
    """Protocol domain entity"""
    protocol_id: str
    protocol_name: str
    description: str
    sport_id: str
    created_by: str
    status: ProtocolStatus
    config: ProtocolConfig
    created_at: datetime
    updated_at: datetime
    version: int = 1

    def to_dict(self) -> Dict:
        return {
            "protocol_id": self.protocol_id,
            "protocol_name": self.protocol_name,
            "description": self.description,
            "sport_id": self.sport_id,
            "created_by": self.created_by,
            "status": self.status.value,
            "config": self.config.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Protocol":
        data["status"] = ProtocolStatus(data["status"])
        data["config"] = ProtocolConfig.from_dict(data["config"])
        data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        data["updated_at"] = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        return cls(**data)


class ProtocolRepository:
    """
    Repository for protocol persistence

    Uses Firestore as the backing store.
    Can be migrated to PostgreSQL later.
    """

    COLLECTION = "protocols_v1"

    def __init__(self, db):
        """
        Initialize repository

        Args:
            db: Firestore client
        """
        self.db = db
        self.collection_ref = db.collection(self.COLLECTION)

    def create(self, user_id: str, protocol_name: str, description: str,
               sport_id: str, config: ProtocolConfig) -> Protocol:
        """
        Create a new protocol in draft state

        Args:
            user_id: ID of physiotherapist creating protocol
            protocol_name: Protocol name
            description: Protocol description
            sport_id: Sport ID
            config: ProtocolConfig with analysis details

        Returns:
            Created Protocol
        """
        protocol_id = str(uuid.uuid4())
        now = datetime.utcnow()

        protocol = Protocol(
            protocol_id=protocol_id,
            protocol_name=protocol_name,
            description=description,
            sport_id=sport_id,
            created_by=user_id,
            status=ProtocolStatus.DRAFT,
            config=config,
            created_at=now,
            updated_at=now,
            version=1,
        )

        self.collection_ref.document(protocol_id).set(protocol.to_dict())

        logger.info(
            "protocol.created",
            user_id=user_id,
            entity_type="protocol",
            entity_id=protocol_id,
            message=f"Protocol '{protocol_name}' created in draft state",
        )

        return protocol

    def get_by_id(self, protocol_id: str) -> Optional[Protocol]:
        """Get protocol by ID"""
        doc = self.collection_ref.document(protocol_id).get()
        if doc.exists:
            return Protocol.from_dict(doc.to_dict())
        return None

    def list_by_user(self, user_id: str, status: Optional[ProtocolStatus] = None) -> List[Protocol]:
        """
        List protocols created by a user

        Args:
            user_id: User ID to filter by
            status: Optional status to filter by

        Returns:
            List of Protocol objects
        """
        query = self.collection_ref.where("created_by", "==", user_id)

        if status:
            query = query.where("status", "==", status.value)

        docs = query.stream()
        return [Protocol.from_dict(doc.to_dict()) for doc in docs]

    def update(self, protocol_id: str, **fields) -> Protocol:
        """
        Update protocol fields

        Args:
            protocol_id: Protocol ID to update
            **fields: Fields to update

        Returns:
            Updated Protocol
        """
        protocol = self.get_by_id(protocol_id)
        if not protocol:
            raise ValueError(f"Protocol {protocol_id} not found")

        fields["updated_at"] = datetime.utcnow().isoformat() + "Z"

        self.collection_ref.document(protocol_id).update(fields)

        logger.info(
            "protocol.updated",
            entity_type="protocol",
            entity_id=protocol_id,
            message=f"Protocol updated with fields: {list(fields.keys())}",
        )

        return self.get_by_id(protocol_id)

    def submit(self, protocol_id: str, user_id: str) -> Protocol:
        """
        Transition protocol from draft to submitted

        Args:
            protocol_id: Protocol ID
            user_id: User submitting (must be creator)

        Returns:
            Updated Protocol
        """
        protocol = self.get_by_id(protocol_id)
        if not protocol:
            raise ValueError(f"Protocol {protocol_id} not found")

        if protocol.created_by != user_id:
            raise ValueError(f"User {user_id} cannot submit protocol created by {protocol.created_by}")

        if protocol.status != ProtocolStatus.DRAFT:
            raise ValueError(f"Can only submit draft protocols; this is {protocol.status}")

        updated = self.update(protocol_id, status=ProtocolStatus.SUBMITTED.value)

        logger.info(
            "protocol.submitted",
            user_id=user_id,
            entity_type="protocol",
            entity_id=protocol_id,
            message="Protocol submitted for approval",
        )

        return updated

    def approve(self, protocol_id: str, approver_id: str) -> Protocol:
        """
        Approve a submitted protocol

        Args:
            protocol_id: Protocol ID
            approver_id: ID of approving superadmin

        Returns:
            Updated Protocol
        """
        protocol = self.get_by_id(protocol_id)
        if not protocol:
            raise ValueError(f"Protocol {protocol_id} not found")

        if protocol.status != ProtocolStatus.SUBMITTED:
            raise ValueError(f"Can only approve submitted protocols; this is {protocol.status}")

        updated = self.update(
            protocol_id,
            status=ProtocolStatus.APPROVED.value,
        )

        logger.info(
            "protocol.approved",
            user_id=approver_id,
            entity_type="protocol",
            entity_id=protocol_id,
            message="Protocol approved",
        )

        return updated

    def list_pending(self) -> List[Protocol]:
        """List all protocols awaiting approval"""
        docs = self.collection_ref.where("status", "==", ProtocolStatus.SUBMITTED.value).stream()
        return [Protocol.from_dict(doc.to_dict()) for doc in docs]

    def list_visible(self) -> List[Protocol]:
        """List all approved protocols (visible to coaches, athletes)"""
        docs = self.collection_ref.where("status", "==", ProtocolStatus.APPROVED.value).stream()
        return [Protocol.from_dict(doc.to_dict()) for doc in docs]
