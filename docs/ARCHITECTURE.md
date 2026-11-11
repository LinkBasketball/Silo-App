# Architecture

```
Browser ──► React SPA (Vite)
              │  services/api.js  (VITE_API_BASE_URL, JSON error envelope)
              ▼
          FastAPI  /api/*
              ├─ api/        routers: news, candidates, finance, rhetoric, conflicts, system
              ├─ services/   scoring (coverage, alignment) · matching · serializers
              ├─ nlp/        engine (spaCy | rules) · analysis · lexicons
              ├─ core/       config · database · errors · security (SSRF) · ratelimit
              ├─ integrations/ base adapter (retry/backoff/provenance) · fec · congress
              ├─ seed/       fictional demo fixtures + idempotent loader
              └─ models/     SQLAlchemy 2 models, Alembic migrations
```

## Request flow: the flagship journey
1. `GET /api/news/{id}` returns the body plus claims with **character offsets** and an evidence status, so the UI highlights exact spans.
2. Selecting a claim calls `showClaim(sentenceIndex)` in `ContextWidgetContext`, which opens the widget on the Evidence tab and scrolls to that claim.
3. The widget loads `GET /api/context-widget/{id}`: coverage, evidence groups, gaps, topics, publisher lineage and sources.
4. **Inspect record** opens the source dialog with the full record text and the excerpt highlighted.

Pasted text uses `POST /api/news/analyze`, which returns the **same context payload shape**, so the same widget renders it. This is also the contract a future browser extension would reuse.

## Data model
`DataProvenance`, `Publisher`/`PublisherRelationship`, `NewsArticle`, `ExtractedClaim`, `EvidenceSource`, `ClaimEvidence`,
`Candidate`, `PublicStatement`, `LegislativeBill`, `RollCallVote`, `CandidateVote`, `StatementVoteLink`, `Committee`,
`FinancialTransaction` (unique `transaction_uid` for dedupe), `Conflict`, `ConflictEvent`, `ConflictMetric`, `PolicyArgument`, `AnalysisRun`.
Every civic record has `data_status` ∈ {live, cached, demo, unavailable}. Timestamps are UTC.

## NLP
`nlp/engine.py` normalizes spaCy (or the rules fallback) into a small `ParsedDoc` structure. `nlp/analysis.py` is pure and deterministic:
sentence classification with reasons, quote detection and attribution, topic distribution, rhetoric metrics, language audit,
context gaps, neutral summary and output verification. A custom spaCy component fixes sentence splits after labels like "Candidate A.".

## Endpoints
`/api/health`, `/api/news`, `/api/news/{id}`, `POST /api/news/analyze`, `/api/context-widget/{id}`, `/api/candidates`,
`/api/candidates/{id|slug}`, `/api/candidates/compare?a=&b=`, `/api/finance-ledger`, `/api/finance-ledger/{candidate_id}`,
`POST /api/rhetoric/analyze`, `/api/conflicts`, `/api/conflicts/{id|slug}`, `/api/methodology`, `/api/sources/status?probe=`,
`/api/live/fec/candidates?q=`, `/api/live/congress/bills`. OpenAPI: `/api/docs`.
