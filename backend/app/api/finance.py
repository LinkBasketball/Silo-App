from collections import defaultdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models as M
from app.api.deps import get_db
from app.core.errors import SiloError

router = APIRouter(tags=["Financial Transparency"])

TYPE_LABELS = {
    "direct_contribution": "Direct contribution",
    "committee_transfer": "Committee transfer",
    "independent_expenditure": "Independent expenditure",
    "operating_disbursement": "Operating disbursement",
}
CATEGORY_LABELS = {
    "individual_itemized": "Individuals (itemized)", "individual_unitemized": "Individuals (unitemized, under $200)",
    "pac": "PACs", "party": "Party committees", "candidate_self": "Candidate's own funds", "vendor": "Vendor", "committee": "Committee",
}
COMMITTEE_TYPES = {"principal_campaign": "Principal campaign committee", "pac": "Political action committee (PAC)",
                   "ie_only": "Independent-expenditure-only committee", "party": "Party committee"}


def _tx_out(t: M.FinancialTransaction) -> dict:
    return {
        "transaction_uid": t.transaction_uid, "committee": {"code": t.committee.committee_code, "name": t.committee.name,
                                                             "type": COMMITTEE_TYPES[t.committee.committee_type]},
        "transaction_type": t.transaction_type, "transaction_type_label": TYPE_LABELS[t.transaction_type],
        "counterparty": t.counterparty, "counterparty_category": CATEGORY_LABELS.get(t.counterparty_category, t.counterparty_category),
        "amount_cents": t.amount_cents, "transaction_date": t.transaction_date, "reporting_period": t.reporting_period,
        "support_oppose": t.support_oppose, "target_candidate": t.target_candidate.name if t.target_candidate else None,
        "filing_id": t.filing_id, "filed_date": t.filed_date, "memo": t.memo, "data_status": t.data_status,
    }


def _ledger(db: Session, candidate_id: int | None, period: str | None, page: int, page_size: int) -> dict:
    cands = db.scalars(select(M.Candidate).order_by(M.Candidate.name)).all()
    if candidate_id is not None and candidate_id not in {c.id for c in cands}:
        raise SiloError(404, "not_found", f"Candidate {candidate_id} was not found.")
    comms = db.scalars(select(M.Committee).order_by(M.Committee.committee_code)).all()
    txs = db.scalars(select(M.FinancialTransaction).options(
        selectinload(M.FinancialTransaction.committee), selectinload(M.FinancialTransaction.target_candidate))
        .order_by(M.FinancialTransaction.transaction_date, M.FinancialTransaction.transaction_uid)).all()
    periods = sorted({t.reporting_period for t in txs})
    if period and period not in periods:
        raise SiloError(400, "invalid_period", f"Unknown reporting period. Available: {', '.join(periods)}")
    if period:
        txs = [t for t in txs if t.reporting_period == period]
    cand_of_comm = {cm.id: cm.candidate_id for cm in comms}

    summaries = []
    for c in cands:
        mine = [t for t in txs if cand_of_comm.get(t.committee_id) == c.id and t.transaction_type in ("direct_contribution", "committee_transfer")]
        by_cat = defaultdict(int)
        for t in mine:
            by_cat[t.counterparty_category] += t.amount_cents
        outside = [t for t in txs if t.transaction_type == "independent_expenditure" and t.target_candidate_id == c.id]
        by_period = []
        for p in ([period] if period else periods):
            by_period.append({
                "period": p,
                "direct_cents": sum(t.amount_cents for t in mine if t.reporting_period == p),
                "outside_support_cents": sum(t.amount_cents for t in outside if t.reporting_period == p and t.support_oppose == "support"),
                "outside_oppose_cents": sum(t.amount_cents for t in outside if t.reporting_period == p and t.support_oppose == "oppose"),
            })
        summaries.append({
            "candidate": {"id": c.id, "name": c.name, "party": c.party},
            "direct_receipts_cents": sum(t.amount_cents for t in mine),
            "receipts_by_category": [{"category": k, "label": CATEGORY_LABELS[k], "amount_cents": v} for k, v in sorted(by_cat.items(), key=lambda kv: -kv[1])],
            "outside_support_cents": sum(t.amount_cents for t in outside if t.support_oppose == "support"),
            "outside_oppose_cents": sum(t.amount_cents for t in outside if t.support_oppose == "oppose"),
            "by_period": by_period,
        })
    if candidate_id is not None:
        summaries = [s for s in summaries if s["candidate"]["id"] == candidate_id]
        own = {cm.id for cm in comms if cm.candidate_id == candidate_id}
        txs = [t for t in txs if t.committee_id in own or t.target_candidate_id == candidate_id]

    # Relationship edges: documented money flows only, labelled by type and aggregated.
    name_to_comm = {cm.name for cm in comms}
    edges: dict[tuple, dict] = {}
    for t in txs:
        if t.transaction_type == "independent_expenditure":
            src, dst, label = t.committee.name, t.target_candidate.name, f"Independent expenditure ({t.support_oppose}s)"
        elif t.counterparty in name_to_comm:
            src, dst, label = t.counterparty, t.committee.name, TYPE_LABELS[t.transaction_type]
        else:
            continue
        key = (src, dst, t.transaction_type, t.support_oppose)
        e = edges.setdefault(key, {"source": src, "target": dst, "type": t.transaction_type, "label": label,
                                   "support_oppose": t.support_oppose, "amount_cents": 0})
        e["amount_cents"] += t.amount_cents

    total = len(txs)
    start = (page - 1) * page_size
    return {
        "data_status": "demo",
        "periods": periods,
        "selected_period": period,
        "summaries": summaries,
        "committees": [{"id": cm.id, "code": cm.committee_code, "name": cm.name, "type": cm.committee_type,
                        "type_label": COMMITTEE_TYPES[cm.committee_type],
                        "candidate": next((c.name for c in cands if c.id == cm.candidate_id), None),
                        "data_status": cm.data_status} for cm in comms],
        "relationships": list(edges.values()),
        "transactions": [_tx_out(t) for t in txs[start: start + page_size]],
        "page": page, "page_size": page_size, "total": total,
        "freshness": {"as_of": "2026-10-15", "note": "Demonstration filings through the 2026-Q3 reporting period."},
        "definitions": {
            "direct_contribution": "Money given to a candidate's own committee. Subject to contribution limits and disclosure.",
            "committee_transfer": "Money moved from another committee (for example a party committee) to the candidate's committee.",
            "independent_expenditure": "Spending by an outside group to support or oppose a candidate, made without coordinating with the campaign. It is not a contribution to the candidate and the candidate does not control it.",
            "caution": "A contribution or expenditure shows a documented financial relationship. It does not by itself show that money influenced any decision.",
        },
    }


@router.get("/finance-ledger", summary="Campaign-finance ledger with summaries and relationships")
def finance_ledger(db: Session = Depends(get_db), candidate_id: int | None = None,
                   period: str | None = Query(None, max_length=20), page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    return _ledger(db, candidate_id, period, page, page_size)


@router.get("/finance-ledger/{candidate_id}", summary="Ledger filtered to one candidate")
def finance_ledger_candidate(candidate_id: int, db: Session = Depends(get_db), period: str | None = Query(None, max_length=20),
                             page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    return _ledger(db, candidate_id, period, page, page_size)
