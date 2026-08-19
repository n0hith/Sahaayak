"""Small repository helpers for loading Scheme + Rule rows as the camelCase
dicts the eligibility/explanation engines expect. Shared by routers/schemes.py,
routers/match.py, and routers/plan.py so the join logic lives in one place.
"""

from typing import Any, Optional

from sqlmodel import Session, select

from ..models.scheme import Rule, Scheme
from .mapper import scheme_to_dict


def load_scheme_dict(db: Session, scheme_id: str) -> Optional[dict[str, Any]]:
    scheme = db.get(Scheme, scheme_id)
    if scheme is None:
        return None
    rules = db.exec(select(Rule).where(Rule.scheme_id == scheme_id)).all()
    return scheme_to_dict(scheme, list(rules))


def load_all_scheme_dicts(db: Session) -> list[dict[str, Any]]:
    schemes = db.exec(select(Scheme)).all()
    all_rules = db.exec(select(Rule)).all()
    rules_by_scheme: dict[str, list[Rule]] = {}
    for rule in all_rules:
        rules_by_scheme.setdefault(rule.scheme_id, []).append(rule)
    return [scheme_to_dict(scheme, rules_by_scheme.get(scheme.id, [])) for scheme in schemes]
