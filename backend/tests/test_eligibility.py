from app.services.eligibility import (
    DEMO_PROFILE,
    check_rule,
    evaluate_scheme,
    get_matches,
    initial_profile,
    missing_docs,
)

AGE_RULE = {"field": "age", "operator": "ageBetween", "value": "18-35", "label": "Age 18–35"}
INCOME_RULE = {
    "field": "incomeBand",
    "operator": "incomeAtMost",
    "value": "15to3",
    "label": "Household income up to ₹3 lakh/year",
}
INCLUDES_RULE = {"field": "situations", "operator": "includes", "value": "farmer", "label": "Farming household"}
EQUALS_RULE = {"field": "enrolled", "operator": "equals", "value": "yes", "label": "Currently enrolled"}
ONE_OF_RULE = {
    "field": "situations",
    "operator": "oneOf",
    "value": ["jobseeker", "employed", "student"],
    "label": "Seeking work, studying, or working",
}

TINY_SCHEME = {
    "id": "tiny",
    "name": "Tiny Test Scheme",
    "rules": [AGE_RULE, INCOME_RULE],
    "requiredDocuments": ["identity"],
}


def profile(**overrides):
    base = initial_profile()
    base.update(overrides)
    return base


# --- check_rule: the unknown vs unmet distinction ---


def test_age_rule_unknown_when_age_unset():
    assert check_rule(AGE_RULE, profile(age=None)) == "unknown"


def test_age_rule_met_within_range():
    assert check_rule(AGE_RULE, profile(age=25)) == "met"


def test_age_rule_unmet_outside_range():
    assert check_rule(AGE_RULE, profile(age=40)) == "unmet"


def test_income_rule_unknown_when_band_is_literal_unknown():
    assert check_rule(INCOME_RULE, profile(incomeBand="unknown")) == "unknown"


def test_income_rule_met_at_exact_threshold():
    assert check_rule(INCOME_RULE, profile(incomeBand="15to3")) == "met"


def test_income_rule_unmet_above_threshold():
    assert check_rule(INCOME_RULE, profile(incomeBand="above5")) == "unmet"


def test_includes_rule_unknown_when_situations_empty():
    assert check_rule(INCLUDES_RULE, profile(situations=[])) == "unknown"


def test_includes_rule_met_when_present():
    assert check_rule(INCLUDES_RULE, profile(situations=["farmer"])) == "met"


def test_includes_rule_unmet_when_absent_but_answered():
    assert check_rule(INCLUDES_RULE, profile(situations=["student"])) == "unmet"


def test_equals_rule_unknown_when_field_is_unknown_string():
    assert check_rule(EQUALS_RULE, profile(enrolled="unknown")) == "unknown"


def test_equals_rule_met():
    assert check_rule(EQUALS_RULE, profile(enrolled="yes")) == "met"


def test_equals_rule_unmet():
    assert check_rule(EQUALS_RULE, profile(enrolled="no")) == "unmet"


def test_one_of_rule_met_against_list_field():
    assert check_rule(ONE_OF_RULE, profile(situations=["employed"])) == "met"


def test_one_of_rule_unmet_against_list_field():
    assert check_rule(ONE_OF_RULE, profile(situations=["farmer"])) == "unmet"


def test_missing_docs_returns_only_absent_required_docs():
    scheme = {"requiredDocuments": ["identity", "income", "education"]}
    result = missing_docs(scheme, profile(documents=["identity"]))
    assert result == ["income", "education"]


# --- evaluate_scheme: the four match levels, with precedence ---


def test_strong_match_when_all_rules_met_and_docs_available():
    result = evaluate_scheme(TINY_SCHEME, profile(age=25, incomeBand="15to3", documents=["identity"]))
    assert result["level"] == "strong"
    assert result["missingInfo"] == []
    assert result["missingDocuments"] == []
    assert result["failedRules"] == []


def test_possible_match_when_rules_met_but_doc_missing():
    result = evaluate_scheme(TINY_SCHEME, profile(age=25, incomeBand="15to3", documents=[]))
    assert result["level"] == "possible"
    assert result["missingDocuments"] == ["identity"]


def test_more_info_when_a_rule_field_is_unknown_even_with_docs_present():
    # age unset -> unknown, income met, doc present. This must NOT be
    # "explore" (that would wrongly imply the person fails to qualify).
    result = evaluate_scheme(TINY_SCHEME, profile(age=None, incomeBand="15to3", documents=["identity"]))
    assert result["level"] == "moreInfo"
    assert result["missingInfo"] == ["Age 18–35"]
    assert result["failedRules"] == []


def test_explore_when_any_rule_is_unmet_even_if_others_are_unknown():
    # income explicitly fails; age is unanswered. unmet must win over unknown.
    result = evaluate_scheme(TINY_SCHEME, profile(age=None, incomeBand="above5", documents=["identity"]))
    assert result["level"] == "explore"
    assert result["failedRules"] == ["Household income up to ₹3 lakh/year"]


def test_unmet_beats_missing_docs_for_level_precedence():
    result = evaluate_scheme(TINY_SCHEME, profile(age=40, incomeBand="15to3", documents=[]))
    assert result["level"] == "explore"


def test_unknown_beats_missing_docs_for_level_precedence():
    result = evaluate_scheme(TINY_SCHEME, profile(age=None, incomeBand="15to3", documents=[]))
    assert result["level"] == "moreInfo"


# --- get_matches: sort order ---


def test_get_matches_orders_strong_before_possible_before_more_info_before_explore():
    strong_scheme = {**TINY_SCHEME, "id": "strong-one"}
    explore_scheme = {
        "id": "explore-one",
        "rules": [{"field": "age", "operator": "ageBetween", "value": "60-90", "label": "Age 60+"}],
        "requiredDocuments": [],
    }
    schemes = [explore_scheme, strong_scheme]
    matches = get_matches(schemes, profile(age=25, incomeBand="15to3", documents=["identity"]))
    assert [m["scheme"]["id"] for m in matches] == ["strong-one", "explore-one"]
    assert matches[0]["level"] == "strong"
    assert matches[1]["level"] == "explore"


# --- demo profile fixture, reused by router tests too ---


def test_demo_profile_matches_expected_levels_against_real_schemes():
    from app.seed.schemes_seed import SCHEMES_DATA

    # SCHEMES_DATA rules use the exact same shape check_rule expects.
    matches = get_matches(SCHEMES_DATA, DEMO_PROFILE)
    levels = {m["scheme"]["id"]: m["level"] for m in matches}

    assert levels["kaushal-nayi-raah"] == "strong"
    assert levels["nayi-disha"] == "possible"
    assert levels["swasthya-saathi"] == "possible"
    assert levels["udyam-shuru"] == "moreInfo"
    assert levels["ghar-urja"] == "moreInfo"
    assert levels["kisan-sahayog"] == "explore"

    # The brief requires the demo profile to produce both strong and
    # incomplete/possible matches - assert that property directly too.
    assert any(level == "strong" for level in levels.values())
    assert any(level in ("possible", "moreInfo") for level in levels.values())
