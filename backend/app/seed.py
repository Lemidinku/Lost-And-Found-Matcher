"""Seed script to populate the database with demo data."""

from datetime import datetime, timedelta
from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models import Report, ReportType, Category, Status


def seed_database() -> None:
    """Create tables and seed with demo data if empty."""
    # Create tables if they don't exist
    create_db_and_tables()

    # Check if database is already populated
    with Session(engine) as session:
        existing_report = session.exec(select(Report)).first()
        if existing_report is not None:
            print("Database already populated, skipping seed.")
            return

        # Base timestamp for consistent seeding
        base_time = datetime(2024, 10, 15, 10, 0, 0)

        # Demo reports: library-backpack lost/found pair (verbatim from assessment brief)
        reports = [
            Report(
                report_type=ReportType.LOST,
                category=Category.BAG,
                title="Black backpack",
                description="Black backpack containing a laptop charger. Lost around the library on Monday afternoon.",
                color="black",
                location="library",
                occurred_at=base_time,
                reporter_name="Alice Johnson",
                reporter_contact="alice@example.com",
                status=Status.OPEN,
            ),
            Report(
                report_type=ReportType.FOUND,
                category=Category.BAG,
                title="Dark-colored backpack",
                description="Dark-colored backpack found near the library entrance Monday evening.",
                color="dark",
                location="library entrance",
                occurred_at=base_time + timedelta(hours=4),
                reporter_name="Bob Smith",
                reporter_contact="bob@example.com",
                status=Status.OPEN,
            ),
            # AirPods-case/earbud-case lost/found pair (verbatim from assessment brief)
            Report(
                report_type=ReportType.LOST,
                category=Category.ELECTRONICS,
                title="AirPods case",
                description="I lost my black AirPods case yesterday near the cafeteria.",
                color="black",
                location="cafeteria",
                occurred_at=base_time + timedelta(days=1),
                reporter_name="Charlie Brown",
                reporter_contact="charlie@example.com",
                status=Status.OPEN,
            ),
            Report(
                report_type=ReportType.FOUND,
                category=Category.ELECTRONICS,
                title="Earbud case",
                description="Found a dark wireless earbud case beside the coffee shop.",
                color="dark",
                location="coffee shop",
                occurred_at=base_time + timedelta(days=1, hours=6),
                reporter_name="Diana Chen",
                reporter_contact="diana@example.com",
                status=Status.OPEN,
            ),
            # Filler reports with different timestamps
            Report(
                report_type=ReportType.LOST,
                category=Category.DOCUMENTS,
                title="Student ID card",
                description="Lost student ID card, blue with name on it",
                color="blue",
                location="cafeteria",
                occurred_at=base_time - timedelta(days=2),
                reporter_name="Edward Davis",
                reporter_contact="edward@example.com",
                status=Status.OPEN,
            ),
            Report(
                report_type=ReportType.FOUND,
                category=Category.ACCESSORY,
                title="Water bottle",
                description="Found a blue water bottle at the gym",
                color="blue",
                location="gym",
                occurred_at=base_time + timedelta(days=2),
                reporter_name="Fiona Garcia",
                reporter_contact="fiona@example.com",
                status=Status.OPEN,
            ),
            Report(
                report_type=ReportType.LOST,
                category=Category.ACCESSORY,
                title="Umbrella",
                description="Lost black umbrella, was left at main building",
                color="black",
                location="main building",
                occurred_at=base_time + timedelta(hours=2),
                reporter_name="George Wilson",
                reporter_contact="george@example.com",
                status=Status.OPEN,
            ),
            Report(
                report_type=ReportType.FOUND,
                category=Category.CLOTHING,
                title="Blue jacket",
                description="Found blue jacket in the library study room",
                color="blue",
                location="library",
                occurred_at=base_time + timedelta(days=3),
                reporter_name="Helen Martinez",
                reporter_contact="helen@example.com",
                status=Status.OPEN,
            ),
        ]

        # Add all reports to session and commit
        for report in reports:
            session.add(report)

        session.commit()
        print(f"Successfully seeded database with {len(reports)} reports.")


if __name__ == "__main__":
    seed_database()
