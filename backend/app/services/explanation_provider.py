"""The `ExplanationProvider` seam.

Routers depend on this interface, not on services.explanations directly,
so a future real-LLM provider could be swapped in later without touching
router code. For this prototype only `DeterministicExplanationProvider`
exists - no LLM/API-key integration is built or stubbed here, by design
(see README "AI role" section).
"""

from typing import Any, Protocol

from . import explanations


class ExplanationProvider(Protocol):
    def simple_terms(self, profile: dict[str, Any], matches: list[dict[str, Any]]) -> str: ...

    def fit_explanation(self, match: dict[str, Any], document_labels: dict[str, str]) -> str: ...

    def plan_tasks(
        self,
        scheme: dict[str, Any],
        profile: dict[str, Any],
        document_labels: dict[str, str],
        existing: dict[str, bool] | None = None,
    ) -> list[dict[str, Any]]: ...

    def explain_task(self, task: dict[str, Any], question: str) -> str: ...


class DeterministicExplanationProvider:
    """Template-based, local, no network calls - the only provider this
    prototype ships. Mirrors src/lib/explanations.ts exactly."""

    def simple_terms(self, profile: dict[str, Any], matches: list[dict[str, Any]]) -> str:
        return explanations.simple_terms(profile, matches)

    def fit_explanation(self, match: dict[str, Any], document_labels: dict[str, str]) -> str:
        return explanations.fit_explanation(match, document_labels)

    def plan_tasks(
        self,
        scheme: dict[str, Any],
        profile: dict[str, Any],
        document_labels: dict[str, str],
        existing: dict[str, bool] | None = None,
    ) -> list[dict[str, Any]]:
        return explanations.plan_tasks(scheme, profile, document_labels, existing)

    def explain_task(self, task: dict[str, Any], question: str) -> str:
        return explanations.explain_task(task, question)


def get_explanation_provider() -> ExplanationProvider:
    return DeterministicExplanationProvider()
