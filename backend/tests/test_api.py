"""Endpoint contracts, pagination, validation and error envelopes."""


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["database"] == "ok" and body["demo_mode"] is True
    assert body["nlp_engine"]


def test_news_list_and_pagination(client):
    r = client.get("/api/news", params={"page_size": 2})
    body = r.json()
    assert r.status_code == 200 and body["total"] == 5 and body["pages"] == 3 and len(body["items"]) == 2
    item = body["items"][0]
    assert item["data_status"] == "demo" and item["publisher"]["name"]
    page3 = client.get("/api/news", params={"page_size": 2, "page": 3}).json()
    assert len(page3["items"]) == 1


def test_news_filters(client):
    assert client.get("/api/news", params={"topic": "Healthcare"}).json()["total"] == 1
    assert client.get("/api/news", params={"q": "Corvan"}).json()["total"] == 1


def test_article_detail_has_claim_offsets(client):
    a = client.get("/api/news/1").json()
    assert a["claims"]
    for c in a["claims"]:
        assert a["body"][c["start"]:c["end"]] == c["text"]
        assert c["status"] in {"supports", "partially_supports", "contradicts", "provides_context", "insufficient_evidence"}


def test_not_found_envelope(client):
    r = client.get("/api/news/9999")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_validation_envelope(client):
    r = client.post("/api/news/analyze", json={})
    assert r.status_code == 422 and r.json()["error"]["code"] == "validation_error"
    r = client.post("/api/news/analyze", json={"text": "x" * 30, "url": "https://example.com"})
    assert r.status_code == 422


def test_context_widget_contract(client):
    w = client.get("/api/context-widget/1").json()
    for key in ("coverage", "evidence", "gaps", "topics", "publisher", "sources", "last_verified_at", "methodology"):
        assert key in w
    assert w["data_status"] == "demo"
    item = w["evidence"][0]["items"][0]
    for key in ("relationship", "excerpt", "explanation", "retrieved_at", "source"):
        assert key in item
    src = item["source"]
    for key in ("title", "organization", "record_date", "source_type_label", "data_status"):
        assert key in src
    assert w["publisher"]["relationships"]


def test_context_widget_insufficient_for_opinion(client):
    items = client.get("/api/news").json()["items"]
    op = next(i for i in items if i["article_type"] == "opinion")
    w = client.get(f"/api/context-widget/{op['id']}").json()
    assert w["coverage"]["state"] == "insufficient_evidence" and w["coverage"]["score"] is None


def test_analyze_text(client):
    text = ("The State X Senate passed the River Restoration Act by a vote of 31 to 19. "
            "Critics said the disastrous bill was a reckless waste. Experts say it is clearly the best plan ever.")
    r = client.post("/api/news/analyze", json={"text": text})
    assert r.status_code == 200
    body = r.json()
    assert body["input"]["kind"] == "text"
    assert body["context"]["data_status"] == "user_submitted"
    assert body["analysis"]["claims"]
    # Automatic matches must never be assessed as support/contradiction.
    for g in body["context"]["evidence"]:
        for i in g["items"]:
            assert i["relationship"] == "provides_context"
            assert i["assessment_method"] == "automatic_related_record"


def test_analyze_does_not_store_text(client, db):
    from sqlalchemy import select

    from app.models import AnalysisRun
    secret = "Unique private sentence number 8472 was written by the user for testing purposes only."
    client.post("/api/news/analyze", json={"text": secret})
    run = db.scalars(select(AnalysisRun).order_by(AnalysisRun.id.desc())).first()
    assert run is not None and len(run.input_sha256) == 64
    assert not any(secret in str(getattr(run, c.name)) for c in AnalysisRun.__table__.columns)


def test_analyze_stored_article(client):
    r = client.post("/api/news/analyze", json={"article_id": 2})
    assert r.status_code == 200 and r.json()["input"]["kind"] == "article"


def test_analyze_text_too_long(client):
    r = client.post("/api/news/analyze", json={"text": "word " * 5000})
    assert r.status_code == 413


def test_rhetoric_endpoint(client):
    r = client.post("/api/rhetoric/analyze", json={"text": "The disastrous bill devastated the economy. Wages rose 3 percent in 2025."})
    assert r.status_code == 200
    body = r.json()
    assert body["rhetoric"]["adjective_noun_ratio"] is not None
    assert body["neutral_summary"]["integrity"]["passed"]


def test_candidates(client):
    items = client.get("/api/candidates").json()["items"]
    assert {c["name"] for c in items} == {"Candidate A", "Candidate B", "Candidate C"}
    assert all(c["data_status"] == "demo" for c in items)
    assert client.get("/api/candidates/candidate-a").json()["name"] == "Candidate A"


def test_compare_same_candidate_rejected(client):
    r = client.get("/api/candidates/compare", params={"a": "candidate-a", "b": "candidate-a"})
    assert r.status_code == 400 and r.json()["error"]["code"] == "same_candidate"


def test_finance_ledger(client):
    r = client.get("/api/finance-ledger")
    body = r.json()
    assert r.status_code == 200 and body["periods"] == ["2026-Q1", "2026-Q2", "2026-Q3"]
    assert body["transactions"] and body["relationships"]
    q2 = client.get("/api/finance-ledger", params={"period": "2026-Q2"}).json()
    assert all(t["reporting_period"] == "2026-Q2" for t in q2["transactions"])
    assert client.get("/api/finance-ledger", params={"period": "1999-Q1"}).status_code == 400
    one = client.get("/api/finance-ledger/1").json()
    assert len(one["summaries"]) == 1


def test_conflicts(client):
    items = client.get("/api/conflicts").json()["items"]
    assert len(items) == 2
    c = client.get("/api/conflicts/corvan-strait").json()
    dates = [e["event_date"] for e in c["events"]]
    assert dates == sorted(dates)
    assert any(e["evidence_category"] == "contested_interpretation" for e in c["events"])
    for ap in c["approaches"]:
        assert len(ap["for"]) == len(ap["against"])  # equal formatting / count
    assert client.get("/api/conflicts/nope").status_code == 404


def test_methodology_and_sources(client):
    m = client.get("/api/methodology").json()
    assert "formula" in m["coverage_score"] and m["limitations"]
    s = client.get("/api/sources/status").json()
    names = {x["name"] for x in s["sources"]}
    assert {"OpenFEC", "Congress.gov"} <= names
    assert all(x["status"] in {"available", "disabled", "not_configured", "configured"} for x in s["sources"])


def test_live_endpoints_unavailable_without_config(client):
    r = client.get("/api/live/fec/candidates", params={"q": "smith"})
    assert r.status_code == 503 and r.json()["error"]["code"] == "live_disabled"


def test_openapi_available(client):
    assert client.get("/api/openapi.json").status_code == 200


def test_rate_limit(client, monkeypatch):
    from app.core import ratelimit
    from app.core.config import get_settings
    monkeypatch.setattr(get_settings(), "rate_limit_per_minute", 2)
    ratelimit.reset()
    payload = {"text": "The senate passed the bill on Tuesday by 31 votes to 19."}
    codes = [client.post("/api/rhetoric/analyze", json=payload).status_code for _ in range(3)]
    ratelimit.reset()
    assert codes == [200, 200, 429]
