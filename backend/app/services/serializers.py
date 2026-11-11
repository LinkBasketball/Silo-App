"""Turn ORM rows into API payloads. Kept in one place so every module labels data the same way."""
from functools import lru_cache

from app import models as M
from app.nlp.analysis import analyze_text
from app.nlp.engine import parse
from app.services import scoring


def source_out(src: M.EvidenceSource) -> dict:
    return {
        "id": src.id, "record_key": src.record_key, "title": src.title, "organization": src.organization,
        "source_type": src.source_type, "source_type_label": scoring.SOURCE_TYPE_LABELS.get(src.source_type, src.source_type),
        "record_date": src.record_date, "url": src.url, "content": src.content, "data_status": src.data_status,
    }


def publisher_out(p: M.Publisher | None) -> dict | None:
    if p is None:
        return None
    return {
        "id": p.id, "slug": p.slug, "name": p.name, "legal_entity": p.legal_entity,
        "parent_organization": p.parent_organization, "ownership_type": p.ownership_type,
        "description": p.description, "data_status": p.data_status,
        "relationships": [{
            "id": r.id, "related_entity": r.related_entity, "relationship_type": r.relationship_type,
            "description": r.description, "amount_usd": r.amount_usd, "start_date": r.start_date,
            "end_date": r.end_date, "established": r.established, "source_label": r.source_label, "source_url": r.source_url,
        } for r in p.relationships],
        "note": "Ownership, funding and donations are listed for transparency. They do not by themselves establish editorial control or influence.",
    }


def evidence_groups(claims: list[dict]) -> list[dict]:
    return [{
        "claim_id": c.get("id"), "sentence_index": c["sentence_index"], "claim_text": c["text"],
        "claim_type": c["claim_type"], "sentence_class": c["sentence_class"], "topic": c["topic"],
        "start": c.get("start"), "end": c.get("end"),
        "items": c["evidence"],
        "status": _claim_status(c["evidence"]),
    } for c in claims]


def _claim_status(items: list[dict]) -> str:
    rels = {i["relationship"] for i in items}
    if "contradicts" in rels:
        return "contradicts"
    if "partially_supports" in rels:
        return "partially_supports"
    if "supports" in rels:
        return "supports"
    if "provides_context" in rels:
        return "provides_context"
    return "insufficient_evidence"


def evidence_item(rel: str, src: M.EvidenceSource, excerpt: str, explanation: str, method: str, retrieved_at) -> dict:
    return {
        "relationship": rel, "relationship_label": scoring.RELATIONSHIPS[rel], "source": source_out(src),
        "source_type": src.source_type, "excerpt": excerpt, "explanation": explanation,
        "assessment_method": method, "retrieved_at": retrieved_at,
    }


@lru_cache(maxsize=128)
def _article_analysis(article_id: int, updated: str, body: str, voice: str) -> dict:
    return analyze_text(parse(body), voice=voice)


def article_analysis(a: M.NewsArticle) -> dict:
    return _article_analysis(a.id, str(a.updated_at), a.body, a.article_type)


def article_claims(a: M.NewsArticle) -> list[dict]:
    return [{
        "id": c.id, "sentence_index": c.sentence_index, "text": c.text, "start": c.start_char, "end": c.end_char,
        "sentence_class": c.sentence_class, "claim_type": c.claim_type, "topic": c.topic,
        "evidence": [evidence_item(e.relationship_type, e.source, e.excerpt, e.explanation, e.assessment_method, e.retrieved_at)
                     for e in c.evidence],
    } for c in a.claims]


def build_context(*, title: str, subtitle: str | None, data_status: str, claims: list[dict], analysis: dict,
                  publisher: dict | None, last_verified_at, article_id: int | None = None) -> dict:
    groups = evidence_groups(claims)
    cov = scoring.coverage(claims)
    gaps = list(analysis["context_gaps"])
    for g in groups:
        if not g["items"]:
            gaps.append({"type": "no_record", "label": "No connected record",
                         "question": "SILO has no record connected to this claim. That does not make it false — it means it has not been checked here.",
                         "trigger": g["claim_text"][:60], "sentence_index": g["sentence_index"]})
    sentences = {s["index"]: s["text"] for s in analysis["sentences"]}
    for g in gaps:
        g["sentence"] = sentences.get(g["sentence_index"])
    gaps.sort(key=lambda g: (g["sentence_index"], g["type"]))
    srcs = {}
    for g in groups:
        for i in g["items"]:
            srcs[i["source"]["id"]] = i["source"]
    return {
        "article_id": article_id, "title": title, "subtitle": subtitle, "data_status": data_status,
        "last_verified_at": last_verified_at, "engine": analysis["engine"],
        "coverage": cov, "evidence": groups, "gaps": gaps, "topics": analysis["topics"],
        "publisher": publisher, "sources": list(srcs.values()),
        "methodology": {
            "coverage": "Coverage measures how much of the text's checkable content is connected to inspectable records. It is not a probability that the text is true.",
            "version": scoring.SCORING_VERSION,
        },
    }


def article_context(a: M.NewsArticle) -> dict:
    return build_context(
        title=a.title, subtitle=f"{a.publisher.name} · {a.published_at:%b %-d, %Y}", data_status=a.data_status,
        claims=article_claims(a), analysis=article_analysis(a), publisher=publisher_out(a.publisher),
        last_verified_at=a.last_verified_at, article_id=a.id,
    )
