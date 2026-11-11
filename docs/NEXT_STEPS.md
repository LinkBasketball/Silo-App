# Highest-impact next steps

1. **Real, citable records.** Add a small cached set of genuine public-domain records (e.g., one real roll call and one real FEC committee summary) fetched with keys, stored as `cached` with provenance, so the UI shows all three data states.
2. **Ingestion jobs** that persist live OpenFEC/Congress.gov responses (dedupe on `transaction_uid` / roll-call IDs) instead of the read-through endpoints.
3. **Evidence Explorer graph**: Claim → Record → Excerpt → Conclusion as an interactive diagram in the widget.
4. **Reviewer workflow** for curated annotations (who assessed, when, revision history), surfaced in the evidence cards.
5. **Optional NLI adapter** (behind a flag) to *suggest* support or contradiction for human review, never auto-publish it.
6. **Civic Learning mode**: inline glossary tooltips (roll-call vote, PAC, independent expenditure, bill vs. law).
7. **Shareable evidence briefs**: a printable, source-linked one-page summary of a claim.
8. Automated accessibility (axe + Playwright) in CI, plus Docker build verification in CI.
9. Browser extension reusing `POST /api/news/analyze` and the widget component.
