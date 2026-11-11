from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app import models as M
from app.api.deps import get_db
from app.core.errors import SiloError
from app.schemas import CandidateList, CandidateSummary, CompareResponse
from app.services.scoring import alignment_index

router = APIRouter(tags=["Candidate Comparison"])

# Identical limits for every candidate: equal treatment is enforced in code, not by convention.
LIMITS = {"statements": 6, "votes": 8, "comparisons": 8}
ALIGNMENT = {
    "consistent": "Consistent",
    "potentially_inconsistent": "Potentially inconsistent",
    "mixed": "Mixed or conditional",
    "not_directly_comparable": "Not directly comparable",
    "insufficient_evidence": "Insufficient evidence",
}


def _get(db: Session, ref: str) -> M.Candidate:
    stmt = select(M.Candidate)
    stmt = stmt.where(M.Candidate.id == int(ref)) if ref.isdigit() else stmt.where(M.Candidate.slug == ref)
    c = db.scalar(stmt.options(selectinload(M.Candidate.statements)))
    if c is None:
        raise SiloError(404, "not_found", f"Candidate {ref!r} was not found.")
    return c


def _vote_out(v: M.CandidateVote) -> dict:
    rc = v.roll_call
    return {"roll_call_id": rc.roll_call_id, "vote_date": rc.vote_date, "question": rc.question, "is_procedural": rc.is_procedural,
            "result": rc.result, "tally": f"{rc.yeas}–{rc.nays}", "position": v.position,
            "bill": {"bill_number": rc.bill.bill_number, "title": rc.bill.title, "status": rc.bill.status, "topic": rc.bill.topic},
            "data_status": rc.data_status}


def profile(db: Session, c: M.Candidate) -> dict:
    votes = db.scalars(select(M.CandidateVote).where(M.CandidateVote.candidate_id == c.id).options(
        selectinload(M.CandidateVote.roll_call).selectinload(M.RollCallVote.bill))).all()
    votes = sorted(votes, key=lambda v: v.roll_call.vote_date, reverse=True)
    pos_by_rc = {v.roll_call_vote_id: v.position for v in votes}
    links = db.scalars(select(M.StatementVoteLink).join(M.PublicStatement).where(M.PublicStatement.candidate_id == c.id).options(
        selectinload(M.StatementVoteLink.statement),
        selectinload(M.StatementVoteLink.roll_call).selectinload(M.RollCallVote.bill))).all()
    links = sorted(links, key=lambda link: (link.statement.statement_date, link.id))
    comparisons = [{
        "quote": link.statement.quote, "quote_date": link.statement.statement_date, "venue": link.statement.venue,
        "quote_source": link.statement.source_label, "roll_call_id": link.roll_call.roll_call_id,
        "vote_date": link.roll_call.vote_date, "question": link.roll_call.question, "is_procedural": link.roll_call.is_procedural,
        "position": pos_by_rc.get(link.roll_call_vote_id, "no_record"),
        "bill": {"bill_number": link.roll_call.bill.bill_number, "title": link.roll_call.bill.title, "status": link.roll_call.bill.status,
                 "summary": link.roll_call.bill.summary},
        "classification": link.classification, "classification_label": ALIGNMENT[link.classification],
        "rationale": link.rationale, "assessment_method": link.assessment_method,
    } for link in links]
    idx = alignment_index([{"classification": x["classification"], "is_procedural": x["is_procedural"]} for x in comparisons])

    committees = db.scalars(select(M.Committee).where(M.Committee.candidate_id == c.id)).all()
    cids = [cm.id for cm in committees]
    direct = db.scalar(select(func.coalesce(func.sum(M.FinancialTransaction.amount_cents), 0)).where(
        M.FinancialTransaction.committee_id.in_(cids), M.FinancialTransaction.transaction_type.in_(["direct_contribution", "committee_transfer"]))) if cids else 0
    ie = {so: db.scalar(select(func.coalesce(func.sum(M.FinancialTransaction.amount_cents), 0)).where(
        M.FinancialTransaction.target_candidate_id == c.id, M.FinancialTransaction.support_oppose == so)) for so in ("support", "oppose")}

    statements = sorted(c.statements, key=lambda s: s.statement_date, reverse=True)
    return {
        "id": c.id, "slug": c.slug, "name": c.name, "office_sought": c.office_sought, "office_held": c.office_held,
        "jurisdiction": c.jurisdiction, "party": c.party, "biography": c.biography, "data_status": c.data_status,
        "statements": [{"quote": s.quote, "date": s.statement_date, "venue": s.venue, "topic": s.topic, "source_label": s.source_label,
                        "source_url": s.source_url} for s in statements[: LIMITS["statements"]]],
        "statement_total": len(statements),
        "voting_record": [_vote_out(v) for v in votes[: LIMITS["votes"]]],
        "vote_total": len(votes),
        "voting_record_note": None if votes else "No roll-call voting record. This candidate has not held legislative office.",
        "speech_vs_vote": comparisons[: LIMITS["comparisons"]],
        "alignment": idx,
        "finance": {"direct_receipts_cents": direct, "outside_support_cents": ie["support"], "outside_opposition_cents": ie["oppose"],
                    "committees": [{"committee_code": cm.committee_code, "name": cm.name} for cm in committees]},
        "sources": sorted({s.source_label for s in statements} | {f"Roll call {v.roll_call.roll_call_id} — State X Senate Clerk (demonstration record)" for v in votes}),
    }


@router.get("/candidates", response_model=CandidateList)
def list_candidates(db: Session = Depends(get_db)):
    rows = db.scalars(select(M.Candidate).order_by(M.Candidate.name)).all()
    return {"items": [CandidateSummary.model_validate(c) for c in rows]}


@router.get("/candidates/compare", response_model=CompareResponse, summary="Side-by-side comparison with identical structure")
def compare(a: str = Query(..., description="Candidate id or slug"), b: str = Query(...), db: Session = Depends(get_db)):
    ca, cb = _get(db, a), _get(db, b)
    if ca.id == cb.id:
        raise SiloError(400, "same_candidate", "Choose two different candidates to compare.")
    pa, pb = profile(db, ca), profile(db, cb)
    va = {v["roll_call_id"]: v for v in pa["voting_record"]}
    vb = {v["roll_call_id"]: v for v in pb["voting_record"]}
    shared = [{"roll_call_id": k, "bill": va[k]["bill"], "question": va[k]["question"], "vote_date": va[k]["vote_date"],
               "is_procedural": va[k]["is_procedural"], "positions": [va[k]["position"], vb[k]["position"]]}
              for k in va if k in vb]
    return {
        "candidates": [pa, pb], "shared_votes": shared, "limits": LIMITS,
        "methodology": {
            "alignment_categories": ALIGNMENT,
            "index": "Index = (consistent + 0.5 × mixed) ÷ comparable pairs × 100. Shown only with at least 4 comparable, non-procedural pairs. "
                     "It describes how documented statements relate to documented votes; it is not a measure of honesty.",
            "classification": "Each statement–vote pair is classified by a reviewer with a written rationale. SILO never infers alignment from keyword similarity.",
            "symmetry": "Both candidates are rendered with the same fields, order, limits and missing-data treatment.",
        },
    }


@router.get("/candidates/{ref}", summary="Single candidate profile")
def get_candidate(ref: str, db: Session = Depends(get_db)):
    return profile(db, _get(db, ref))
