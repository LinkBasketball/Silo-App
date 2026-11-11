"""NLP: classification, rhetoric metrics, quotes, neutral summaries and guardrails."""
from app.nlp.analysis import analyze_text, verify_summary
from app.nlp.engine import RulesEngine, parse


def classes(text):
    return [s["sentence_class"] for s in analyze_text(parse(text))["sentences"]]


def test_sentence_classes():
    assert classes("Unemployment fell to 4.1 percent in the third quarter of 2026.") == ["checkable_fact"]
    assert classes("Lawmakers should pass the bill without delay.") == ["normative"]
    assert classes("Next year, wages will rise.") == ["prediction"]
    assert classes("I believe this is a wonderful plan.") == ["opinion"]
    assert classes("The disastrous plan cut 300 jobs in 2025.") == ["mixed"]
    assert classes("Is this the right plan?") == ["ambiguous"]


def test_attributed_quote_is_checkable():
    r = analyze_text(parse("“This bill is a lifeline for every family on the river,” said Candidate A."))
    assert r["claims"][0]["claim_type"] == "attributed_quote"
    assert r["quotes"][0]["speaker"] == "Candidate A"


def test_label_boundary_split():
    r = analyze_text(parse("The bill passed, said Candidate A. Experts say it is the best plan."))
    assert len(r["sentences"]) == 2


def test_adjective_noun_ratio_and_density():
    r = analyze_text(parse("The disastrous bill devastated the economy."))["rhetoric"]
    assert r["adjective_count"] == 1 and r["noun_count"] == 2
    assert r["adjective_noun_ratio"] == 0.5
    assert r["emotional_term_count"] == 2
    assert r["emotional_density"] == round(2 / 6, 4)


def test_spec_example_neutral_summary():
    r = analyze_text(parse("The disastrous bill devastated the economy."), voice="speech")
    out = r["neutral_summary"]["items"][0]["neutral"]
    assert out.startswith("The speaker characterizes the bill negatively")
    assert "No supporting data is provided" in out


def test_original_text_never_modified():
    text = "“We will never stop fighting this corrupt, disastrous plan,” said Candidate B. The plan passed 31 to 19."
    r = analyze_text(parse(text))
    q = r["quotes"][0]["text"]
    assert q in text
    assert f"“{q}”" in r["neutral_summary"]["text"]
    assert r["neutral_summary"]["integrity"]["quotes_preserved"]


def test_loaded_modifiers_removed_only_in_summary():
    r = analyze_text(parse("The heroic senator voted for the bill on April 14, 2026."))
    item = r["neutral_summary"]["items"][0]
    main_clause = item["neutral"].split(" It also uses")[0]
    assert "heroic" not in main_clause and "heroic" in item["original"]
    assert item["removed_modifiers"] == ["heroic"]


def test_verify_summary_catches_altered_quote_and_endorsement():
    v = verify_summary("He said “the plan is fine.”", "He is quoted: “the plan is great.” You should vote for him.")
    assert not v["passed"] and not v["quotes_preserved"] and v["endorsements_introduced"]


def test_language_audit_types():
    r = analyze_text(parse("Experts say the mayor is corrupt. Clearly, this is a disastrous plan."))
    types = {f["type"] for f in r["language_audit"]}
    assert {"vague_attribution", "unsupported_certainty", "loaded_language"} <= types
    assert "unattributed_allegation" in types


def test_allegation_attributed_is_not_unattributed():
    r = analyze_text(parse("Candidate B said the deal was corrupt."))
    assert all(f["type"] != "unattributed_allegation" for f in r["language_audit"])


def test_context_gaps():
    r = analyze_text(parse("Factory jobs grew 40 percent. Pollution has doubled. Experts say this is the best economy."))
    types = {g["type"] for g in r["context_gaps"]}
    assert {"missing_time_period", "missing_baseline", "unnamed_source", "incomplete_comparison"} <= types


def test_topic_distribution_sums_to_one():
    t = analyze_text(parse("The budget surplus grew. The river pollution fell. Clinics closed in rural counties."))["topics"]
    assert abs(sum(d["share"] for d in t["distribution"]) - 1) < 0.01
    assert "not a measure of political bias" in t["note"]


def test_rules_engine_fallback_works():
    doc = RulesEngine().parse("Unemployment fell 4 percent in 2025. Lawmakers should act. The disastrous plan failed.")
    r = analyze_text(doc)
    assert r["engine"] == "rules-fallback"
    assert len(r["sentences"]) == 3
    assert r["sentences"][0]["sentence_class"] == "checkable_fact"
    assert r["sentences"][1]["sentence_class"] == "normative"
