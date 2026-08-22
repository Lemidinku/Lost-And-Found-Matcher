"""Tests for the Reports API (FastAPI routes).

Uses an in-memory SQLite database via dependency override, so nothing here
touches backend/data/app.db. Fixtures mirror Task 4's own worked examples
(fixtures (a) and (c) from test_matching.py) but expressed as HTTP payloads.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    # Deliberately not used as a context manager: entering it would run the
    # app's lifespan (create_db_and_tables against the real DATABASE_URL),
    # touching backend/data/app.db even though no rows are ever written
    # there. Without `with`, requests still work but lifespan is skipped.
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _report_payload(**overrides):
    defaults = dict(
        report_type="lost",
        category="bag",
        title="Item",
        description="An item.",
        color="black",
        location="somewhere",
        occurred_at="2026-08-17T12:00:00",
        reporter_name="Reporter",
        reporter_contact="reporter@example.com",
    )
    defaults.update(overrides)
    return defaults


# --- Fixture (a): Strong/Possible match, from Task 4's test_matching.py -----

LOST_A = _report_payload(
    report_type="lost",
    category="bag",
    title="Black backpack",
    description="Black backpack containing a laptop charger",
    color="black",
    location="library",
    occurred_at="2026-08-17T14:00:00",
)

FOUND_A = _report_payload(
    report_type="found",
    category="bag",
    title="Dark backpack",
    description="Dark-colored backpack found near the library entrance",
    color="dark",
    location="library entrance",
    occurred_at="2026-08-17T18:00:00",
)

# --- Fixture (c): unrelated pair ---------------------------------------------

FOUND_C = _report_payload(
    report_type="found",
    category="electronics",
    title="earbud case",
    description="Found a dark wireless earbud case beside the coffee shop",
    color="white",
    location="coffee shop",
    occurred_at="2026-08-17T20:00:00",
)


# --- Basic CRUD behavior ------------------------------------------------------


def test_create_report_returns_201_with_defaults(client: TestClient):
    resp = client.post("/reports", json=LOST_A)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] is not None
    assert body["status"] == "open"
    assert body["created_at"] is not None
    assert body["title"] == "Black backpack"


def test_get_report_by_id(client: TestClient):
    created = client.post("/reports", json=LOST_A).json()
    resp = client.get(f"/reports/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_report_by_id_404(client: TestClient):
    resp = client.get("/reports/999999")
    assert resp.status_code == 404


def test_list_reports_with_filters(client: TestClient):
    client.post("/reports", json=LOST_A)
    client.post("/reports", json=FOUND_A)

    resp = client.get("/reports", params={"report_type": "lost"})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["report_type"] == "lost"

    resp = client.get("/reports", params={"status": "open"})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_patch_report_status(client: TestClient):
    created = client.post("/reports", json=LOST_A).json()
    resp = client.patch(f"/reports/{created['id']}", json={"status": "resolved"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "resolved"


def test_patch_report_404(client: TestClient):
    resp = client.patch("/reports/999999", json={"status": "resolved"})
    assert resp.status_code == 404


# --- Matches endpoint (brief Step 1 (a)(b)(c)) --------------------------------


def test_matches_returns_strong_or_possible_for_related_pair(client: TestClient):
    lost_id = client.post("/reports", json=LOST_A).json()["id"]
    found_id = client.post("/reports", json=FOUND_A).json()["id"]

    resp = client.get(f"/reports/{lost_id}/matches")
    assert resp.status_code == 200
    matches = resp.json()

    match = next((m for m in matches if m["report"]["id"] == found_id), None)
    assert match is not None
    assert match["tier"] in ("Strong", "Possible")
    assert match["reason"] != ""


def test_matches_omits_or_weak_for_unrelated_pair(client: TestClient):
    lost_id = client.post("/reports", json=LOST_A).json()["id"]
    found_id = client.post("/reports", json=FOUND_C).json()["id"]

    resp = client.get(f"/reports/{lost_id}/matches")
    matches = resp.json()

    match = next((m for m in matches if m["report"]["id"] == found_id), None)
    assert match is None or match["tier"] == "Weak"


def test_resolved_report_excluded_from_subsequent_matches(client: TestClient):
    lost_id = client.post("/reports", json=LOST_A).json()["id"]
    found_id = client.post("/reports", json=FOUND_A).json()["id"]

    patch_resp = client.patch(f"/reports/{found_id}", json={"status": "resolved"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "resolved"

    resp = client.get(f"/reports/{lost_id}/matches")
    matches = resp.json()

    match = next((m for m in matches if m["report"]["id"] == found_id), None)
    assert match is None


def test_matches_404_for_missing_report(client: TestClient):
    resp = client.get("/reports/999999/matches")
    assert resp.status_code == 404


def test_matches_sorted_descending_by_score(client: TestClient):
    lost_id = client.post("/reports", json=LOST_A).json()["id"]
    client.post("/reports", json=FOUND_A)
    client.post("/reports", json=FOUND_C)

    resp = client.get(f"/reports/{lost_id}/matches")
    scores = [m["score"] for m in resp.json()]
    assert scores == sorted(scores, reverse=True)
