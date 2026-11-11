from app.services.scoring import alignment_index, coverage


def ev(rel, st="primary_record"):
    return {"relationship": rel, "source_type": st}


def test_insufficient_when_too_few_claims():
    r = coverage([{"evidence": [ev("supports")]}])
    assert r["state"] == "insufficient_evidence" and r["score"] is None


def test_insufficient_when_nothing_assessed():
    r = coverage([{"evidence": [ev("provides_context")]}, {"evidence": []}])
    assert r["state"] == "insufficient_evidence"
    assert r["claims_context_only"] == 1 and r["claims_lacking_evidence"] == 1


def test_formula():
    claims = [
        {"evidence": [ev("supports")]},                               # 1.0
        {"evidence": [ev("contradicts", "secondary_reporting")]},     # 0.6
        {"evidence": [ev("provides_context")]},                       # 0.5
        {"evidence": []},                                             # 0
    ]
    r = coverage(claims)
    assert r["score"] == round(100 * 2.1 / 4) == 52
    assert r["band"] == "Partial coverage"
    assert (r["claims_supported"], r["claims_conflicting"], r["claims_context_only"], r["claims_lacking_evidence"]) == (1, 1, 1, 1)


def test_contradiction_counts_as_coverage_not_truth():
    supported = coverage([{"evidence": [ev("supports")]}] * 2)
    contradicted = coverage([{"evidence": [ev("contradicts")]}] * 2)
    assert supported["score"] == contradicted["score"] == 100
    assert contradicted["claims_conflicting"] == 2


def test_best_evidence_wins():
    r = coverage([{"evidence": [ev("provides_context"), ev("supports")]}, {"evidence": [ev("supports")]}])
    assert r["score"] == 100


def test_alignment_requires_minimum():
    links = [{"classification": "consistent", "is_procedural": False}] * 3
    assert alignment_index(links)["state"] == "insufficient_evidence"


def test_alignment_excludes_procedural_and_noncomparable():
    links = ([{"classification": "consistent", "is_procedural": False}] * 3
             + [{"classification": "mixed", "is_procedural": False}]
             + [{"classification": "potentially_inconsistent", "is_procedural": True}]
             + [{"classification": "not_directly_comparable", "is_procedural": False}])
    r = alignment_index(links)
    assert r["comparable"] == 4 and r["excluded"] == 2
    assert r["value"] == round(100 * 3.5 / 4)
