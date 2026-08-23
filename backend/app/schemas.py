"""Pydantic request/response schemas for the Reports API.

These mirror `Report` (see models.py) field-for-field so the API contract
stays in lockstep with the DB model.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, field_validator

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

    @field_validator("occurred_at")
    @classmethod
    def normalize_occurred_at(cls, value: datetime) -> datetime:
        """SQLite has no timezone-aware column type, so SQLAlchemy silently
        drops any offset instead of converting it -- two submissions of the
        same real instant expressed with different offsets would otherwise
        be stored as different, incomparable naive values. Converting to
        naive UTC here, before the value ever reaches the database, makes
        storage and comparison correct regardless of what offset a client
        sends. Naive datetimes (e.g. from the frontend's `datetime-local`
        input, which carries no offset at all) pass through unchanged.
        """
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value


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
