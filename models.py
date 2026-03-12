"""Data models used by the SDS2 AI Copilot API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Literal

from pydantic import BaseModel, Field


class Point3D(BaseModel):
    x: float
    y: float
    z: float


class Member(BaseModel):
    member_id: str = Field(..., description="Unique member identifier")
    type: str = Field(..., description="Member type (beam, column, brace, etc.)")
    material: str = Field(..., description="Material grade/spec")
    length_mm: float = Field(..., gt=0)
    weight_kg: float = Field(..., gt=0)
    start: Point3D
    end: Point3D


class ModelData(BaseModel):
    project_id: str
    revision: str
    members: List[Member]


class EstimateResult(BaseModel):
    project_id: str
    revision: str
    total_weight_kg: float
    estimated_cost_usd: float
    assumptions: List[str]


class ClashPair(BaseModel):
    member_a: str
    member_b: str
    severity: Literal["low", "medium", "high"]


class ClashReport(BaseModel):
    project_id: str
    revision: str
    clashes: List[ClashPair]


class SuggestedChange(BaseModel):
    change_id: str
    member_id: str
    action: Literal["shift_member", "resize_plate", "flag_review"]
    reason: str
    payload: dict


class ChangeProposal(BaseModel):
    project_id: str
    revision: str
    suggested_changes: List[SuggestedChange]


class ApplyRequest(BaseModel):
    model: ModelData
    selected_change_ids: List[str]
    approval_token: str = Field(..., description="Must be 'APPROVED' for write actions")


class ApplyResult(BaseModel):
    event_id: str
    project_id: str
    revision: str
    applied_change_ids: List[str]
    message: str


class RollbackRequest(BaseModel):
    event_id: str


class AuditEvent(BaseModel):
    event_id: str
    timestamp_utc: datetime
    action: Literal["apply", "rollback"]
    project_id: str
    revision: str
    before_snapshot: ModelData
    after_snapshot: ModelData
    metadata: dict


class ErrorResponse(BaseModel):
    detail: str


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
