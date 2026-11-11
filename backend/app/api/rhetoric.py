from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.core.errors import SiloError
from app.core.ratelimit import rate_limit
from app.nlp.analysis import analyze_text
from app.nlp.engine import parse
from app.schemas import RhetoricRequest, RhetoricResponse

router = APIRouter(tags=["Rhetoric & Neutral Language"])


@router.post("/rhetoric/analyze", response_model=RhetoricResponse, dependencies=[Depends(rate_limit)])
def rhetoric(req: RhetoricRequest):
    if len(req.text) > get_settings().max_text_chars:
        raise SiloError(413, "text_too_long", f"Text is limited to {get_settings().max_text_chars:,} characters.")
    r = analyze_text(parse(req.text), voice=req.voice)
    return {"engine": r["engine"], "rhetoric": r["rhetoric"], "sentences": r["sentences"],
            "language_audit": r["language_audit"], "neutral_summary": r["neutral_summary"], "quotes": r["quotes"]}
