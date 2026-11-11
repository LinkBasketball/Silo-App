from collections import OrderedDict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models as M
from app.api.deps import get_db
from app.core.errors import SiloError
from app.schemas import ConflictDetail, ConflictList

router = APIRouter(tags=["Geopolitical Context"])


@router.get("/conflicts", response_model=ConflictList)
def list_conflicts(db: Session = Depends(get_db)):
    rows = db.scalars(select(M.Conflict).options(selectinload(M.Conflict.events)).order_by(M.Conflict.name)).all()
    return {"items": [{"id": c.id, "slug": c.slug, "name": c.name, "region": c.region, "summary": c.summary,
                       "data_status": c.data_status, "event_count": len(c.events)} for c in rows]}


@router.get("/conflicts/{ref}", response_model=ConflictDetail)
def get_conflict(ref: str, db: Session = Depends(get_db)):
    stmt = select(M.Conflict).options(selectinload(M.Conflict.events), selectinload(M.Conflict.metrics), selectinload(M.Conflict.arguments))
    stmt = stmt.where(M.Conflict.id == int(ref)) if ref.isdigit() else stmt.where(M.Conflict.slug == ref)
    c = db.scalar(stmt)
    if c is None:
        raise SiloError(404, "not_found", f"Conflict {ref!r} was not found.")
    approaches: OrderedDict[str, dict] = OrderedDict()
    for a in c.arguments:
        ap = approaches.setdefault(a.approach, {"approach": a.approach, "for": [], "against": []})
        ap[a.stance].append({"argument": a.argument, "argument_type": a.argument_type, "evidence_note": a.evidence_note})
    return {
        "id": c.id, "slug": c.slug, "name": c.name, "region": c.region, "summary": c.summary, "actors": c.actors,
        "limitations": c.limitations, "data_status": c.data_status, "events": c.events,
        "metrics": [{"id": m.id, "metric_group": m.metric_group, "label": m.label, "value": m.value, "value_low": m.value_low,
                     "value_high": m.value_high, "unit": m.unit, "period": m.period, "scope": m.scope,
                     "methodology": m.methodology, "source_label": m.source_label, "series": m.series} for m in c.metrics],
        "approaches": list(approaches.values()),
    }
