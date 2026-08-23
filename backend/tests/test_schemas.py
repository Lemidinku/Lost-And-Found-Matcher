"""Tests for Pydantic schema validation (backend/app/schemas.py)."""

from datetime import datetime, timedelta, timezone

from app.schemas import ReportCreate


def _payload(**overrides):
    defaults = dict(
        report_type="lost",
        category="bag",
        title="Black backpack",
        description="Black backpack containing a laptop charger.",
        color="black",
        location="library",
        occurred_at=datetime(2026, 8, 17, 14, 0, 0),
        reporter_name="Reporter",
        reporter_contact="reporter@example.com",
    )
    defaults.update(overrides)
    return defaults


def test_naive_occurred_at_passes_through_unchanged():
    """The frontend's datetime-local input has no offset at all -- naive
    datetimes must be left exactly as submitted."""
    naive = datetime(2026, 8, 17, 14, 0, 0)
    report = ReportCreate(**_payload(occurred_at=naive))
    assert report.occurred_at == naive
    assert report.occurred_at.tzinfo is None


def test_offset_aware_occurred_at_is_normalized_to_naive_utc():
    """SQLite has no timezone-aware column type -- SQLAlchemy silently
    drops any offset instead of converting it, so two submissions of the
    same real instant expressed with different offsets would otherwise be
    stored as different, incomparable naive values. Normalizing to naive
    UTC before storage fixes that."""
    aware = datetime(2026, 8, 17, 19, 0, 0, tzinfo=timezone(timedelta(hours=5)))
    report = ReportCreate(**_payload(occurred_at=aware))
    assert report.occurred_at == datetime(2026, 8, 17, 14, 0, 0)
    assert report.occurred_at.tzinfo is None


def test_same_instant_different_offsets_normalize_identically():
    """The actual bug: two ways of writing the same real-world instant must
    end up as the exact same stored value, not off by the offset gap."""
    utc = datetime(2026, 8, 17, 14, 0, 0, tzinfo=timezone.utc)
    plus_five = datetime(2026, 8, 17, 19, 0, 0, tzinfo=timezone(timedelta(hours=5)))

    report_utc = ReportCreate(**_payload(occurred_at=utc))
    report_plus_five = ReportCreate(**_payload(occurred_at=plus_five))

    assert report_utc.occurred_at == report_plus_five.occurred_at
