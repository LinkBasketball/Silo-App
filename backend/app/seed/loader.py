"""Idempotently load the demonstration fixtures into an empty database."""
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as M
from app.nlp.analysis import analyze_text, classify_sentence, topic_for_sentence
from app.nlp.engine import parse
from app.seed import demo_data as D
from app.services.matching import best_excerpt, content_terms

VERIFIED_AT = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)  # fixed for deterministic output


def seed_demo(db: Session) -> bool:
    if db.scalar(select(M.NewsArticle.id).limit(1)) is not None:
        return False
    prov = M.DataProvenance(source_name="SILO demonstration fixtures", data_status=M.DataStatus.DEMO,
                            retrieved_at=VERIFIED_AT, notes=D.DEMO_NOTE)
    db.add(prov)
    db.flush()

    pubs = {}
    for p in D.PUBLISHERS:
        pub = M.Publisher(**{k: v for k, v in p.items() if k != "relationships"}, provenance_id=prov.id)
        for r in p["relationships"]:
            pub.relationships.append(M.PublisherRelationship(**{"established": True, **r}))
        db.add(pub)
        pubs[p["slug"]] = pub

    sources = {}
    for e in D.EVIDENCE:
        src = M.EvidenceSource(**e, provenance_id=prov.id)
        db.add(src)
        sources[e["record_key"]] = src
    db.flush()

    for a in D.ARTICLES:
        art = M.NewsArticle(
            slug=a["slug"], title=a["title"], dek=a["dek"], article_type=a["article_type"], author=a["author"],
            published_at=datetime.fromisoformat(a["published_at"].replace("Z", "+00:00")), body=a["body"],
            primary_topic=a["primary_topic"], publisher_id=pubs[a["publisher"]].id, provenance_id=prov.id,
            last_verified_at=VERIFIED_AT,
        )
        db.add(art)
        doc = parse(a["body"])
        result = analyze_text(doc)
        claims_by_idx = {}
        for c in result["claims"]:
            claims_by_idx[c["sentence_index"]] = M.ExtractedClaim(
                sentence_index=c["sentence_index"], text=c["text"], start_char=c["start"], end_char=c["end"],
                sentence_class=c["sentence_class"], claim_type=c["claim_type"], topic=c["topic"])
        for needle, key, rel, expl in a["annotations"]:
            sent = next((s for s in doc.sentences if needle in s.text), None)
            if sent is None:
                raise ValueError(f"Annotation {needle!r} not found in article {a['slug']}")
            claim = claims_by_idx.get(sent.index)
            if claim is None:  # curator marked a sentence the classifier did not flag
                cls = classify_sentence(sent)
                claim = M.ExtractedClaim(sentence_index=sent.index, text=sent.text, start_char=sent.start,
                                         end_char=sent.end, sentence_class=cls["sentence_class"],
                                         claim_type=cls["claim_type"] or "event", topic=topic_for_sentence(sent)[0])
                claims_by_idx[sent.index] = claim
            src = sources[key]
            claim.evidence.append(M.ClaimEvidence(
                evidence_source_id=src.id, relationship_type=rel, explanation=expl,
                excerpt=best_excerpt(src.content, content_terms(sent.text)), retrieved_at=VERIFIED_AT))
        art.claims = [claims_by_idx[i] for i in sorted(claims_by_idx)]

    cands = {}
    for c in D.CANDIDATES:
        cand = M.Candidate(**c, provenance_id=prov.id)
        db.add(cand)
        cands[c["slug"]] = cand
    db.flush()

    rcs = {}
    for b in D.BILLS:
        bill = M.LegislativeBill(**{k: v for k, v in b.items() if k != "roll_calls"},
                                 source_label=f"State X Legislature bill record {b['bill_number']} {D.D}")
        db.add(bill)
        for rc in b["roll_calls"]:
            vote = M.RollCallVote(**{k: v for k, v in rc.items() if k != "positions"}, bill=bill)
            db.add(vote)
            rcs[rc["roll_call_id"]] = vote
            db.flush()
            for slug, pos in rc["positions"].items():
                db.add(M.CandidateVote(candidate_id=cands[slug].id, roll_call_vote_id=vote.id, position=pos))
    db.flush()

    for _key, slug, quote, when, venue, topic, links in D.STATEMENTS:
        st = M.PublicStatement(candidate_id=cands[slug].id, quote=quote, statement_date=when, venue=venue, topic=topic,
                               source_label=f"{venue}, {when.strftime('%B %-d, %Y')} — transcript {D.D}")
        db.add(st)
        db.flush()
        for rc_id, cls, why in links:
            db.add(M.StatementVoteLink(statement_id=st.id, roll_call_vote_id=rcs[rc_id].id, classification=cls, rationale=why))

    comms = {}
    for c in D.COMMITTEES:
        cm = M.Committee(committee_code=c["committee_code"], name=c["name"], committee_type=c["committee_type"],
                         candidate_id=cands[c["candidate"]].id if c["candidate"] else None, provenance_id=prov.id,
                         treasurer="Treasurer of record (demonstration)")
        db.add(cm)
        comms[c["committee_code"]] = cm
    db.flush()

    def add_tx(uid, committee, ttype, counterparty, category, dollars, period, **kw):
        db.add(M.FinancialTransaction(
            transaction_uid=uid, committee_id=comms[committee].id, transaction_type=ttype, counterparty=counterparty,
            counterparty_category=category, amount_cents=dollars * 100, transaction_date=D.PERIODS[period],
            reporting_period=period, filing_id=f"DEMO-FIL-{committee[5:]}-{period[-2:]}",
            filed_date=D.PERIODS[period].replace(day=15, month=D.PERIODS[period].month + 1 if D.PERIODS[period].month < 12 else 12),
            **kw))

    for recipient, cat, cp, amounts in D.RECEIPTS:
        for period, dollars in amounts.items():
            add_tx(f"{recipient}:{cat}:{cp[:24]}:{period}", recipient, "direct_contribution", cp, cat, dollars, period)
    for recipient, cp, amounts in D.TRANSFERS:
        for period, dollars in amounts.items():
            add_tx(f"{recipient}:transfer:{cp[:24]}:{period}", recipient, "committee_transfer", cp, "party", dollars, period)
    for spender, target, so, vendor, amounts in D.IES:
        for period, dollars in amounts.items():
            add_tx(f"{spender}:ie:{target}:{so}:{period}", spender, "independent_expenditure", vendor, "vendor", dollars, period,
                   support_oppose=so, target_candidate_id=cands[target].id,
                   memo="Independent expenditure: spent without coordination with the candidate. Not a contribution to the campaign.")

    for c in D.CONFLICTS:
        conf = M.Conflict(slug=c["slug"], name=c["name"], region=c["region"], summary=c["summary"],
                          actors=c["actors"], limitations=c["limitations"])
        for d, title, desc, etype, cat, src in c["events"]:
            conf.events.append(M.ConflictEvent(event_date=d, title=title, description=desc, event_type=etype,
                                               evidence_category=cat, source_label=f"{src} {D.D}"))
        for m in c["metrics"]:
            conf.metrics.append(M.ConflictMetric(**{**m, "source_label": f"{m['source_label']} {D.D}"}))
        for approach, stance, atype, arg, note in c["arguments"]:
            conf.arguments.append(M.PolicyArgument(approach=approach, stance=stance, argument_type=atype,
                                                   argument=arg, evidence_note=note))
        db.add(conf)
    db.commit()
    return True
