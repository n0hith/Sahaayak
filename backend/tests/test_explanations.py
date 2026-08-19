from app.seed.document_labels import DOCUMENT_LABELS
from app.seed.schemes_seed import SCHEMES_DATA
from app.services.eligibility import DEMO_PROFILE, evaluate_scheme, get_matches
from app.services.explanations import explain_task, fit_explanation, plan_tasks, simple_terms

SCHEMES_BY_ID = {scheme["id"]: scheme for scheme in SCHEMES_DATA}


def test_simple_terms_mentions_top_three_and_profile_summary():
    matches = get_matches(SCHEMES_DATA, DEMO_PROFILE)
    text = simple_terms(DEMO_PROFILE, matches)
    assert "age 20" in text
    assert "town" in text
    assert "Kaushal Nayi Raah Training" in text
    assert "guidance" in text.lower() or "strong demo matches" in text.lower()


def test_simple_terms_handles_no_useful_matches():
    # age is *answered* (5) so the rule is genuinely unmet ("explore"),
    # not merely unanswered ("moreInfo") - that distinction is the point.
    answered_profile = {"age": 5, "location": "unknown", "incomeBand": "unknown", "situations": [], "documents": []}
    all_explore_schemes = [
        {
            "id": "impossible",
            "name": "Impossible Scheme",
            "rules": [{"field": "age", "operator": "equals", "value": 999, "label": "Age 999"}],
            "requiredDocuments": [],
        }
    ]
    matches = get_matches(all_explore_schemes, answered_profile)
    assert matches[0]["level"] == "explore"
    text = simple_terms(answered_profile, matches)
    assert "need a little more information" in text


def test_fit_explanation_strong_cites_reasons():
    scheme = SCHEMES_BY_ID["kaushal-nayi-raah"]
    match = evaluate_scheme(scheme, DEMO_PROFILE)
    assert match["level"] == "strong"
    text = fit_explanation(match, DOCUMENT_LABELS)
    assert "match the main demo conditions" in text
    assert "official provider" in text


def test_fit_explanation_possible_lists_missing_documents():
    scheme = SCHEMES_BY_ID["nayi-disha"]
    match = evaluate_scheme(scheme, DEMO_PROFILE)
    assert match["level"] == "possible"
    text = fit_explanation(match, DOCUMENT_LABELS)
    assert "prepare or confirm" in text
    assert "income certificate" in text.lower()


def test_fit_explanation_more_info_cites_missing_info():
    scheme = SCHEMES_BY_ID["ghar-urja"]
    match = evaluate_scheme(scheme, DEMO_PROFILE)
    assert match["level"] == "moreInfo"
    text = fit_explanation(match, DOCUMENT_LABELS)
    assert "cannot tell yet" in text


def test_fit_explanation_explore_cites_failed_rules():
    scheme = SCHEMES_BY_ID["kisan-sahayog"]
    match = evaluate_scheme(scheme, DEMO_PROFILE)
    assert match["level"] == "explore"
    text = fit_explanation(match, DOCUMENT_LABELS)
    assert "does not match the demo conditions" in text


def test_plan_tasks_marks_available_docs_done_and_needed_docs_not_done():
    scheme = SCHEMES_BY_ID["nayi-disha"]
    tasks = plan_tasks(scheme, DEMO_PROFILE, DOCUMENT_LABELS)
    by_id = {task["id"]: task for task in tasks}

    assert by_id["doc-identity"]["status"] == "available"
    assert by_id["doc-identity"]["done"] is True
    assert by_id["doc-education"]["status"] == "available"
    assert by_id["doc-income"]["status"] == "needed"
    assert by_id["doc-income"]["done"] is False

    # three fixed tasks always present
    for fixed_id in ("official-instructions", "provider-check", "secure-copy"):
        assert fixed_id in by_id


def test_plan_tasks_preserves_existing_checkbox_state():
    scheme = SCHEMES_BY_ID["nayi-disha"]
    existing = {"official-instructions": True, "doc-income": True}
    tasks = plan_tasks(scheme, DEMO_PROFILE, DOCUMENT_LABELS, existing)
    by_id = {task["id"]: task for task in tasks}
    assert by_id["official-instructions"]["done"] is True
    # doc-income is "needed" (not available) but was manually checked before
    assert by_id["doc-income"]["done"] is True


def test_explain_task_why():
    task = {"id": "doc-income", "title": "Gather Income certificate (example)", "status": "needed"}
    text = explain_task(task, "why")
    assert "Gather Income certificate (example)" in text
    assert "does not review or receive the document" in text


def test_explain_task_missing_when_available():
    task = {"id": "doc-identity", "title": "x", "status": "available"}
    text = explain_task(task, "missing")
    assert "verified official channel" in text


def test_explain_task_missing_when_needed():
    task = {"id": "doc-income", "title": "x", "status": "needed"}
    text = explain_task(task, "missing")
    assert "local support centre" in text


def test_explain_task_first_prioritizes_needed_task():
    task = {"id": "doc-income", "title": "Gather Income certificate", "status": "needed"}
    text = explain_task(task, "first")
    assert "Start with" in text


def test_explain_task_first_falls_back_for_non_needed_task():
    task = {"id": "secure-copy", "title": "x", "status": "optional"}
    text = explain_task(task, "first")
    assert "Start by reading the official instructions" in text
