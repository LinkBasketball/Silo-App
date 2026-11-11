"""Evidence Coverage Score — deterministic, documented, unit-tested.

The score answers ONE question: "How much of this text's checkable content is connected
to inspectable records?" It is NOT a probability that the text is true. Contradicting
records raise coverage just as supporting ones do, and are reported separately.
"""
from __future__ import annotations

SCORING_VERSION = "coverage-v1"

RELATIONSHIPS = {
    "supports": "Supports",
    "partially_supports": "Partially supports",
    "contradicts": "Contradicts",
    "provides_context": "Provides context",
    "insufficient_evidence": "Insufficient evidence",
}
RELATIONSHIP_WEIGHT = {
    "supports": 1.0, "partially_supports": 1.0, "contradicts": 1.0,
    "provides_context": 0.5, "insufficient_evidence": 0.0,
}
SOURCE_QUALITY = {
    "primary_record": 1.0,        # bill text, roll call, filing, court record
    "official_statistic": 1.0,    # published by a statistical agency
    "official_transcript": 0.9,   # transcript or recording of the statement
    "secondary_reporting": 0.6,   # another publication's account
    "unverified": 0.3,
}
SOURCE_TYPE_LABELS = {
    "primary_record": "Original record",
    "official_statistic": "Official statistic",
    "official_transcript": "Direct quotation record",
    "secondary_reporting": "Secondary reporting",
    "unverified": "Unverified",
}
MIN_CLAIMS = 2
ASSESSED = {"supports", "partially_supports", "contradicts"}


def claim_weight(evidence: list[dict]) -> float:
    """Best (relationship × source-quality) across a claim's evidence; 0 if none."""
    best = 0.0
    for e in evidence:
        w = RELATIONSHIP_WEIGHT.get(e["relationship"], 0.0) * SOURCE_QUALITY.get(e.get("source_type"), 0.3)
        best = max(best, w)
    return best


def coverage(claims: list[dict]) -> dict:
    """claims: [{"evidence": [{"relationship", "source_type"}, ...]}, ...]"""
    n = len(claims)
    rels = [{e["relationship"] for e in c.get("evidence", [])} for c in claims]
    supported = sum(1 for r in rels if r & {"supports", "partially_supports"} and "contradicts" not in r)
    conflicting = sum(1 for r in rels if "contradicts" in r)
    context_only = sum(1 for r in rels if r and not (r & ASSESSED) and "provides_context" in r)
    lacking = n - supported - conflicting - context_only
    assessed_claims = sum(1 for r in rels if r & ASSESSED)

    counts = {
        "claims_total": n, "claims_supported": supported, "claims_conflicting": conflicting,
        "claims_context_only": context_only, "claims_lacking_evidence": lacking,
    }
    if n < MIN_CLAIMS or assessed_claims == 0:
        reason = (f"Fewer than {MIN_CLAIMS} checkable claims were found." if n < MIN_CLAIMS
                  else "No claim could be matched to a record that was assessed as supporting, partially supporting, or contradicting it.")
        return {"state": "insufficient_evidence", "score": None, "band": None, "reason": reason,
                "version": SCORING_VERSION, **counts}
    score = round(100 * sum(claim_weight(c.get("evidence", [])) for c in claims) / n)
    band = "Broad coverage" if score >= 70 else "Partial coverage" if score >= 40 else "Limited coverage"
    return {"state": "scored", "score": score, "band": band, "reason": None, "version": SCORING_VERSION, **counts}


def alignment_index(links: list[dict], minimum: int = 4) -> dict:
    """Statement-vs-vote consistency index, computed only with enough comparable observations.

    links: [{"classification", "is_procedural"}]. Procedural votes and 'not directly comparable'
    or 'insufficient evidence' pairs are excluded from the denominator.
    """
    comparable = [l for l in links if not l.get("is_procedural") and l["classification"] in
                  ("consistent", "potentially_inconsistent", "mixed")]
    excluded = len(links) - len(comparable)
    n = len(comparable)
    if n < minimum:
        return {"state": "insufficient_evidence", "value": None, "comparable": n, "excluded": excluded,
                "minimum": minimum, "reason": f"At least {minimum} directly comparable statement–vote pairs are required; {n} available."}
    c = sum(1 for l in comparable if l["classification"] == "consistent")
    m = sum(1 for l in comparable if l["classification"] == "mixed")
    return {"state": "scored", "value": round(100 * (c + 0.5 * m) / n), "comparable": n, "excluded": excluded,
            "minimum": minimum, "reason": None}
