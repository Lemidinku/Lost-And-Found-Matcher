"""Tests for the matching/scoring module.

Fixtures are built directly from the assessment brief's own worked examples
(no DB needed — Report is just an in-memory SQLModel object here).
"""

from datetime import datetime

from app.models import Report, ReportType, Category, Status
from app.matching import (
    score_pair,
    tier_for_score,
    build_reason,
    score_color,
    score_location,
    score_text,
)


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


# --- Fixture (d): Task 3's own related-pair calibration strings --------------
# Exact LOST_BACKPACK / FOUND_BACKPACK sentences from
# backend/tests/test_embeddings.py, known to score cosine ~0.8029 — comfortably
# above FLOOR (0.748). Used to exercise score_text()'s positive-score path and
# build_reason()'s "similar item description" branch, which no other fixture
# in this file reaches (their shorter, more repetitive text stays under FLOOR).

LOST_D = _report(
    report_type=ReportType.LOST,
    category=Category.BAG,
    title="Lost item: backpack",
    description=(
        "Black backpack containing a laptop charger. "
        "Lost around the library on Monday afternoon."
    ),
    color="black",
    location="library",
    occurred_at=datetime(2026, 8, 17, 14, 0),
)

FOUND_D = _report(
    report_type=ReportType.FOUND,
    category=Category.BAG,
    title="Found item: backpack",
    description="Dark-colored backpack found near the library entrance Monday evening.",
    color="dark",
    location="library entrance",
    occurred_at=datetime(2026, 8, 17, 18, 0),
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


def test_blank_color_does_not_score_as_a_match():
    """"" is a substring of every string in Python — must not be treated as a match."""
    assert score_color("", "black") == 0
    assert score_color("black", "") == 0
    assert score_color("", "") == 0


def test_blank_location_does_not_score_as_a_match():
    """"" is a substring of every string in Python — must not be treated as a match."""
    assert score_location("", "library") == 0
    assert score_location("library", "") == 0
    assert score_location("", "") == 0


def test_unrelated_short_locations_do_not_score_as_similar():
    """"cafeteria" and "library" share individual letters ('a', 'r') but no words —
    character-level similarity (the old difflib approach) scored this 5/20 and
    produced a misleading "similar location" reason. Word-level overlap must
    correctly treat these as unrelated."""
    assert score_location("cafeteria", "library") == 0
    assert score_location("library", "cafeteria") == 0


def test_location_that_is_a_word_subset_of_another_scores_as_a_near_full_match():
    """"library" is entirely contained in "library entrance"'s words — this should
    score as a strong match, same as the substring-boost the old implementation
    special-cased, but now falling out of plain word-overlap."""
    assert score_location("library", "library entrance") == 20
    assert score_location("library entrance", "library") == 20


def test_location_exact_match_scores_full():
    assert score_location("library", "library") == 20


def test_location_partial_word_overlap_scores_partial_credit():
    """Sharing one of two words each should score roughly half, not zero and not full."""
    assert score_location("main building", "building lobby") == 10


def test_text_similarity_scores_positive_for_a_genuinely_related_pair():
    """Task 3's related-pair calibration strings (cosine ~0.8029) should clear FLOOR
    and produce a clearly positive text score — the 30-point component's main path,
    not exercised by fixtures (a)-(c), whose shorter/more repetitive text stays
    under FLOOR."""
    text_score = score_text(LOST_D, FOUND_D)
    print(f"\nFixture (d) text score: {text_score}")
    assert text_score >= 10


def test_build_reason_includes_similar_item_description_when_text_score_is_high():
    breakdown = score_pair(LOST_D, FOUND_D)
    reason = build_reason(LOST_D, FOUND_D, breakdown)

    print(f"Fixture (d) breakdown: {breakdown}, total={breakdown.total}")
    print(f"Fixture (d) reason: {reason}")

    assert breakdown.text >= 10
    assert "similar item description" in reason


def test_blank_title_and_description_does_not_score_as_a_perfect_text_match():
    """Two reports with blank/whitespace-only title+description embed nearly
    identically (cosine ~1.0 for two copies of the same near-empty input),
    which would otherwise rescale to the *maximum* text score (30/30) --
    a false-perfect match on the highest-weighted component, worse than the
    false-partial-match bugs already found in colour and location matching.
    Neither field is validated non-empty by the API schema, so this is
    directly reachable by any client, not just a defensive edge case."""
    lost = _report(title="", description="")
    found = _report(title="   ", description="   ")
    assert score_text(lost, found) == 0


def test_blank_text_on_only_one_side_still_scores_normally():
    """A report with a title but no description (or vice versa) is real,
    valid content -- only a BOTH-blank pair should be guarded against."""
    lost = _report(title="Black backpack", description="")
    found = _report(title="Black backpack", description="")
    # Same non-blank title on both sides should still produce a real,
    # non-zero embedding comparison, not get caught by the blank guard.
    assert score_text(lost, found) > 0
