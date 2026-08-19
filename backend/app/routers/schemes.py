from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..db import get_session
from ..deps import get_current_session
from ..models.session import AnonymousSession
from ..schemas.scheme import ExplanationResponse, SchemeListResponse, SchemeOut
from ..seed.document_labels import DOCUMENT_LABELS
from ..services.eligibility import evaluate_scheme
from ..services.explanation_provider import get_explanation_provider
from ..services.mapper import profile_to_dict
from ..services.profile_repo import get_profile_or_404
from ..services.scheme_repo import load_all_scheme_dicts, load_scheme_dict

router = APIRouter(prefix="/api/schemes", tags=["schemes"])


@router.get("", response_model=SchemeListResponse)
def list_schemes(db: Session = Depends(get_session)) -> SchemeListResponse:
    schemes = load_all_scheme_dicts(db)
    return SchemeListResponse(schemes=[SchemeOut(**s) for s in schemes], documentLabels=DOCUMENT_LABELS)


@router.get("/{scheme_id}", response_model=SchemeOut)
def get_scheme(scheme_id: str, db: Session = Depends(get_session)) -> SchemeOut:
    scheme = load_scheme_dict(db, scheme_id)
    if scheme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found.")
    return SchemeOut(**scheme)


@router.get("/{scheme_id}/explanation", response_model=ExplanationResponse)
def get_scheme_explanation(
    scheme_id: str,
    anon: AnonymousSession = Depends(get_current_session),
    db: Session = Depends(get_session),
) -> ExplanationResponse:
    scheme = load_scheme_dict(db, scheme_id)
    if scheme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found.")
    profile = profile_to_dict(get_profile_or_404(db, anon))
    match = evaluate_scheme(scheme, profile)
    provider = get_explanation_provider()
    return ExplanationResponse(explanation=provider.fit_explanation(match, DOCUMENT_LABELS))
