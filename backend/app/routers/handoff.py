from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..db import get_session
from ..deps import get_current_session
from ..models.plan import Plan, PlanTask
from ..models.reference import ReferenceRequest
from ..models.session import AnonymousSession
from ..schemas.reference import HandoffRequest, ReferenceOut
from ..services.reference_generator import generate_reference_code

router = APIRouter(tags=["handoff"])

MAX_REFERENCE_ATTEMPTS = 5


def _reference_to_out(db: Session, ref: ReferenceRequest) -> ReferenceOut:
    tasks = db.exec(select(PlanTask).where(PlanTask.plan_id == ref.plan_id)).all()
    completed = sum(1 for task in tasks if task.done)
    total = len(tasks)
    return ReferenceOut(
        referenceCode=ref.reference_code,
        route=ref.route,
        schemeId=ref.scheme_id,
        planId=ref.plan_id,
        completedTasks=completed,
        totalTasks=total,
        status="Preparation complete" if total > 0 and completed == total else "Documents still needed",
        createdAt=ref.created_at,
    )


@router.post("/api/handoff", response_model=ReferenceOut)
def create_handoff(
    payload: HandoffRequest,
    anon: AnonymousSession = Depends(get_current_session),
    db: Session = Depends(get_session),
) -> ReferenceOut:
    """The mock hand-off step. This never submits anything anywhere - it
    only records a synthetic readiness reference on this session, mirroring
    src/components/Handoff.tsx's "Create my readiness reference" action but
    with a deterministic, collision-checked code (services/reference_generator.py)
    instead of Math.random()."""
    plan = db.get(Plan, payload.planId)
    if plan is None or plan.session_id != anon.id or plan.scheme_id != payload.schemeId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found for this scheme/session.")

    now = datetime.utcnow()
    code = None
    for attempt in range(MAX_REFERENCE_ATTEMPTS):
        candidate = generate_reference_code(anon.id, payload.schemeId, now, attempt)
        collision = db.exec(
            select(ReferenceRequest).where(ReferenceRequest.reference_code == candidate)
        ).first()
        if collision is None:
            code = candidate
            break
    if code is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate a unique reference code. Please try again.",
        )

    ref = ReferenceRequest(
        session_id=anon.id,
        scheme_id=payload.schemeId,
        plan_id=payload.planId,
        route=payload.route,
        reference_code=code,
        created_at=now,
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return _reference_to_out(db, ref)


@router.get("/api/references/{reference_code}", response_model=ReferenceOut)
def get_reference(
    reference_code: str,
    anon: AnonymousSession = Depends(get_current_session),
    db: Session = Depends(get_session),
) -> ReferenceOut:
    ref = db.exec(
        select(ReferenceRequest).where(
            ReferenceRequest.reference_code == reference_code,
            ReferenceRequest.session_id == anon.id,
        )
    ).first()
    if ref is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reference not found.")
    return _reference_to_out(db, ref)
