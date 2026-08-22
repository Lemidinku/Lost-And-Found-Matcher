"""Tests for the matching/scoring module.

Fixtures are built directly from the assessment brief's own worked examples
(no DB needed — Report is just an in-memory SQLModel object here).
"""

from datetime import datetime

from app.models import Report, ReportType, Category, Status
from app.matching import score_pair, tier_for_score, build_reason


def _report(**overrides) -> Report:
    """Build a Report with sensible defaults, overridden per fixture."""
    defaults = dict(
        report_type=ReportType.LOST,
        category=Category.BAG,
        title="Item",
        description="An item.",
        color="black",
        location="somewhere",
        occurred_at=datetime(2026, 8, 17, 12, 0),
        reporter_name="Reporter",
        reporter_contact="reporter@example.com",
        status=Status.OPEN,
    )
    defaults.update(overrides)
    return Report(**defaults)


# --- Fixture (a): Strong/Possible match -------------------------------------
# lost/found library-backpack pair, straight from the assessment brief.

LOST_A = _report(
    report_type=ReportType.LOST,
    category=Category.BAG,
    title="Black backpack",
    description="Black backpack containing a laptop charger",
    color="black",
    location="library",
    occurred_at=datetime(2026, 8, 17, 14, 0),  # Monday 14:00
)

FOUND_A = _report(
    report_type=ReportType.FOUND,
    category=Category.BAG,
    title="Dark backpack",
    description="Dark-colored backpack found near the library entrance",
    color="dark",
    location="library entrance",
    occurred_at=datetime(2026, 8, 17, 18, 0),  # Monday 18:00, 4 hours later
)


# --- Fixture (b): Weaker match ------------------------------------------------
# Same lost report as (a); found report is a plausible-but-weaker match:
# same category and color, but different location and much later date.

LOST_B = LOST_A

FOUND_B = _report(
    report_type=ReportType.FOUND,
    category=Category.BAG,
    title="Black backpack",
    description="Black backpack found at the football field two weeks later",
    color="black",
    location="football field",
    occurred_at=datetime(2026, 8, 31, 14, 0),  # two weeks after LOST_A
)


# --- Fixture (c): Unrelated pair ---------------------------------------------
# lost = the backpack from (a); found = an unrelated earbud case report,
# using the exact wording from the brief's own calibration string.

LOST_C = LOST_A

FOUND_C = _report(
    report_type=ReportType.FOUND,
    category=Category.ELECTRONICS,
    title="earbud case",
    description="Found a dark wireless earbud case beside the coffee shop",
    color="white",
    location="coffee shop",
    occurred_at=datetime(2026, 8, 17, 20, 0),  # same day as LOST_A
)


def test_strong_or_possible_match():
    breakdown = score_pair(LOST_A, FOUND_A)
    tier = tier_for_score(breakdown.total)
    reason = build_reason(LOST_A, FOUND_A, breakdown)

    print(f"\nFixture (a) breakdown: {breakdown}, total={breakdown.total}, tier={tier}")
    print(f"Fixture (a) reason: {reason}")

    assert tier in ("Strong", "Possible")
    assert "category" in reason
    assert "colour" in reason
    assert "location" in reason


def test_weaker_match_scores_lower_and_is_not_strong():
    breakdown_a = score_pair(LOST_A, FOUND_A)
    breakdown_b = score_pair(LOST_B, FOUND_B)
    tier_b = tier_for_score(breakdown_b.total)

    print(f"\nFixture (b) breakdown: {breakdown_b}, total={breakdown_b.total}, tier={tier_b}")

    assert breakdown_b.total < breakdown_a.total
    assert tier_b != "Strong"


def test_unrelated_pair_is_weak_or_hidden():
    breakdown = score_pair(LOST_C, FOUND_C)
    tier = tier_for_score(breakdown.total)

    print(f"\nFixture (c) breakdown: {breakdown}, total={breakdown.total}, tier={tier}")

    assert tier in ("Weak", "Hidden")


def test_reason_string_format():
    """Reason string should be a comma-joined, capitalized sentence ending in a period."""
    breakdown = score_pair(LOST_A, FOUND_A)
    reason = build_reason(LOST_A, FOUND_A, breakdown)

    assert reason[0] == reason[0].upper()
    assert reason.endswith(".")
    assert ", " in reason
