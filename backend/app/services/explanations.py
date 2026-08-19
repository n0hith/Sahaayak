"""Port of src/lib/explanations.ts - the deterministic "AI" / explanation
layer. Every function here is a pure template over structured data: the
user's selected profile answers and the matched scheme's mock rules. There
is no LLM call, no network access, and no free-text generation - see
services/explanation_provider.py for the seam a future real-LLM provider
could be plugged into without touching this module's contract.
"""

from typing import Any

from .eligibility import document_name, profile_at_a_glance


def simple_terms(profile: dict[str, Any], matches: list[dict[str, Any]]) -> str:
    top = [match for match in matches if match["level"] != "explore"][:3]
    if not top:
        return (
            "We need a little more information before we can suggest a useful next step. "
            "You can still explore the demo schemes below."
        )
    names = ", ".join(
        match["scheme"]["name"].replace(" Support", "").replace(" Voucher", "") for match in top
    )
    uncertainty = (
        " A few items still need confirming, so these are guidance—not approval."
        if any(match["level"] != "strong" for match in top)
        else " These are strong demo matches based on the answers you shared."
    )
    return f"You told us: {profile_at_a_glance(profile)}. The clearest places to start are {names}.{uncertainty}"


def fit_explanation(match: dict[str, Any], document_labels: dict[str, str]) -> str:
    level = match["level"]
    if level == "strong":
        reasons = ", ".join(match["reasons"]).lower()
        return (
            f"Your answers match the main demo conditions: {reasons}. "
            "Please still confirm current requirements with the official provider."
        )
    if level == "possible":
        docs = ", ".join(document_name(doc, document_labels) for doc in match["missingDocuments"]).lower()
        return f"Your answers meet the main demo conditions. Before you continue, prepare or confirm {docs}."
    if level == "moreInfo":
        info = ", ".join(match["missingInfo"]).lower()
        return f"This could be relevant, but we cannot tell yet because {info} needs confirmation."
    failed = ", ".join(match["failedRules"]).lower()
    return (
        f"This is not one of your current matches because {failed} does not match the demo conditions. "
        "You can still explore it and update your answers later."
    )


def plan_tasks(
    scheme: dict[str, Any],
    profile: dict[str, Any],
    document_labels: dict[str, str],
    existing: dict[str, bool] | None = None,
) -> list[dict[str, Any]]:
    existing = existing or {}
    documents: list[dict[str, Any]] = []
    for doc in scheme["requiredDocuments"]:
        available = doc in profile.get("documents", [])
        task_id = f"doc-{doc}"
        label = document_name(doc, document_labels)
        documents.append(
            {
                "id": task_id,
                "title": f"{label} is marked available" if available else f"Gather {label}",
                "description": (
                    "Keep a current copy ready for the official provider."
                    if available
                    else "Check the latest official requirements before requesting or sharing this document."
                ),
                "status": "available" if available else "needed",
                "done": existing.get(task_id, available),
            }
        )
    fixed = [
        {
            "id": "official-instructions",
            "title": "Read the official application instructions",
            "description": "Check the official provider’s current eligibility, dates, fees, and process.",
            "status": "needed",
            "done": existing.get("official-instructions", False),
        },
        {
            "id": "provider-check",
            "title": "Confirm eligibility with the official provider",
            "description": "Ask about anything that is unclear before submitting documents.",
            "status": "needed",
            "done": existing.get("provider-check", False),
        },
        {
            "id": "secure-copy",
            "title": "Keep your acknowledgement safely",
            "description": "After using an official channel, save the reference number somewhere secure.",
            "status": "optional",
            "done": existing.get("secure-copy", False),
        },
    ]
    return documents + fixed


def explain_task(task: dict[str, Any], question: str) -> str:
    if question == "why":
        return (
            f"{task['title']} helps the official provider check the mock conditions. "
            "Sahaayak does not review or receive the document."
        )
    if question == "missing":
        if task["status"] == "available":
            return (
                "You have marked this as available. Make sure it is current, readable, "
                "and only share it through a verified official channel."
            )
        return (
            "Check the official provider’s current instructions. They can tell you whether "
            "an alternative document or a local support centre can help."
        )
    # question == "first"
    if task["status"] == "needed":
        return f'Start with "{task["title"]}". It is one of the items that could hold up preparation.'
    return "Start by reading the official instructions, then complete the still-needed items one at a time."
