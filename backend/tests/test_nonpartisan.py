"""Paired-swap regression tests: exchanging actors, parties or positions while keeping the
evidence structure identical must not change any score, classification or requirement.

Limitation: these tests show the *rules* are symmetric for the pairs below. They cannot prove
that the lexicons or the curated demonstration annotations are free of bias."""
import pytest

from app.nlp.analysis import analyze_text
from app.nlp.engine import parse
from app.services.scoring import alignment_index, coverage

PAIRS = [
    ("Senator Ross of the Harbor Party voted for the bill on May 3, 2026.",
     "Senator Diaz of the Summit Party voted for the bill on May 3, 2026."),
    ("The reckless Harbor Party plan will destroy jobs.",
     "The reckless Summit Party plan will destroy jobs."),
    ("Candidate A said the tax cut was a disastrous giveaway.",
     "Candidate B said the spending bill was a disastrous giveaway."),
    ("Experts say the conservative proposal is clearly the best option.",
     "Experts say the progressive proposal is clearly the best option."),
    ("“This heroic reform will save our state,” said Candidate A.",
     "“This heroic reform will save our state,” said Candidate B."),
    ("Candidate A said the tax cut was approved on March 3, 2026.",
     "Candidate B said the tax increase was approved on March 3, 2026."),
    ("Republicans should fund the border program immediately.",
     "Democrats should fund the climate program immediately."),
]


def fingerprint(text):
    r = analyze_text(parse(text))
    return {
        "classes": [s["sentence_class"] for s in r["sentences"]],
        "claims": len(r["claims"]),
        "audit": sorted((f["type"], f["term"].lower()) for f in r["language_audit"]),
        "gaps": sorted(g["type"] for g in r["context_gaps"]),
        "emotional": r["rhetoric"]["emotional_term_count"],
        "integrity": r["neutral_summary"]["integrity"]["passed"],
    }


@pytest.mark.parametrize("left,right", PAIRS)
def test_equivalent_text_receives_equivalent_treatment(left, right):
    assert fingerprint(left) == fingerprint(right)


@pytest.mark.parametrize("left,right", PAIRS)
def test_summaries_introduce_no_endorsement(left, right):
    for t in (left, right):
        s = analyze_text(parse(t))["neutral_summary"]
        assert not s["integrity"]["endorsements_introduced"]
        lower = s["text"].lower()
        for banned in ("vote for", "the best candidate", "should support", "should oppose"):
            assert banned not in lower or banned in t.lower()


def test_scoring_ignores_identity():
    claims = [{"evidence": [{"relationship": "supports", "source_type": "primary_record"}], "actor": "Harbor"},
              {"evidence": [], "actor": "Harbor"}]
    swapped = [{**c, "actor": "Summit"} for c in claims]
    assert coverage(claims) == coverage(swapped)


def test_alignment_ignores_identity():
    links = [{"classification": "consistent", "is_procedural": False, "party": "Harbor"}] * 4
    assert alignment_index(links) == alignment_index([{**x, "party": "Summit"} for x in links])


def test_compare_profiles_are_structurally_identical(client):
    body = client.get("/api/candidates/compare", params={"a": "candidate-a", "b": "candidate-b"}).json()
    a, b = body["candidates"]
    assert list(a.keys()) == list(b.keys())
    for key in ("statements", "voting_record", "speech_vs_vote"):
        assert len(a[key]) <= body["limits"][{"statements": "statements", "voting_record": "votes", "speech_vs_vote": "comparisons"}[key]]
    # Order of request does not change any candidate's profile.
    rev = client.get("/api/candidates/compare", params={"a": "candidate-b", "b": "candidate-a"}).json()
    assert rev["candidates"][0] == b and rev["candidates"][1] == a


def test_missing_data_treated_identically(client):
    body = client.get("/api/candidates/compare", params={"a": "candidate-a", "b": "candidate-c"}).json()
    c = body["candidates"][1]
    assert c["voting_record"] == [] and c["voting_record_note"]
    assert c["alignment"]["state"] == "insufficient_evidence" and c["alignment"]["value"] is None
