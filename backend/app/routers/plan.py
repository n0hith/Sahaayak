from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..db import get_session
from ..deps import get_current_session
from ..models.plan import Plan, PlanTask
from ..models.session import AnonymousSession
from ..schemas.plan import ExplainTaskRequest, PlanOut
from ..schemas.scheme import ExplanationResponse
from ..seed.document_labels import DOCUMENT_LABELS
from ..services.explanation_provider import get_explanation_provider
from ..services.mapper import plan_task_to_dict, profile_to_dict
from ..services.profile_repo import get_profile_or_404
from ..services.scheme_repo import load_scheme_dict

router = APIRouter(prefix="/api/plans", tags=["plans"])


def _plan_to_out(db: Session, plan: Plan) -> PlanOut:
    tasks = db.exec(select(PlanTask).where(PlanTask.plan_id == plan.id)).all()
    return PlanOut(
        id=plan.id,
        schemeId=plan.scheme_id,
        tasks=[plan_task_to_dict(task) for task in tasks],
        createdAt=plan.created_at,
        updatedAt=plan.updated_at,
    )


def _get_owned_plan_or_404(db: Session, anon: AnonymousSession, plan_id: str) -> Plan:
    plan = db.get(Plan, plan_id)
    if plan is None or plan.session_id != anon.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found.")
    return plan


@router.get("", response_model=list[PlanOut])
def list_plans(
    anon: AnonymousSession = Depends(get_current_session),
    db: Session = Depends(get_session),
) -> list[PlanOut]:
    """Every plan the session has ever started, not just one - this is the
    backend-side fix for the frontend's single-active-plan limitation."""
    plans = db.exec(select(Plan).where(Plan.session_id == anon.id)).all()
    return [_plan_to_out(db, plan) for plan in plans]


@router.post("/{scheme_id}", response_model=PlanOut)
def create_or_reset_plan(
    scheme_id: str,
    anon: AnonymousSession = Depends(get_current_session),
    db: Session = Depends(get_session),
) -> PlanOut:
    """Creates a plan for this scheme, or regenerates an existing one's
    tasks from the current profile - preserving any checkbox state a user
    already set, exactly like the frontend's planTasks(existing) behavior."""
    scheme = load_scheme_dict(db, scheme_id)
    if scheme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found.")
    profile = profile_to_dict(get_profile_or_404(db, anon))

    plan = db.exec(
        select(Plan).where(Plan.session_id == anon.id, Plan.scheme_id == scheme_id)
    ).first()
    existing_done: dict[str, bool] = {}
    if plan is None:
        plan = Plan(session_id=anon.id, scheme_id=scheme_id)
        db.add(plan)
        db.commit()
        db.refresh(plan)
    else:
        old_tasks = db.exec(select(PlanTask).where(PlanTask.plan_id == plan.id)).all()
        existing_done = {task.task_key: task.done for task in old_tasks}
        for task in old_tasks:
            db.delete(task)
        db.commit()

    provider = get_explanation_provider()
    tasks = provider.plan_tasks(scheme, profile, DOCUMENT_LABELS, existing_done)
    for task in tasks:
        db.add(
            PlanTask(
                plan_id=plan.id,
                task_key=task["id"],
                title=task["title"],
                description=task["description"],
                status=task["status"],
                done=task["done"],
            )
        )
    plan.updated_at = datetime.utcnow()
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return _plan_to_out(db, plan)


@router.patch("/{plan_id}/tasks/{task_id}", response_model=PlanOut)
def toggle_task(
    plan_id: str,
    task_id: str,
    anon: AnonymousSession = Depends(get_current_session),
    db: Session = Depends(get_session),
) -> PlanOut:
    plan = _get_owned_plan_or_404(db, anon, plan_id)
    task = db.exec(
        select(PlanTask).where(PlanTask.plan_id == plan.id, PlanTask.task_key == task_id)
    ).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    task.done = not task.done
    db.add(task)
    plan.updated_at = datetime.utcnow()
    db.add(plan)
    db.commit()
    return _plan_to_out(db, plan)


@router.post("/{plan_id}/explain", response_model=ExplanationResponse)
def explain_plan_task(
    plan_id: str,
    payload: ExplainTaskRequest,
    anon: AnonymousSession = Depends(get_current_session),
    db: Session = Depends(get_session),
) -> ExplanationResponse:
    plan = _get_owned_plan_or_404(db, anon, plan_id)
    task = db.exec(
        select(PlanTask).where(PlanTask.plan_id == plan.id, PlanTask.task_key == payload.taskId)
    ).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    provider = get_explanation_provider()
    explanation = provider.explain_task(plan_task_to_dict(task), payload.question)
    return ExplanationResponse(explanation=explanation)
