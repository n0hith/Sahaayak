from fastapi import Depends, HTTPException, Request, status
from itsdangerous import BadSignature, URLSafeSerializer
from sqlmodel import Session

from .config import settings
from .db import get_session
from .models.session import AnonymousSession

SESSION_COOKIE_NAME = "sahaayak_session"
SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


def get_serializer() -> URLSafeSerializer:
    return URLSafeSerializer(settings.session_secret, salt="sahaayak-session")


def get_current_session(
    request: Request,
    db: Session = Depends(get_session),
) -> AnonymousSession:
    """Resolves the signed session cookie into an AnonymousSession row.

    There is no login/password/OTP path anywhere in this API - the cookie
    is the entire "account" model, and it carries nothing but an opaque
    UUID (see models/session.py).
    """
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active session. Call POST /api/session first.",
        )
    try:
        session_id = get_serializer().loads(token)
    except BadSignature as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token.",
        ) from exc

    anon = db.get(AnonymousSession, session_id)
    if anon is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found. Call POST /api/session first.",
        )
    return anon
