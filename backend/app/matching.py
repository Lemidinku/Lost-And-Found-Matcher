"""Hybrid rule-based + embedding match scorer for lost/found report pairs.

Five components (weights sum to 100) are scored independently and combined
into a `ScoreBreakdown`, which is then mapped onto a coarse tier and rendered
into a human-readable reason string. Each component has its own small,
readable scoring function so the logic can be read top to bottom without
unrolling one large function.
"""

import difflib
from dataclasses import dataclass
from datetime import datetime

from app.embeddings import embed, cosine_similarity
from app.models import Category, Report


# Cosine-similarity floor for the text-similarity component.
#
# Calibrated from Task 3's three raw cosine values on the brief's own
# library-backpack / earbud-case strings:
#   - unrelated pair (backpack vs. earbud case): 0.6932907496101726
#   - related pair   (backpack lost vs. found):  0.8028587327960973
# FLOOR is set roughly halfway between them, so the unrelated pair rescales
# to ~0 and the related pair rescales to a clearly positive text score.
FLOOR = 0.748

# Colour synonym groups (lowercase). The literal words "dark"/"light" are
# included as members of their own group so e.g. "black" vs. "dark" hits the
# synonym-group match (8 points) rather than falling through to 0 — this is
# the spec's own worked example ("colour overlap (black/dark)").
COLOR_SYNONYM_GROUPS: dict[str, set[str]] = {
    "dark": {"black", "navy", "charcoal", "dark blue", "dark grey", "dark gray", "dark"},
    "light": {"white", "cream", "beige", "light grey", "light gray", "light"},
}


@dataclass
class ScoreBreakdown:
    """Per-component scores for one lost/found report pair."""

    category: int
    color: int
    location: int
    date: int
    text: int

    @property
    def total(self) -> int:
        return self.category + self.color + self.location + self.date + self.text


# --- Individual scoring components ------------------------------------------


def score_category(lost_category: Category, found_category: Category) -> int:
    """Exact category match is worth the full 20 points, else 0."""
    return 20 if lost_category == found_category else 0


def _normalize_color(color: str) -> str:
    """Lowercase/strip, and unify "gray"/"grey" spelling for comparison."""
    return color.strip().lower().replace("gray", "grey")


def score_color(lost_color: str, found_color: str) -> int:
    """Exact match → 15; substring of one another → 10; same synonym group → 8; else 0."""
    a = _normalize_color(lost_color)
    b = _normalize_color(found_color)

    # Guard against blank fields: "" is a substring of everything in Python,
    # so without this a missing color would falsely score as a 10-point
    # substring match against any other color.
    if not a or not b:
        return 0

    if a == b:
        return 15
    if a in b or b in a:
        return 10
    for group in COLOR_SYNONYM_GROUPS.values():
        # Synonym-group sets were written with "gray" spellings too; unify
        # them the same way as the inputs so membership checks line up.
        normalized_group = {_normalize_color(member) for member in group}
        if a in normalized_group and b in normalized_group:
            return 8
    return 0


def _location_ratio(lost_location: str, found_location: str) -> float:
    """difflib similarity ratio, boosted to at least 0.8 if one contains the other."""
    a = lost_location.strip().lower()
    b = found_location.strip().lower()

    # Guard against blank fields: "" is a substring of everything in Python,
    # so without this a missing location would falsely trigger the "contains"
    # boost to 0.8 against any other location.
    if not a or not b:
        return 0.0

    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    if a in b or b in a:
        ratio = max(ratio, 0.8)
    return ratio


def score_location(lost_location: str, found_location: str) -> int:
    """Fuzzy string similarity, scaled to the 20-point weight."""
    return round(_location_ratio(lost_location, found_location) * 20)


def _hours_between(a: datetime, b: datetime) -> float:
    return abs((a - b).total_seconds()) / 3600


def score_date(lost_occurred_at: datetime, found_occurred_at: datetime) -> int:
    """Closer occurrence times score higher, in four bands."""
    hours = _hours_between(lost_occurred_at, found_occurred_at)
    if hours <= 24:
        return 15
    if hours <= 72:
        return 10
    if hours <= 168:
        return 5
    return 0


def score_text(lost: Report, found: Report) -> int:
    """Embedding cosine similarity, rescaled against FLOOR and clamped to [0, 30]."""
    lost_embedding = embed(f"{lost.title} {lost.description}")
    found_embedding = embed(f"{found.title} {found.description}")
    cosine = cosine_similarity(lost_embedding, found_embedding)

    scaled = (cosine - FLOOR) / (1 - FLOOR)
    scaled = min(max(scaled, 0.0), 1.0)
    return round(scaled * 30)


# --- Combined scoring, tiering, and explanation -----------------------------


def score_pair(lost: Report, found: Report) -> ScoreBreakdown:
    """Score a lost/found report pair across all five components."""
    return ScoreBreakdown(
        category=score_category(lost.category, found.category),
        color=score_color(lost.color, found.color),
        location=score_location(lost.location, found.location),
        date=score_date(lost.occurred_at, found.occurred_at),
        text=score_text(lost, found),
    )


def tier_for_score(total: int) -> str:
    """Map a total score onto a coarse match-confidence tier."""
    if total >= 65:
        return "Strong"
    if total >= 35:
        return "Possible"
    if total >= 15:
        return "Weak"
    return "Hidden"


def build_reason(lost: Report, found: Report, breakdown: ScoreBreakdown) -> str:
    """Render a human-readable, comma-joined explanation of a match's score.

    Components that scored 0 are skipped. The result is capitalized and
    ends with a period, matching the spec's worked example:
    "Same category (bag), colour overlap (black/dark), same location
    (library), 4 hours apart, similar item description."
    """
    phrases: list[str] = []

    if breakdown.category > 0:
        phrases.append(f"same category ({lost.category.value})")

    if breakdown.color == 15:
        phrases.append(f"same colour ({lost.color})")
    elif breakdown.color > 0:
        phrases.append(f"colour overlap ({lost.color}/{found.color})")

    if breakdown.location > 0:
        ratio = _location_ratio(lost.location, found.location)
        if ratio >= 0.8:
            phrases.append(f"same location ({found.location})")
        else:
            phrases.append(f"similar location ({lost.location} / {found.location})")

    if breakdown.date > 0:
        hours = _hours_between(lost.occurred_at, found.occurred_at)
        if hours < 2:
            phrases.append("same day")
        elif hours < 24:
            phrases.append(f"{round(hours)} hours apart")
        else:
            phrases.append(f"{round(hours / 24)} days apart")

    # Skip below 10/30 to avoid noise from the embedding anisotropy floor.
    if breakdown.text >= 10:
        phrases.append("similar item description")

    if not phrases:
        return ""

    reason = ", ".join(phrases)
    return reason[0].upper() + reason[1:] + "."
