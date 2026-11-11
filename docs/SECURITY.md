# Security

- **Input validation:** Pydantic schemas; text limited to 20,000 characters; exactly one of text/url/article_id.
- **SSRF protection** (`core/security.py`): http/https only; ports 80/443; no embedded credentials; blocks localhost,
  `.local`/`.internal`, metadata hosts, and any hostname resolving to private, loopback, link-local, reserved, multicast or
  IPv4-mapped private addresses. Every redirect hop is re-validated (max 3). 8 s timeout, 1.5 MB streaming size limit,
  HTML/plain text only, robots.txt honoured, 401/402/403 reported as access-restricted (no bypass).
  *Residual risk:* DNS rebinding between validation and connection. Mitigate with an egress proxy in production.
- **Rate limiting:** in-process sliding window (30/min/IP) on POST analysis endpoints. Use a shared limiter at the proxy for multi-worker deploys.
- **CORS:** explicit allowlist (`SILO_CORS_ORIGINS`), GET/POST only, no credentials.
- **Errors:** uniform `{"error": {code, message, details}}`; unhandled exceptions are logged server-side and return a generic message.
- **Secrets:** environment variables only; `.env` is git-ignored; the frontend bundle contains no secrets.
- **Privacy / retention:** submitted text is never stored. `analysis_runs` keeps a SHA-256 hash, engine, counts and duration only (tested).
- **No costly inference:** the core pipeline is local and deterministic; there are no paid AI API calls.
- **Containers:** backend runs as a non-root user; nginx adds nosniff/referrer/frame headers.
