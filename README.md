# SILO — Civic intelligence, without the noise

**Less persuasion. More evidence.**

SILO is an open-source, nonpartisan civic-intelligence and news-context platform built for the
Presidential AI Challenge (Track II: Technical Implementation). A reader opens an article,
selects a claim, and SILO's floating context panel shows which statements connect to inspectable
records, which records conflict, what context is missing, how the text is written, and who owns
the publisher — with the reasoning behind every label.

SILO never tells anyone what to believe. It makes evidence easier to find, compare and verify.

> **Demonstration mode.** The bundled data (State X, Candidates A/B/C, publishers, bills, filings,
> the Corvan Strait and Highland Basin disputes) is **fictional** and labelled as such everywhere it
> appears. Identifiers use a `DEMO-` prefix and records carry no external URLs. Text you paste is
> analyzed for real.

## Features

| Module | What works |
|---|---|
| **News Intelligence** | Article browsing/search, claim highlighting, text and URL analysis, floating context widget (coverage score, evidence, context gaps, narrative-focus chart, publisher lineage, sources), source dialog |
| **Candidate Comparison** | Symmetric side-by-side profiles, speech-vs-vote comparisons with written rationales, alignment index with a minimum sample size, shared-vote table |
| **Financial Transparency** | Receipts by period and source, outside spending kept separate from contributions, documented money flows, paginated ledger, rhetoric scanner |
| **Geopolitical Context** | Timeline with documented vs. contested labels and an "as of" year slider, humanitarian/economic metrics with method and scope (never summed), parallel policy arguments labelled empirical vs. value judgement |
| **Methodology & Sources** | Scoring formulas, weights, lexicons, limitations and live data-source status, all served by the API |
| **Nonpartisan language engine** | Original text preserved; language audit (loaded terms, unsupported certainty, vague attribution, unattributed allegations); deterministic neutral restatement with quote-integrity and no-endorsement guardrails |

## Architecture

```
frontend/  React 18 · Vite · Tailwind · Recharts · Framer Motion · React Router
backend/   FastAPI · Pydantic v2 · SQLAlchemy 2 · Alembic · spaCy (rules fallback) · HTTPX
           SQLite for development/tests, PostgreSQL in production (tested on PostgreSQL 16)
```
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Quick start (native)

Prerequisites: Python 3.11+, Node 20+.

```bash
# Backend
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
uvicorn app.main:app --reload --port 8000     # migrates + seeds demo data on first start

# Frontend (second terminal)
cd frontend
npm install
npm run dev                                   # http://localhost:5173 (proxies /api to :8000)
```
API docs: http://localhost:8000/api/docs. Without the spaCy model, SILO falls back to a
dependency-free rules engine and reports that in the UI.

## Docker

```bash
docker compose up --build     # PostgreSQL + API + nginx frontend → http://localhost:8080
```

## Tests

```bash
cd backend && pytest -q --cov=app        # 93 tests
cd backend && ruff check app tests
cd frontend && npm test                  # 10 tests
cd frontend && npm run build
```
Latest measured results: [docs/TEST_RESULTS.md](docs/TEST_RESULTS.md).

## Configuration

All settings are `SILO_*` environment variables; see [.env.example](.env.example). Live
Congress.gov and OpenFEC adapters stay disabled until `SILO_LIVE_DATA_ENABLED=true` and an
[api.data.gov](https://api.data.gov/signup/) key are provided.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) · [Methodology](docs/METHODOLOGY.md) · [Data sources](docs/DATA_SOURCES.md)
- [Security](docs/SECURITY.md) · [Deployment](docs/DEPLOYMENT.md) · [Test results](docs/TEST_RESULTS.md)
- [Known limitations](docs/KNOWN_LIMITATIONS.md) · [Demo script](docs/DEMO_SCRIPT.md) · [Next steps](docs/NEXT_STEPS.md)

## License

GPL-3.0. See [LICENSE](LICENSE). Third-party: spaCy and `en_core_web_sm` (MIT), FastAPI (MIT),
SQLAlchemy (MIT), React (MIT), Recharts (MIT), Framer Motion (MIT), Lucide (ISC), Inter and
Source Serif 4 fonts (SIL OFL 1.1). All are GPL-compatible.
