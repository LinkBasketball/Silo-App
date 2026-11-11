# Known limitations

- **Demo data is fictional.** There are no real civic records in this build. Real-world pasted text will usually show "Insufficient evidence": this is the honest result.
- **Live adapters unverified.** OpenFEC/Congress.gov are implemented and mock-tested only, and nothing ingests live data into the database yet.
- **Claim–evidence assessment** for new text is limited to "related record (not assessed)". There is no automated support/contradiction (NLI) model.
- **Rule-based NLP** misreads sarcasm, nested quotes and complex syntax. The lexicons are small, English-only and not validated against a labelled corpus.
- **Statement–vote links** are curated demo annotations; there is no review workflow or audit trail UI yet.
- **Rate limiter** is per-process; the URL fetcher has a DNS-rebinding window (see SECURITY.md).
- **Docker/Compose** files were written but not built here (no daemon). No public deployment was made.
- No dark mode, i18n, or automated accessibility audit (axe) yet. Keyboard and screen-reader basics are implemented but not formally audited.
- Competition rules were not verified against official documentation (no network access to the challenge site).
