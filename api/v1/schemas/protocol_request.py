"""
Schemas for protocol request endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ApprovalDecisionSchema(BaseModel):
    """Approval decision detail"""
    decided_by: str
    decision: str
    reason: Optional[str] = None
    decided_at: str


class ProtocolRequestResponse(BaseModel):
    """Protocol request response"""
    request_id: str
    protocol_id: str
    requested_by: str
    status: str
    created_at: str
    decision: Optional[ApprovalDecisionSchema] = None

    class Config:
        schema_extra = {
            "example": {
                "request_id": "req_abc123",
                "protocol_id": "proto_xyz",
                "requested_by": "user_123",
                "status": "pending",
                "created_at": "2026-06-26T12:00:00Z",
                "decision": None,
            }
        }


class ProtocolRequestListResponse(BaseModel):
    """List of protocol requests"""
    requests: List[ProtocolRequestResponse]
    count: int


class ApproveRequest(BaseModel):
    """Request to approve a protocol"""
    reason: Optional[str] = Field(None, description="Optional approval reason")


class RejectRequest(BaseModel):
    """Request to reject a protocol"""
    reason: str = Field(description="Reason for rejection")
