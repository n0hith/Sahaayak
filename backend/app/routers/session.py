from datetime import datetime

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlmodel import Session

from ..db import get_session
from ..deps import SESSION_COOKIE_MAX_AGE, SESSION_COOKIE_NAME, get_serializer
from ..models.profile import Profile
from ..models.session import AnonymousSession
from ..services.eligibility import initial_profile
from ..services.mapper import apply_profile_dict

router = APIRouter(prefix="/api/session", tags=["session"])


class SessionOut(BaseModel):
    sessionId: str
    createdAt: datetime


@router.post("", response_model=SessionOut)
def create_session(response: Response, db: Session = Depends(get_session)) -> SessionOut:
    """Creates a new anonymous session and a blank profile for it, and
    sets a signed httpOnly cookie carrying nothing but the session's
    opaque UUID. There is no username/password/OTP anywhere in this flow -
    see README "Anonymous session model"."""
    anon = AnonymousSession()
    db.add(anon)
    db.commit()
    db.refresh(anon)

    profile = Profile(session_id=anon.id)
    apply_profile_dict(profile, initial_profile())
    db.add(profile)
    db.commit()

    token = get_serializer().dumps(anon.id)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_COOKIE_MAX_AGE,
    )
    return SessionOut(sessionId=anon.id, createdAt=anon.created_at)
