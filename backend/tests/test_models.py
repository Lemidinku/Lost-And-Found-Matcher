"""Tests for data models and database operations."""

from datetime import datetime
from sqlalchemy import create_engine
from sqlmodel import Session

from app.models import Report, ReportType, Category, Status
from app.database import create_db_and_tables


def test_report_round_trip():
    """Test that Report model can be inserted and read back with all fields intact."""
    # Create in-memory SQLite engine
    engine = create_engine("sqlite://", echo=False)

    # Create tables
    create_db_and_tables(engine)

    # Create test data
    test_time = datetime(2026, 8, 22, 10, 30, 45)

    new_report = Report(
        report_type=ReportType.LOST,
        category=Category.BAG,
        title="Black backpack",
        description="Lost at the airport terminal, has a laptop inside",
        color="black",
        location="Airport Terminal 2",
        occurred_at=test_time,
        reporter_name="John Doe",
        reporter_contact="john@example.com",
        status=Status.OPEN,
        created_at=test_time,
    )

    # Insert report
    with Session(engine) as session:
        session.add(new_report)
        session.commit()
        session.refresh(new_report)
        inserted_id = new_report.id

    # Read back and assert
    with Session(engine) as session:
        retrieved_report = session.get(Report, inserted_id)

        assert retrieved_report is not None, "Report should exist after insertion"
        assert retrieved_report.id == inserted_id
        assert retrieved_report.report_type == ReportType.LOST
        assert retrieved_report.category == Category.BAG
        assert retrieved_report.title == "Black backpack"
        assert retrieved_report.description == "Lost at the airport terminal, has a laptop inside"
        assert retrieved_report.color == "black"
        assert retrieved_report.location == "Airport Terminal 2"
        assert retrieved_report.occurred_at == test_time
        assert retrieved_report.reporter_name == "John Doe"
        assert retrieved_report.reporter_contact == "john@example.com"
        assert retrieved_report.status == Status.OPEN
        assert retrieved_report.created_at == test_time
