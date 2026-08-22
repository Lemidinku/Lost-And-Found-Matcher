"""Report CRUD routes plus the /matches endpoint.

Scoring logic itself lives in matching.py — this module only fetches
candidates, calls into it, and shapes the HTTP responses.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.matching import build_reason, score_pair, tier_for_score
from app.models import Report, ReportType, Status
from app.schemas import MatchResult, ReportCreate, ReportRead, ReportStatusUpdate

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportRead, status_code=201)
def create_report(payload: ReportCreate, session: Session = Depends(get_session)) -> Report:
    report = Report(**payload.model_dump())
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


@router.get("", response_model=list[ReportRead])
def list_reports(
    report_type: Optional[ReportType] = None,
    status: Optional[Status] = None,
    session: Session = Depends(get_session),
) -> list[Report]:
    query = select(Report)
    if report_type is not None:
        query = query.where(Report.report_type == report_type)
    if status is not None:
        query = query.where(Report.status == status)
    return list(session.exec(query).all())


@router.get("/{report_id}", response_model=ReportRead)
def get_report(report_id: int, session: Session = Depends(get_session)) -> Report:
    report = session.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.patch("/{report_id}", response_model=ReportRead)
def update_report_status(
    report_id: int,
    payload: ReportStatusUpdate,
    session: Session = Depends(get_session),
) -> Report:
    report = session.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    report.status = payload.status
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


@router.get("/{report_id}/matches", response_model=list[MatchResult])
def get_matches(report_id: int, session: Session = Depends(get_session)) -> list[MatchResult]:
    report = session.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    opposite_type = ReportType.FOUND if report.report_type == ReportType.LOST else ReportType.LOST
    query = select(Report).where(
        Report.report_type == opposite_type,
        Report.status == Status.OPEN,
        Report.id != report_id,
    )
    candidates = session.exec(query).all()

    results: list[MatchResult] = []
    for candidate in candidates:
        if report.report_type == ReportType.LOST:
            lost, found = report, candidate
        else:
            lost, found = candidate, report

        breakdown = score_pair(lost, found)
        tier = tier_for_score(breakdown.total)

        # A pair that scores on fewer than two of the five components (e.g.
        # nothing but date proximity) carries essentially zero relevance,
        # even if the total happens to clear the Hidden threshold — drop it
        # too, per the design's own "only essentially-zero-relevance pairs
        # are dropped" intent.
        contributing = sum(
            1
            for value in (breakdown.category, breakdown.color, breakdown.location, breakdown.date, breakdown.text)
            if value > 0
        )
        if tier == "Hidden" or contributing < 2:
            continue

        reason = build_reason(lost, found, breakdown)
        results.append(
            MatchResult(report=ReportRead.model_validate(candidate), score=breakdown.total, tier=tier, reason=reason)
        )

    results.sort(key=lambda m: m.score, reverse=True)
    return results
