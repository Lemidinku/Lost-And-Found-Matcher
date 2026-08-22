"""Data models for the Lost & Found Matcher application."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field


class ReportType(str, Enum):
    """Type of report: lost or found item."""

    LOST = "lost"
    FOUND = "found"


class Category(str, Enum):
    """Category of lost/found item."""

    ELECTRONICS = "electronics"
    BAG = "bag"
    CLOTHING = "clothing"
    ACCESSORY = "accessory"
    DOCUMENTS = "documents"
    KEYS = "keys"
    OTHER = "other"


class Status(str, Enum):
    """Status of a report."""

    OPEN = "open"
    RESOLVED = "resolved"


class Report(SQLModel, table=True):
    """A lost or found item report."""

    id: Optional[int] = Field(default=None, primary_key=True)
    report_type: ReportType
    category: Category
    title: str
    description: str
    color: str
    location: str
    occurred_at: datetime
    reporter_name: str
    reporter_contact: str
    status: Status = Status.OPEN
    created_at: datetime = Field(default_factory=datetime.utcnow)
