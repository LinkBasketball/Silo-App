"""Database integrity, migrations, fixtures and adapters."""
import httpx
import pytest
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.exc import IntegrityError

from app import models as M
from app.seed import demo_data as D


def test_migration_creates_all_tables(tmp_path):
    from app.main import run_migrations
    url = f"sqlite:///{tmp_path}/m.db"
    run_migrations(url)
    tables = set(inspect(create_engine(url)).get_table_names())
    from app.core.database import Base
    assert set(Base.metadata.tables) <= tables


def test_seed_is_idempotent(db):
    from app.seed.loader import seed_demo
    before = db.scalar(select(func.count()).select_from(M.NewsArticle))
    assert seed_demo(db) is False
    assert db.scalar(select(func.count()).select_from(M.NewsArticle)) == before


def test_every_annotation_attached(db):
    expected = sum(len(a["annotations"]) for a in D.ARTICLES)
    assert db.scalar(select(func.count()).select_from(M.ClaimEvidence)) == expected


def test_duplicate_transactions_rejected(db):
    t = db.scalars(select(M.FinancialTransaction)).first()
    db.add(M.FinancialTransaction(transaction_uid=t.transaction_uid, committee_id=t.committee_id, transaction_type=t.transaction_type,
                                  counterparty="dup", counterparty_category="pac", amount_cents=1, transaction_date=t.transaction_date,
                                  reporting_period=t.reporting_period, filing_id="x", filed_date=t.filed_date))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_independent_expenditures_not_counted_as_contributions(client):
    body = client.get("/api/finance-ledger").json()
    a = next(s for s in body["summaries"] if s["candidate"]["name"] == "Candidate A")
    direct_expected = sum(sum(v.values()) for r, *_rest, v in [(x[0], x[1], x[2], x[3]) for x in D.RECEIPTS] if r == "DEMO-C-A01") * 100
    direct_expected += sum(sum(v.values()) for r, _cp, v in D.TRANSFERS if r == "DEMO-C-A01") * 100
    assert a["direct_receipts_cents"] == direct_expected
    ie_support = sum(sum(v.values()) for _s, tgt, so, _v, v in D.IES if tgt == "candidate-a" and so == "support") * 100
    assert a["outside_support_cents"] == ie_support
    for t in body["transactions"]:
        if t["transaction_type"] == "independent_expenditure":
            assert t["support_oppose"] in ("support", "oppose") and "Not a contribution" in t["memo"]


def test_demo_records_use_demo_identifiers_and_no_urls(db):
    for src in db.scalars(select(M.EvidenceSource)):
        assert src.data_status == "demo" and src.url is None and src.record_key.startswith("DEMO-")
    for rc in db.scalars(select(M.RollCallVote)):
        assert rc.roll_call_id.startswith("DEMO-")
    for cm in db.scalars(select(M.Committee)):
        assert cm.committee_code.startswith("DEMO-")


def test_fec_adapter_normalizes_and_retries(monkeypatch):
    from app.core.config import get_settings
    from app.integrations.fec import FECAdapter
    monkeypatch.setattr(get_settings(), "live_data_enabled", True)
    calls = {"n": 0}

    def handler(req):
        calls["n"] += 1
        assert req.url.params["api_key"] == "k"
        if calls["n"] == 1:
            return httpx.Response(503)
        return httpx.Response(200, json={"results": [{"candidate_id": "P00000001", "name": "EXAMPLE, PAT", "party_full": "X", "office_full": "President"}],
                                         "pagination": {"page": 1, "pages": 1, "count": 1}})
    a = FECAdapter("k", transport=httpx.MockTransport(handler), sleep=lambda s: None)
    out = a.search_candidates("example")
    assert calls["n"] == 2 and out["items"][0]["candidate_id"] == "P00000001"
    assert out["provenance"]["data_status"] == "live"


def test_adapter_gives_up_and_reports(monkeypatch):
    from app.core.config import get_settings
    from app.integrations.base import AdapterError
    from app.integrations.congress import CongressAdapter
    monkeypatch.setattr(get_settings(), "live_data_enabled", True)
    a = CongressAdapter("k", transport=httpx.MockTransport(lambda r: httpx.Response(500)), sleep=lambda s: None)
    with pytest.raises(AdapterError) as e:
        a.recent_bills()
    assert e.value.code == "upstream_unavailable" and a.status.last_error


def test_adapter_rejects_bad_key(monkeypatch):
    from app.core.config import get_settings
    from app.integrations.base import AdapterError
    from app.integrations.congress import CongressAdapter
    monkeypatch.setattr(get_settings(), "live_data_enabled", True)
    a = CongressAdapter("bad", transport=httpx.MockTransport(lambda r: httpx.Response(403)), sleep=lambda s: None)
    with pytest.raises(AdapterError) as e:
        a.recent_bills()
    assert e.value.code == "unauthorized"


def test_adapter_requires_configuration():
    from app.integrations.base import AdapterError
    from app.integrations.fec import FECAdapter
    with pytest.raises(AdapterError) as e:
        FECAdapter(None).search_candidates("x")
    assert e.value.code in ("live_disabled", "not_configured")


def test_postgres_url_normalized():
    from app.core.config import Settings
    assert Settings(database_url="postgres://u:p@h/db").database_url == "postgresql+psycopg://u:p@h/db"
    assert Settings(database_url="sqlite:///x.db").database_url == "sqlite:///x.db"
