from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models.profile import Profile
from ..models.session import AnonymousSession


def get_profile_or_404(db: Session, anon: AnonymousSession) -> Profile:
    profile = db.exec(select(Profile).where(Profile.session_id == anon.id)).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No profile for this session yet.")
    return profile
