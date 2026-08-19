"""Translates between snake_case SQLModel rows (the DB/ORM convention) and
the camelCase dicts the eligibility/explanation engines and the frontend
both expect (the src/types.ts convention). Keeping this in one place means
services/eligibility.py and services/explanations.py never need to know
about the ORM at all.
"""

from typing import Any

from ..models.plan import PlanTask
from ..models.profile import Profile
from ..models.scheme import Rule, Scheme


def profile_to_dict(profile: Profile) -> dict[str, Any]:
    return {
        "age": profile.age,
        "region": profile.region,
        "language": profile.language,
        "householdSize": profile.household_size,
        "incomeBand": profile.income_band,
        "location": profile.location,
        "cleanCooking": profile.clean_cooking,
        "situations": profile.situations,
        "educationStage": profile.education_stage,
        "enrolled": profile.enrolled,
        "landholding": profile.landholding,
        "trainingArea": profile.training_area,
        "planningBusiness": profile.planning_business,
        "documents": profile.documents,
    }


def apply_profile_dict(profile: Profile, data: dict[str, Any]) -> None:
    profile.age = data.get("age")
    profile.region = data.get("region")
    profile.language = data.get("language", "en")
    profile.household_size = data.get("householdSize")
    profile.income_band = data.get("incomeBand", "unknown")
    profile.location = data.get("location", "unknown")
    profile.clean_cooking = data.get("cleanCooking", "unknown")
    profile.situations = data.get("situations", [])
    profile.education_stage = data.get("educationStage", "unknown")
    profile.enrolled = data.get("enrolled", "unknown")
    profile.landholding = data.get("landholding", "unknown")
    profile.training_area = data.get("trainingArea")
    profile.planning_business = data.get("planningBusiness", "unknown")
    profile.documents = data.get("documents", [])


def scheme_to_dict(scheme: Scheme, rules: list[Rule]) -> dict[str, Any]:
    return {
        "id": scheme.id,
        "name": scheme.name,
        "icon": scheme.icon,
        "category": scheme.category,
        "summary": scheme.summary,
        "whoItMayHelp": scheme.who_it_may_help,
        "support": scheme.support,
        "rules": [
            {"field": rule.field, "operator": rule.operator, "value": rule.value, "label": rule.label}
            for rule in rules
        ],
        "requiredDocuments": scheme.required_documents,
        "optionalDocuments": scheme.optional_documents,
        "preparationTime": scheme.preparation_time,
        "nextSteps": scheme.next_steps,
        "availability": scheme.availability,
        "privacyNote": scheme.privacy_note,
    }


def plan_task_to_dict(task: PlanTask) -> dict[str, Any]:
    return {
        "id": task.task_key,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "done": task.done,
    }
