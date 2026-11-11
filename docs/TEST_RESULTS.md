# Test results (measured 2026-11-11, Linux, 4 vCPU Xeon @ 2.3 GHz, Python 3.13, Node 22)

| Check | Command | Result |
|---|---|---|
| Backend tests, SQLite | `pytest -q --cov=app` | **93 passed**, 96% line coverage |
| Backend tests, PostgreSQL 16 | `SILO_DATABASE_URL=postgresql+psycopg://… pytest -q` | **93 passed** (migration + seed + all endpoints) |
| Lint | `ruff check app tests` | clean |
| Frontend tests | `npm test` | **10 passed** |
| Production build | `npm run build` | success |
| Browser smoke (Playwright, Chromium) | desktop 1440×900 + iPhone 13 | all pages render, 0 console errors, no horizontal overflow on mobile; claim click opens widget on that claim; Escape closes |

Coverage includes NLP (98%), scoring (100%), matching (100%), security (89%), adapters (47–89%).

## Latency (local uvicorn, single worker, SQLite, 60 requests each)
| Endpoint | p50 | p95 |
|---|---|---|
| GET /api/news | 3.9 ms | 6.2 ms |
| GET /api/context-widget/1 | 3.6 ms | 5.1 ms |
| GET /api/candidates/compare | 8.5 ms | 9.7 ms |
| GET /api/finance-ledger | 4.7 ms | 5.9 ms |
| POST /api/rhetoric/analyze (~4 KB text) | 93 ms | 96 ms |

Not verified: Docker image builds / Compose startup (no Docker daemon), live Congress.gov/OpenFEC calls (hosts blocked), public deployment.
