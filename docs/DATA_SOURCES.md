# Data sources

| Source | Status in this build | Auth | Notes |
|---|---|---|---|
| SILO demo fixtures (`backend/app/seed/demo_data.py`) | Active | none | Fictional; `DEMO-` IDs; no URLs |
| OpenFEC `api.open.fec.gov/v1` | Adapter implemented, mocked in tests; **not live-verified** | api.data.gov key | `/candidates/search/` normalized with provenance |
| Congress.gov `api.congress.gov/v3` | Adapter implemented, mocked in tests; **not live-verified** | api.data.gov key | `/bill` recent bills |
| User-supplied article URLs | Implemented | none | SSRF-protected, robots.txt respected, no paywall bypass |

The build environment blocked outbound access to both APIs, so live calls were never made. Enable with
`SILO_LIVE_DATA_ENABLED=true`, `SILO_FEC_API_KEY`, `SILO_CONGRESS_API_KEY`, then use *Check live connections* on the
Methodology page or `GET /api/sources/status?probe=true`.

Not yet implemented: Google Civic Information, Vote Smart, UN records, IRS Form 990 (e.g., ProPublica Nonprofit Explorer),
roll-call XML feeds. Each should be a new `BaseAdapter` subclass with fixtures and mocked tests.

**Provenance rule:** every record carries `data_status`, and adapters return a `provenance` block (source, URL, status, retrieved_at).
