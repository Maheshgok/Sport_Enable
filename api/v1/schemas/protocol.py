"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class ProtocolConfigSchema(BaseModel):
    """Protocol analysis configuration schema"""
    joints_to_track: List[str] = Field(description="List of joints to track (e.g., 'left_knee')")
    angles_to_measure: List[str] = Field(description="List of angles to measure")
    metrics_to_calculate: List[str] = Field(description="List of metrics to compute")
    baseline_metrics: Dict[str, Any] = Field(description="Baseline values for comparison")
    risk_factors: Dict[str, Any] = Field(description="Risk thresholds and factors")
    report_template: Dict[str, Any] = Field(description="Report structure and sections")
    required_views: List[str] = Field(default=["front"], description="Required video views")
    expected_duration_seconds: int = Field(default=30, description="Expected video duration")

    class Config:
        schema_extra = {
            "example": {
                "joints_to_track": ["left_knee", "right_knee", "left_hip", "right_hip"],
                "angles_to_measure": ["knee_flexion", "hip_abduction"],
                "metrics_to_calculate": ["range_of_motion", "symmetry"],
                "baseline_metrics": {
                    "knee_flexion": {"min": 0, "max": 120},
                    "hip_abduction": {"min": 30, "max": 45},
                },
                "risk_factors": {"asymmetry_threshold": 15},
                "report_template": {
                    "sections": ["summary", "metrics", "recommendations"],
                },
                "required_views": ["front", "side"],
                "expected_duration_seconds": 60,
            }
        }


class ProtocolCreateRequest(BaseModel):
    """Request to create a new protocol"""
    protocol_name: str = Field(description="Name of the protocol")
    description: str = Field(description="Protocol description")
    sport_id: str = Field(description="Sport ID (e.g., 'football', 'basketball')")
    config: ProtocolConfigSchema = Field(description="Analysis configuration")


class ProtocolUpdateRequest(BaseModel):
    """Request to update a protocol"""
    protocol_name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[ProtocolConfigSchema] = None


class ProtocolResponse(BaseModel):
    """Protocol response"""
    protocol_id: str
    protocol_name: str
    description: str
    sport_id: str
    created_by: str
    status: str
    config: ProtocolConfigSchema
    created_at: str
    updated_at: str
    version: int

    class Config:
        schema_extra = {
            "example": {
                "protocol_id": "proto_abc123",
                "protocol_name": "Football ACL Baseline",
                "description": "Baseline movement assessment for ACL injury risk",
                "sport_id": "football",
                "created_by": "user_123",
                "status": "draft",
                "config": {
                    "joints_to_track": ["left_knee", "right_knee"],
                    "angles_to_measure": ["knee_flexion"],
                    "metrics_to_calculate": ["range_of_motion"],
                    "baseline_metrics": {"knee_flexion": {"min": 0, "max": 120}},
                    "risk_factors": {},
                    "report_template": {"sections": ["summary"]},
                    "required_views": ["front"],
                    "expected_duration_seconds": 30,
                },
                "created_at": "2026-06-26T12:00:00Z",
                "updated_at": "2026-06-26T12:00:00Z",
                "version": 1,
            }
        }


class ProtocolListResponse(BaseModel):
    """List of protocols"""
    protocols: List[ProtocolResponse]
    count: int


class ProtocolSubmitRequest(BaseModel):
    """Request to submit a protocol for approval"""
    pass


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    correlation_id: Optional[str] = None
