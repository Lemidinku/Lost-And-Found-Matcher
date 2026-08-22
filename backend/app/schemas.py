"""Pydantic request/response schemas for the Reports API.

These mirror `Report` (see models.py) field-for-field so the API contract
stays in lockstep with the DB model.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import Category, ReportType, Status


class ReportCreate(BaseModel):
    """Body for POST /reports. All Report fields except server-generated ones
    (id, status, created_at)."""

    report_type: ReportType
    category: Category
    title: str
    description: str
    color: str
    location: str
    occurred_at: datetime
    reporter_name: str
    reporter_contact: str


class ReportRead(BaseModel):
    """Response shape for a Report: every field, including server-generated ones."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    report_type: ReportType
    category: Category
    title: str
    description: str
    color: str
    location: str
    occurred_at: datetime
    reporter_name: str
    reporter_contact: str
    status: Status
    created_at: datetime


class ReportStatusUpdate(BaseModel):
    """Body for PATCH /reports/{id}."""

    status: Status


class MatchResult(BaseModel):
    """One scored candidate returned by GET /reports/{id}/matches."""

    model_config = ConfigDict(from_attributes=True)

    report: ReportRead
    score: int
    tier: str
    reason: str
