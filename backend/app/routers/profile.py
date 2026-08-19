from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..deps import get_current_session
from ..models.profile import Profile
from ..models.session import AnonymousSession
from ..schemas.profile import ProfileIn, ProfileOut
from ..services.eligibility import DEMO_PROFILE
from ..services.mapper import apply_profile_dict, profile_to_dict
from ..services.profile_repo import get_profile_or_404

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _to_out(profile: Profile) -> ProfileOut:
    return ProfileOut(id=profile.id, createdAt=profile.created_at, updatedAt=profile.updated_at, **profile_to_dict(profile))


@router.get("", response_model=ProfileOut)
def read_profile(
    anon: AnonymousSession = Depends(get_current_session),
    db: Session = Depends(get_session),
) -> ProfileOut:
    return _to_out(get_profile_or_404(db, anon))


@router.put("", response_model=ProfileOut)
def replace_profile(
    payload: ProfileIn,
    anon: AnonymousSession = Depends(get_current_session),
    db: Session = Depends(get_session),
) -> ProfileOut:
    profile = db.exec(select(Profile).where(Profile.session_id == anon.id)).first()
    if profile is None:
        profile = Profile(session_id=anon.id)
        db.add(profile)

    apply_profile_dict(profile, payload.model_dump())
    profile.updated_at = datetime.utcnow()
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _to_out(profile)


@router.post("/demo", response_model=ProfileOut)
def load_demo_profile(
    anon: AnonymousSession = Depends(get_current_session),
    db: Session = Depends(get_session),
) -> ProfileOut:
    """Mirrors the frontend's "Use demo profile" shortcut in the
    questionnaire (src/components/Questionnaire.tsx)."""
    profile = db.exec(select(Profile).where(Profile.session_id == anon.id)).first()
    if profile is None:
        profile = Profile(session_id=anon.id)
        db.add(profile)

    apply_profile_dict(profile, DEMO_PROFILE)
    profile.updated_at = datetime.utcnow()
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _to_out(profile)
