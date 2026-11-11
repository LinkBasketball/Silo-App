"""Request/response schemas. Response models document the stable top-level contract; deeply
nested analysis payloads are typed as dicts and documented in docs/ARCHITECTURE.md."""
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DataStatus = Literal["live", "cached", "demo", "unavailable", "user_submitted"]


class Page(BaseModel):
    page: int
    page_size: int
    total: int
    pages: int


class Health(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    database: str
    nlp_engine: str
    demo_mode: bool
    live_data_enabled: bool


class PublisherBrief(BaseModel):
    id: int
    name: str
    ownership_type: str


class NewsListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    title: str
    dek: str | None
    article_type: str
    author: str | None
    published_at: datetime
    primary_topic: str
    data_status: DataStatus
    publisher: PublisherBrief
    claim_count: int
    coverage_state: str
    coverage_score: int | None


class NewsList(Page):
    items: list[NewsListItem]


class ArticleDetail(NewsListItem):
    body: str
    source_url: str | None
    last_verified_at: datetime | None
    claims: list[dict[str, Any]]


class Coverage(BaseModel):
    state: Literal["scored", "insufficient_evidence"]
    score: int | None
    band: str | None
    reason: str | None
    version: str
    claims_total: int
    claims_supported: int
    claims_conflicting: int
    claims_context_only: int
    claims_lacking_evidence: int


class ContextPayload(BaseModel):
    article_id: int | None
    title: str
    subtitle: str | None
    data_status: DataStatus
    last_verified_at: datetime | None
    engine: str
    coverage: Coverage
    evidence: list[dict[str, Any]]
    gaps: list[dict[str, Any]]
    topics: dict[str, Any]
    publisher: dict[str, Any] | None
    sources: list[dict[str, Any]]
    methodology: dict[str, Any]


class AnalyzeRequest(BaseModel):
    text: str | None = Field(None, description="Article or speech text to analyze.")
    url: str | None = Field(None, description="Public article URL (http/https). Paywalled pages are not bypassed.")
    article_id: int | None = Field(None, description="Analyze a stored article.")
    title: str | None = Field(None, max_length=300)
    voice: Literal["text", "speech", "opinion"] = "text"

    @model_validator(mode="after")
    def exactly_one(self):
        given = [x for x in (self.text, self.url, self.article_id) if x not in (None, "")]
        if len(given) != 1:
            raise ValueError("Provide exactly one of: text, url, article_id.")
        if self.text is not None and len(self.text.strip()) < 20:
            raise ValueError("Text must be at least 20 characters.")
        return self


class AnalyzeResponse(BaseModel):
    input: dict[str, Any]
    context: ContextPayload
    analysis: dict[str, Any]
    analyzed_at: datetime
    duration_ms: int


class RhetoricRequest(BaseModel):
    text: str = Field(..., min_length=20)
    voice: Literal["text", "speech", "opinion"] = "text"


class RhetoricResponse(BaseModel):
    engine: str
    rhetoric: dict[str, Any]
    sentences: list[dict[str, Any]]
    language_audit: list[dict[str, Any]]
    neutral_summary: dict[str, Any]
    quotes: list[dict[str, Any]]


class CandidateSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    office_sought: str
    office_held: str | None
    jurisdiction: str
    party: str
    data_status: DataStatus


class CandidateList(BaseModel):
    items: list[CandidateSummary]


class CompareResponse(BaseModel):
    candidates: list[dict[str, Any]]
    shared_votes: list[dict[str, Any]]
    limits: dict[str, int]
    methodology: dict[str, Any]


class ConflictSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    region: str
    summary: str
    data_status: DataStatus
    event_count: int


class ConflictList(BaseModel):
    items: list[ConflictSummary]


class ConflictEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_date: date
    title: str
    description: str
    event_type: str
    evidence_category: str
    source_label: str
    source_url: str | None


class ConflictDetail(BaseModel):
    id: int
    slug: str
    name: str
    region: str
    summary: str
    actors: list[str]
    limitations: str
    data_status: DataStatus
    events: list[ConflictEventOut]
    metrics: list[dict[str, Any]]
    approaches: list[dict[str, Any]]
