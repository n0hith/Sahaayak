"""Byte-for-byte port of src/lib/eligibility.ts.

Operates on plain dicts keyed exactly like the frontend's `Profile` /
`Scheme` / `Rule` TypeScript interfaces (camelCase field names), not on
the SQLModel ORM rows or snake_case DB columns - see services/mapper.py
for the translation layer. This keeps the matching semantics a direct,
checkable mirror of the TypeScript source rather than a reinterpretation.

The one rule that must never be simplified away: `unknown` (the profile
field was never answered) and `unmet` (the profile field was answered and
it fails the rule) are different states, and they produce different match
levels. Losing that distinction is exactly the "approved vs. guaranteed"
overclaiming this app exists to avoid.
"""

from typing import Any, Literal

RuleState = Literal["met", "unmet", "unknown"]
MatchLevel = Literal["strong", "possible", "moreInfo", "explore"]

INCOME_RANK: dict[str, int | None] = {
    "under15": 1,
    "15to3": 2,
    "3to5": 3,
    "above5": 4,
    "unknown": None,
}

INCOME_LABEL: dict[str, str] = {
    "under15": "under ₹1.5 lakh/year",
    "15to3": "₹1.5–3 lakh/year",
    "3to5": "₹3–5 lakh/year",
    "above5": "above ₹5 lakh/year",
    "unknown": "not shared",
}

_LEVEL_ORDER: dict[str, int] = {"strong": 0, "possible": 1, "moreInfo": 2, "explore": 3}


def check_rule(rule: dict[str, Any], profile: dict[str, Any]) -> RuleState:
    field = rule["field"]
    current = profile.get(field)

    if current is None or current == "unknown" or (isinstance(current, list) and len(current) == 0):
        return "unknown"

    operator = rule["operator"]
    value = rule["value"]

    if operator == "ageBetween":
        lo_str, hi_str = str(value).split("-")
        lo, hi = int(lo_str), int(hi_str)
        # isinstance(True, int) is True in Python but booleans never reach
        # here for an age field, so this mirrors the TS `typeof === 'number'` guard.
        return "met" if isinstance(current, int) and lo <= current <= hi else "unmet"

    if operator == "incomeAtMost":
        limit = INCOME_RANK.get(str(value))
        current_rank = INCOME_RANK.get(current) if isinstance(current, str) else None
        return "met" if current_rank is not None and limit is not None and current_rank <= limit else "unmet"

    if operator == "equals":
        return "met" if current == value else "unmet"

    if operator == "includes":
        return "met" if isinstance(current, list) and value in current else "unmet"

    if operator == "oneOf":
        accepted = value if isinstance(value, list) else [value]
        accepted_strs = [str(item) for item in accepted]
        if isinstance(current, list):
            return "met" if any(str(item) in accepted_strs for item in current) else "unmet"
        return "met" if str(current) in accepted_strs else "unmet"

    return "unknown"


def missing_docs(scheme: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    required = scheme.get("requiredDocuments", [])
    have = profile.get("documents", [])
    return [doc for doc in required if doc not in have]


def evaluate_scheme(scheme: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    states = [(rule, check_rule(rule, profile)) for rule in scheme.get("rules", [])]
    unmet = [rule["label"] for rule, state in states if state == "unmet"]
    unknown = [rule["label"] for rule, state in states if state == "unknown"]
    reasons = [rule["label"] for rule, state in states if state == "met"]
    docs = missing_docs(scheme, profile)

    level: MatchLevel
    if unmet:
        level = "explore"
    elif unknown:
        level = "moreInfo"
    elif docs:
        level = "possible"
    else:
        level = "strong"

    return {
        "scheme": scheme,
        "level": level,
        "reasons": reasons,
        "missingInfo": unknown,
        "missingDocuments": docs,
        "failedRules": unmet,
    }


def get_matches(schemes: list[dict[str, Any]], profile: dict[str, Any]) -> list[dict[str, Any]]:
    results = [evaluate_scheme(scheme, profile) for scheme in schemes]
    return sorted(results, key=lambda result: _LEVEL_ORDER[result["level"]])


def rule_friendly_text(rule: dict[str, Any]) -> str:
    return rule["label"]


def document_name(doc_id: str, document_labels: dict[str, str]) -> str:
    return document_labels.get(doc_id, doc_id)


def profile_at_a_glance(profile: dict[str, Any]) -> str:
    location = profile.get("location", "unknown")
    place = "location not shared" if location == "unknown" else location
    income = INCOME_LABEL.get(profile.get("incomeBand", "unknown"), "not shared")
    situations = profile.get("situations") or []
    roles = ", ".join(situations).replace("jobseeker", "job seeker") if situations else "situation not shared"
    age = profile.get("age")
    age_text = f"age {age}" if age else "age not shared"
    return f"{age_text} · {place} · {income} · {roles}"


DEMO_PROFILE: dict[str, Any] = {
    "age": 20,
    "region": "Sundar Pradesh (demo)",
    "language": "en",
    "householdSize": 4,
    "incomeBand": "15to3",
    "location": "town",
    "cleanCooking": "unknown",
    "situations": ["student", "jobseeker"],
    "educationStage": "higher",
    "enrolled": "yes",
    "landholding": "unknown",
    "trainingArea": "Digital services",
    "planningBusiness": "unknown",
    "documents": ["identity", "education"],
}


def initial_profile(language: str = "en") -> dict[str, Any]:
    return {
        "age": None,
        "region": None,
        "language": language,
        "householdSize": None,
        "incomeBand": "unknown",
        "location": "unknown",
        "cleanCooking": "unknown",
        "situations": [],
        "educationStage": "unknown",
        "enrolled": "unknown",
        "landholding": "unknown",
        "trainingArea": None,
        "planningBusiness": "unknown",
        "documents": [],
    }
