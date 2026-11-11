import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app import models as M
from app.api.deps import get_db
from app.core.config import APP_VERSION, get_settings
from app.core.errors import SiloError
from app.integrations.base import AdapterError
from app.integrations.congress import CongressAdapter
from app.integrations.fec import FECAdapter
from app.nlp import lexicons as L
from app.nlp.analysis import SENTENCE_CLASSES
from app.nlp.engine import get_engine
from app.schemas import Health
from app.services import scoring

router = APIRouter(tags=["System & Methodology"])
_probe_cache: dict[str, tuple[float, dict]] = {}


def adapters():
    s = get_settings()
    return [FECAdapter(s.fec_api_key, s.fec_api_base), CongressAdapter(s.congress_api_key, s.congress_api_base)]


@router.get("/health", response_model=Health)
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        dbs = "ok"
    except Exception:
        dbs = "unavailable"
    demo = (db.scalar(select(func.count()).select_from(M.NewsArticle).where(M.NewsArticle.data_status == "demo")) or 0) > 0 if dbs == "ok" else False
    s = get_settings()
    return {"status": "ok" if dbs == "ok" else "degraded", "version": APP_VERSION, "database": dbs,
            "nlp_engine": get_engine().name, "demo_mode": demo, "live_data_enabled": s.live_data_enabled}


@router.get("/methodology")
def methodology():
    return {
        "principles": [
            "Evidence before interpretation; primary sources before commentary.",
            "Every score is deterministic, versioned and explained. No score is a probability of truth.",
            "Missing evidence is reported as missing — never as proof of falsehood.",
            "Original quotations are preserved verbatim; summaries are labelled as summaries.",
            "The same rules, lexicons and limits apply to every political actor.",
            "Demonstration data is labelled everywhere it appears.",
        ],
        "data_statuses": {
            "live": "Fetched from an official source during this request.",
            "cached": "A real record fetched earlier and stored by SILO.",
            "demo": "Fictional, illustrative record used to demonstrate features. Not a real government record.",
            "unavailable": "SILO could not obtain this information.",
            "user_submitted": "Text you provided; SILO has not verified its origin.",
        },
        "coverage_score": {
            "version": scoring.SCORING_VERSION,
            "question": "How much of this text's checkable content is connected to inspectable records?",
            "formula": "score = round(100 × Σ best(relationship_weight × source_quality) ÷ number_of_checkable_claims)",
            "relationship_weights": scoring.RELATIONSHIP_WEIGHT,
            "source_quality": scoring.SOURCE_QUALITY,
            "minimum_claims": scoring.MIN_CLAIMS,
            "insufficient_when": f"fewer than {scoring.MIN_CLAIMS} checkable claims, or no claim has an assessed (supporting, partially supporting or contradicting) record",
            "bands": {"70–100": "Broad coverage", "40–69": "Partial coverage", "0–39": "Limited coverage"},
            "notes": [
                "Contradicting records count toward coverage: coverage measures how checkable a text is, not whether it is right.",
                "Automatic matches for pasted text are labelled 'provides context' and are never assessed as supporting or contradicting without review.",
            ],
        },
        "alignment_index": {
            "formula": "(consistent + 0.5 × mixed) ÷ comparable pairs × 100",
            "minimum_comparable_pairs": 4,
            "excluded": ["procedural votes", "not directly comparable pairs", "insufficient evidence pairs"],
            "caution": "Describes how documented statements relate to documented votes. It does not measure honesty.",
        },
        "sentence_classes": {k: v for k, v in SENTENCE_CLASSES.items() if k != "ambiguous"},
        "rhetoric": {
            "adjective_noun_ratio": "Adjective tokens ÷ (noun + proper-noun tokens), using the active part-of-speech tagger.",
            "emotional_density": "Tokens matching the emotional-language lexicon ÷ alphabetic tokens.",
            "caution": "Emotional language is not evidence of falsehood, and neutral-sounding language is not evidence of truth.",
        },
        "lexicon": {
            "version": L.LEXICON_VERSION,
            "emotional_terms": {k: sorted(v) for k, v in L.EMOTIONAL_TERMS.items()},
            "certainty_markers": L.CERTAINTY_MARKERS, "vague_attribution": L.VAGUE_ATTRIBUTION,
            "topics": {k: sorted(v) for k, v in L.TOPIC_KEYWORDS.items()},
        },
        "nlp_engine": get_engine().name,
        "limitations": [
            "Rule-based classification misreads sarcasm, complex quotation structures and unusual phrasing.",
            "The emotional-language lexicon is small and English-only; it has not been validated against a labelled corpus.",
            "Statement–vote classifications in demonstration mode are curated examples, not automated judgements.",
            "Topic keywords can mis-assign sentences that mention several subjects.",
            "Automated tests check that the rules are symmetric. They cannot prove the system as a whole is neutral.",
        ],
    }


@router.get("/sources/status")
def sources_status(probe: bool = Query(False, description="Make a lightweight live request to each configured adapter.")):
    s = get_settings()
    out = [{"name": "SILO demonstration fixtures", "kind": "fixture", "status": "available", "configured": True, "enabled": True,
            "data_status": "demo", "docs_url": None, "note": "Fictional records used for the offline demonstration."}]
    for a in adapters():
        status = "disabled" if not s.live_data_enabled else "not_configured" if not a.api_key else "configured"
        entry = {"name": a.name, "kind": "live_adapter", "configured": bool(a.api_key), "enabled": s.live_data_enabled,
                 "status": status, "data_status": "live" if status == "configured" else "unavailable", "docs_url": a.docs_url,
                 "note": "Set SILO_LIVE_DATA_ENABLED=true and an api.data.gov key to enable." if status != "configured" else None}
        if probe and status == "configured":
            cached = _probe_cache.get(a.name)
            if cached and time.time() - cached[0] < 300:
                entry.update(cached[1])
            else:
                try:
                    (a.search_candidates("smith", per_page=1) if isinstance(a, FECAdapter) else a.recent_bills(limit=1))
                    res = {"status": "reachable", "last_success_at": a.status.last_success_at}
                except AdapterError as e:
                    res = {"status": "unreachable", "last_error": e.code}
                _probe_cache[a.name] = (time.time(), res)
                entry.update(res)
        out.append(entry)
    return {"sources": out, "live_data_enabled": s.live_data_enabled}


def _live(call):
    try:
        return call()
    except AdapterError as e:
        status = 503 if e.code in ("live_disabled", "not_configured", "upstream_unavailable") else 502
        raise SiloError(status, e.code, e.message) from None


@router.get("/live/fec/candidates", summary="Live OpenFEC candidate search (requires configuration)")
def live_fec_candidates(q: str = Query(..., min_length=2, max_length=80), page: int = Query(1, ge=1)):
    a = adapters()[0]
    return _live(lambda: a.search_candidates(q, page=page))


@router.get("/live/congress/bills", summary="Live Congress.gov recent bills (requires configuration)")
def live_congress_bills(congress: int | None = Query(None, ge=1, le=200), limit: int = Query(10, ge=1, le=50)):
    a = adapters()[1]
    return _live(lambda: a.recent_bills(congress, limit))
