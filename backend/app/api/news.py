import hashlib
import math
import time
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app import models as M
from app.api.deps import get_db
from app.core.config import get_settings
from app.core.errors import SiloError
from app.core.ratelimit import rate_limit
from app.core.security import fetch_article_text
from app.nlp.analysis import analyze_text
from app.nlp.engine import parse
from app.schemas import AnalyzeRequest, AnalyzeResponse, ArticleDetail, ContextPayload, NewsList
from app.services import scoring
from app.services.matching import match_claim
from app.services.serializers import (
    article_analysis, article_claims, article_context, build_context, evidence_item,
)

router = APIRouter(tags=["News Intelligence"])


def _load(db: Session, article_id: int) -> M.NewsArticle:
    a = db.scalar(
        select(M.NewsArticle).where(M.NewsArticle.id == article_id).options(
            selectinload(M.NewsArticle.publisher).selectinload(M.Publisher.relationships),
            selectinload(M.NewsArticle.claims).selectinload(M.ExtractedClaim.evidence).selectinload(M.ClaimEvidence.source),
        ))
    if a is None:
        raise SiloError(404, "not_found", f"Article {article_id} was not found.")
    return a


def _list_item(a: M.NewsArticle) -> dict:
    cov = scoring.coverage([{"evidence": [{"relationship": e.relationship_type, "source_type": e.source.source_type}
                                          for e in c.evidence]} for c in a.claims])
    return {
        "id": a.id, "slug": a.slug, "title": a.title, "dek": a.dek, "article_type": a.article_type, "author": a.author,
        "published_at": a.published_at, "primary_topic": a.primary_topic, "data_status": a.data_status,
        "publisher": {"id": a.publisher.id, "name": a.publisher.name, "ownership_type": a.publisher.ownership_type},
        "claim_count": len(a.claims), "coverage_state": cov["state"], "coverage_score": cov["score"],
    }


@router.get("/news", response_model=NewsList, summary="Browse stored articles")
def list_news(db: Session = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50),
              topic: str | None = None, q: str | None = Query(None, max_length=100)):
    stmt = select(M.NewsArticle)
    if topic:
        stmt = stmt.where(M.NewsArticle.primary_topic == topic)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(M.NewsArticle.title.ilike(like), M.NewsArticle.body.ilike(like)))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(M.NewsArticle.published_at.desc()).offset((page - 1) * page_size).limit(page_size).options(
        selectinload(M.NewsArticle.publisher),
        selectinload(M.NewsArticle.claims).selectinload(M.ExtractedClaim.evidence).selectinload(M.ClaimEvidence.source),
    )).all()
    return {"items": [_list_item(a) for a in rows], "page": page, "page_size": page_size, "total": total,
            "pages": max(1, math.ceil(total / page_size))}


@router.get("/news/{article_id}", response_model=ArticleDetail, summary="Article with extracted claims")
def get_news(article_id: int, db: Session = Depends(get_db)):
    a = _load(db, article_id)
    claims = article_claims(a)
    for c in claims:
        rels = {e["relationship"] for e in c["evidence"]}
        c["status"] = next((r for r in ("contradicts", "partially_supports", "supports", "provides_context") if r in rels),
                           "insufficient_evidence")
    return {**_list_item(a), "body": a.body, "source_url": a.source_url, "last_verified_at": a.last_verified_at, "claims": claims}


@router.get("/context-widget/{article_id}", response_model=ContextPayload, summary="Floating context widget payload")
def context_widget(article_id: int, db: Session = Depends(get_db)):
    return article_context(_load(db, article_id))


@router.post("/news/analyze", response_model=AnalyzeResponse, dependencies=[Depends(rate_limit)],
             summary="Analyze pasted text, a public URL, or a stored article")
def analyze(req: AnalyzeRequest, db: Session = Depends(get_db)):
    s = get_settings()
    t0 = time.perf_counter()
    if req.article_id is not None:
        a = _load(db, req.article_id)
        ctx = article_context(a)
        analysis = article_analysis(a)
        inp = {"kind": "article", "title": a.title, "url": a.source_url, "char_count": len(a.body)}
        text = a.body
    else:
        if req.url:
            fetched = fetch_article_text(req.url)
            text, title, url, kind = fetched["text"], req.title or fetched["title"], fetched["url"], "url"
        else:
            text, title, url, kind = req.text.strip(), req.title or "Submitted text", None, "text"
        if len(text) > s.max_text_chars:
            raise SiloError(413, "text_too_long", f"Text is limited to {s.max_text_chars:,} characters.")
        analysis = analyze_text(parse(text), voice=req.voice)
        sources = db.scalars(select(M.EvidenceSource)).all()
        now = datetime.now(UTC)
        claims = []
        for c in analysis["claims"]:
            items = [evidence_item(m["relationship"], m["source"], m["excerpt"], m["explanation"], m["assessment_method"], now)
                     for m in match_claim(c["text"], sources)]
            claims.append({**c, "id": None, "evidence": items})
        ctx = build_context(title=title, subtitle="Submitted for analysis" if kind == "text" else url,
                            data_status="user_submitted", claims=claims, analysis=analysis, publisher=None,
                            last_verified_at=now)
        inp = {"kind": kind, "title": title, "url": url, "char_count": len(text)}
    ms = int((time.perf_counter() - t0) * 1000)
    db.add(M.AnalysisRun(input_kind=inp["kind"], input_sha256=hashlib.sha256(text.encode()).hexdigest(),
                         engine=analysis["engine"], claim_count=len(analysis["claims"]),
                         coverage_score=ctx["coverage"]["score"], duration_ms=ms))
    db.commit()
    return {"input": inp, "context": ctx, "analysis": analysis, "analyzed_at": datetime.now(UTC), "duration_ms": ms}
