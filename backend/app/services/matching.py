"""Find records related to free-text claims.

Automatic matches are labelled 'provides_context' — SILO does not decide on its own whether a
record supports or contradicts a claim. An entity gate prevents matching a claim to a record
about an unrelated place or person merely because they share common words.
"""
import re

from app.nlp.engine import _FUNCTION

_WORD = re.compile(r"[a-z][a-z'-]{3,}")
STOP = _FUNCTION | {"said", "says", "state", "year", "years", "would", "about", "after", "before", "percent"}


def content_terms(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in STOP}


def best_excerpt(record_text: str, terms: set[str]) -> str:
    sents = re.split(r"(?<=[.!?])\s+", record_text)
    return max(sents, key=lambda s: len(content_terms(s) & terms)) if sents else record_text[:300]


def match_claim(claim_text: str, sources: list) -> list[dict]:
    lower = claim_text.lower()
    terms = content_terms(claim_text)
    out = []
    for src in sources:
        if not any(e.lower() in lower for e in (src.entities or [])):
            continue
        overlap = terms & content_terms(src.title + " " + src.content)
        if len(overlap) < 3:
            continue
        out.append({
            "source": src, "relationship": "provides_context", "assessment_method": "automatic_related_record",
            "excerpt": best_excerpt(src.content, terms),
            "explanation": "SILO found a record that names the same entity and shares key terms "
                           f"({', '.join(sorted(overlap)[:6])}). Whether it supports or contradicts the claim "
                           "has not been assessed automatically — open the record to compare.",
            "overlap": len(overlap),
        })
    out.sort(key=lambda m: -m["overlap"])
    return out[:2]
