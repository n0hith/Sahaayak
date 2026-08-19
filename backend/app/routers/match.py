from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..db import get_session
from ..deps import get_current_session
from ..models.session import AnonymousSession
from ..schemas.match import MatchResponse, MatchResultOut
from ..seed.document_labels import DOCUMENT_LABELS
from ..services.eligibility import get_matches
from ..services.explanation_provider import get_explanation_provider
from ..services.mapper import profile_to_dict
from ..services.profile_repo import get_profile_or_404
from ..services.scheme_repo import load_all_scheme_dicts

router = APIRouter(prefix="/api/match", tags=["match"])


@router.post("", response_model=MatchResponse)
def run_match(
    anon: AnonymousSession = Depends(get_current_session),
    db: Session = Depends(get_session),
) -> MatchResponse:
    """Runs the full eligibility engine (services/eligibility.py) against
    the session's current profile and every seeded scheme, and includes
    the deterministic "in simple terms" summary in the same response so
    the frontend's Results screen needs only one call."""
    profile = profile_to_dict(get_profile_or_404(db, anon))
    schemes = load_all_scheme_dicts(db)
    matches = get_matches(schemes, profile)
    provider = get_explanation_provider()
    return MatchResponse(
        matches=[MatchResultOut(**match) for match in matches],
        simpleTerms=provider.simple_terms(profile, matches),
    )
