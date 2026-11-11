"""Relational data model. Every civic record carries a data_status and a provenance link."""
from datetime import UTC, date, datetime
from enum import StrEnum

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class DataStatus(StrEnum):
    LIVE = "live"            # fetched from an official source during this request
    CACHED = "cached"        # real record fetched earlier and stored
    DEMO = "demo"            # fictional, illustrative fixture
    UNAVAILABLE = "unavailable"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class DataProvenance(TimestampMixin, Base):
    __tablename__ = "data_provenance"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_name: Mapped[str] = mapped_column(String(200))
    source_url: Mapped[str | None] = mapped_column(String(500))
    data_status: Mapped[str] = mapped_column(String(20), default=DataStatus.DEMO, index=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    notes: Mapped[str | None] = mapped_column(Text)


# ───────────────────────── News ─────────────────────────
class Publisher(TimestampMixin, Base):
    __tablename__ = "publishers"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    legal_entity: Mapped[str | None] = mapped_column(String(200))
    parent_organization: Mapped[str | None] = mapped_column(String(200))
    ownership_type: Mapped[str] = mapped_column(String(40))  # corporate | nonprofit | cooperative | public
    description: Mapped[str | None] = mapped_column(Text)
    data_status: Mapped[str] = mapped_column(String(20), default=DataStatus.DEMO)
    provenance_id: Mapped[int | None] = mapped_column(ForeignKey("data_provenance.id"))
    provenance: Mapped[DataProvenance | None] = relationship()
    relationships: Mapped[list["PublisherRelationship"]] = relationship(
        back_populates="publisher", cascade="all, delete-orphan", order_by="PublisherRelationship.id"
    )


class PublisherRelationship(TimestampMixin, Base):
    __tablename__ = "publisher_relationships"
    id: Mapped[int] = mapped_column(primary_key=True)
    publisher_id: Mapped[int] = mapped_column(ForeignKey("publishers.id", ondelete="CASCADE"), index=True)
    related_entity: Mapped[str] = mapped_column(String(200))
    relationship_type: Mapped[str] = mapped_column(String(60))  # owner | parent | funder | grant | board
    description: Mapped[str] = mapped_column(Text)
    amount_usd: Mapped[int | None] = mapped_column(Integer)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    established: Mapped[bool] = mapped_column(Boolean, default=True)  # documented vs "not established"
    source_label: Mapped[str] = mapped_column(String(300))
    source_url: Mapped[str | None] = mapped_column(String(500))
    publisher: Mapped[Publisher] = relationship(back_populates="relationships")


class NewsArticle(TimestampMixin, Base):
    __tablename__ = "news_articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    title: Mapped[str] = mapped_column(String(300))
    dek: Mapped[str | None] = mapped_column(Text)
    article_type: Mapped[str] = mapped_column(String(30), default="news")  # news | opinion | speech
    author: Mapped[str | None] = mapped_column(String(200))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    body: Mapped[str] = mapped_column(Text)
    primary_topic: Mapped[str] = mapped_column(String(60), index=True)
    source_url: Mapped[str | None] = mapped_column(String(500))
    data_status: Mapped[str] = mapped_column(String(20), default=DataStatus.DEMO)
    publisher_id: Mapped[int] = mapped_column(ForeignKey("publishers.id"), index=True)
    provenance_id: Mapped[int | None] = mapped_column(ForeignKey("data_provenance.id"))
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    publisher: Mapped[Publisher] = relationship()
    provenance: Mapped[DataProvenance | None] = relationship()
    claims: Mapped[list["ExtractedClaim"]] = relationship(
        back_populates="article", cascade="all, delete-orphan", order_by="ExtractedClaim.sentence_index"
    )


class EvidenceSource(TimestampMixin, Base):
    __tablename__ = "evidence_sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    record_key: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(String(300))
    organization: Mapped[str] = mapped_column(String(200))
    source_type: Mapped[str] = mapped_column(String(40))  # see services.scoring.SOURCE_QUALITY
    record_date: Mapped[date | None] = mapped_column(Date)
    url: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)  # the record text shown in the source dialog
    entities: Mapped[list[str]] = mapped_column(JSON, default=list)  # entity gate for matching
    data_status: Mapped[str] = mapped_column(String(20), default=DataStatus.DEMO)
    provenance_id: Mapped[int | None] = mapped_column(ForeignKey("data_provenance.id"))
    provenance: Mapped[DataProvenance | None] = relationship()


class ExtractedClaim(TimestampMixin, Base):
    __tablename__ = "extracted_claims"
    __table_args__ = (UniqueConstraint("article_id", "sentence_index"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("news_articles.id", ondelete="CASCADE"), index=True)
    sentence_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    start_char: Mapped[int] = mapped_column(Integer)
    end_char: Mapped[int] = mapped_column(Integer)
    sentence_class: Mapped[str] = mapped_column(String(40))
    claim_type: Mapped[str] = mapped_column(String(40))
    topic: Mapped[str] = mapped_column(String(60))
    article: Mapped[NewsArticle] = relationship(back_populates="claims")
    evidence: Mapped[list["ClaimEvidence"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan", order_by="ClaimEvidence.id"
    )


class ClaimEvidence(TimestampMixin, Base):
    __tablename__ = "claim_evidence"
    __table_args__ = (UniqueConstraint("claim_id", "evidence_source_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("extracted_claims.id", ondelete="CASCADE"), index=True)
    evidence_source_id: Mapped[int] = mapped_column(ForeignKey("evidence_sources.id"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(40))
    excerpt: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)
    assessment_method: Mapped[str] = mapped_column(String(40), default="curated_demo_annotation")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    claim: Mapped[ExtractedClaim] = relationship(back_populates="evidence")
    source: Mapped[EvidenceSource] = relationship()


# ───────────────────────── Candidates & votes ─────────────────────────
class Candidate(TimestampMixin, Base):
    __tablename__ = "candidates"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    office_sought: Mapped[str] = mapped_column(String(200))
    office_held: Mapped[str | None] = mapped_column(String(200))
    jurisdiction: Mapped[str] = mapped_column(String(120))
    party: Mapped[str] = mapped_column(String(80))
    biography: Mapped[str] = mapped_column(Text)
    data_status: Mapped[str] = mapped_column(String(20), default=DataStatus.DEMO)
    provenance_id: Mapped[int | None] = mapped_column(ForeignKey("data_provenance.id"))
    statements: Mapped[list["PublicStatement"]] = relationship(
        back_populates="candidate", order_by="PublicStatement.statement_date"
    )


class PublicStatement(TimestampMixin, Base):
    __tablename__ = "public_statements"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    quote: Mapped[str] = mapped_column(Text)  # verbatim; never rewritten
    statement_date: Mapped[date] = mapped_column(Date)
    venue: Mapped[str] = mapped_column(String(200))
    topic: Mapped[str] = mapped_column(String(60))
    source_label: Mapped[str] = mapped_column(String(300))
    source_url: Mapped[str | None] = mapped_column(String(500))
    data_status: Mapped[str] = mapped_column(String(20), default=DataStatus.DEMO)
    candidate: Mapped[Candidate] = relationship(back_populates="statements")


class LegislativeBill(TimestampMixin, Base):
    __tablename__ = "legislative_bills"
    id: Mapped[int] = mapped_column(primary_key=True)
    bill_number: Mapped[str] = mapped_column(String(40), unique=True)
    title: Mapped[str] = mapped_column(String(300))
    summary: Mapped[str] = mapped_column(Text)
    topic: Mapped[str] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(60))
    introduced_date: Mapped[date] = mapped_column(Date)
    source_label: Mapped[str] = mapped_column(String(300))
    source_url: Mapped[str | None] = mapped_column(String(500))
    data_status: Mapped[str] = mapped_column(String(20), default=DataStatus.DEMO)
    roll_calls: Mapped[list["RollCallVote"]] = relationship(back_populates="bill")


class RollCallVote(TimestampMixin, Base):
    __tablename__ = "roll_call_votes"
    id: Mapped[int] = mapped_column(primary_key=True)
    roll_call_id: Mapped[str] = mapped_column(String(40), unique=True)
    bill_id: Mapped[int] = mapped_column(ForeignKey("legislative_bills.id"), index=True)
    vote_date: Mapped[date] = mapped_column(Date)
    question: Mapped[str] = mapped_column(String(200))
    is_procedural: Mapped[bool] = mapped_column(Boolean, default=False)
    result: Mapped[str] = mapped_column(String(60))
    yeas: Mapped[int] = mapped_column(Integer)
    nays: Mapped[int] = mapped_column(Integer)
    data_status: Mapped[str] = mapped_column(String(20), default=DataStatus.DEMO)
    bill: Mapped[LegislativeBill] = relationship(back_populates="roll_calls")


class CandidateVote(TimestampMixin, Base):
    __tablename__ = "candidate_votes"
    __table_args__ = (UniqueConstraint("candidate_id", "roll_call_vote_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    roll_call_vote_id: Mapped[int] = mapped_column(ForeignKey("roll_call_votes.id"), index=True)
    position: Mapped[str] = mapped_column(String(20))  # yea | nay | present | not_voting
    roll_call: Mapped[RollCallVote] = relationship()


class StatementVoteLink(TimestampMixin, Base):
    """A curated, human-reviewable judgement that a statement and a vote are related."""
    __tablename__ = "statement_vote_links"
    __table_args__ = (UniqueConstraint("statement_id", "roll_call_vote_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    statement_id: Mapped[int] = mapped_column(ForeignKey("public_statements.id"), index=True)
    roll_call_vote_id: Mapped[int] = mapped_column(ForeignKey("roll_call_votes.id"), index=True)
    classification: Mapped[str] = mapped_column(String(40))
    rationale: Mapped[str] = mapped_column(Text)
    assessment_method: Mapped[str] = mapped_column(String(40), default="curated_demo_annotation")
    statement: Mapped[PublicStatement] = relationship()
    roll_call: Mapped[RollCallVote] = relationship()


# ───────────────────────── Finance ─────────────────────────
class Committee(TimestampMixin, Base):
    __tablename__ = "committees"
    id: Mapped[int] = mapped_column(primary_key=True)
    committee_code: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    committee_type: Mapped[str] = mapped_column(String(60))  # principal_campaign | pac | ie_only | party
    candidate_id: Mapped[int | None] = mapped_column(ForeignKey("candidates.id"), index=True)
    treasurer: Mapped[str | None] = mapped_column(String(200))
    data_status: Mapped[str] = mapped_column(String(20), default=DataStatus.DEMO)
    provenance_id: Mapped[int | None] = mapped_column(ForeignKey("data_provenance.id"))
    candidate: Mapped[Candidate | None] = relationship()


class FinancialTransaction(TimestampMixin, Base):
    __tablename__ = "financial_transactions"
    __table_args__ = (Index("ix_fin_period_type", "reporting_period", "transaction_type"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_uid: Mapped[str] = mapped_column(String(80), unique=True)  # dedupe key
    committee_id: Mapped[int] = mapped_column(ForeignKey("committees.id"), index=True)
    transaction_type: Mapped[str] = mapped_column(String(40))
    # direct_contribution | committee_transfer | independent_expenditure | operating_disbursement
    counterparty: Mapped[str] = mapped_column(String(200))
    counterparty_category: Mapped[str] = mapped_column(String(40))
    # individual_itemized | individual_unitemized | pac | party | candidate_self | vendor | committee
    amount_cents: Mapped[int] = mapped_column(Integer)
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    reporting_period: Mapped[str] = mapped_column(String(20))
    support_oppose: Mapped[str | None] = mapped_column(String(10))  # support | oppose (IEs only)
    target_candidate_id: Mapped[int | None] = mapped_column(ForeignKey("candidates.id"), index=True)
    filing_id: Mapped[str] = mapped_column(String(60))
    filed_date: Mapped[date] = mapped_column(Date)
    memo: Mapped[str | None] = mapped_column(Text)
    data_status: Mapped[str] = mapped_column(String(20), default=DataStatus.DEMO)
    committee: Mapped[Committee] = relationship()
    target_candidate: Mapped[Candidate | None] = relationship()


# ───────────────────────── Geopolitics ─────────────────────────
class Conflict(TimestampMixin, Base):
    __tablename__ = "conflicts"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    region: Mapped[str] = mapped_column(String(120))
    summary: Mapped[str] = mapped_column(Text)
    actors: Mapped[list[str]] = mapped_column(JSON, default=list)
    limitations: Mapped[str] = mapped_column(Text)
    data_status: Mapped[str] = mapped_column(String(20), default=DataStatus.DEMO)
    events: Mapped[list["ConflictEvent"]] = relationship(
        back_populates="conflict", cascade="all, delete-orphan", order_by="ConflictEvent.event_date"
    )
    metrics: Mapped[list["ConflictMetric"]] = relationship(
        back_populates="conflict", cascade="all, delete-orphan", order_by="ConflictMetric.id"
    )
    arguments: Mapped[list["PolicyArgument"]] = relationship(
        back_populates="conflict", cascade="all, delete-orphan", order_by="PolicyArgument.id"
    )


class ConflictEvent(TimestampMixin, Base):
    __tablename__ = "conflict_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    conflict_id: Mapped[int] = mapped_column(ForeignKey("conflicts.id", ondelete="CASCADE"), index=True)
    event_date: Mapped[date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    event_type: Mapped[str] = mapped_column(String(40))  # agreement | resolution | escalation | humanitarian | diplomacy
    evidence_category: Mapped[str] = mapped_column(String(40))  # documented_record | contested_interpretation
    source_label: Mapped[str] = mapped_column(String(300))
    source_url: Mapped[str | None] = mapped_column(String(500))
    conflict: Mapped[Conflict] = relationship(back_populates="events")


class ConflictMetric(TimestampMixin, Base):
    __tablename__ = "conflict_metrics"
    id: Mapped[int] = mapped_column(primary_key=True)
    conflict_id: Mapped[int] = mapped_column(ForeignKey("conflicts.id", ondelete="CASCADE"), index=True)
    metric_group: Mapped[str] = mapped_column(String(30))  # humanitarian | economic
    label: Mapped[str] = mapped_column(String(200))
    value: Mapped[float] = mapped_column(Float)
    value_low: Mapped[float | None] = mapped_column(Float)
    value_high: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(40))
    period: Mapped[str] = mapped_column(String(60))
    scope: Mapped[str] = mapped_column(String(200))
    methodology: Mapped[str] = mapped_column(Text)
    source_label: Mapped[str] = mapped_column(String(300))
    series: Mapped[list[dict] | None] = mapped_column(JSON)
    conflict: Mapped[Conflict] = relationship(back_populates="metrics")


class PolicyArgument(TimestampMixin, Base):
    __tablename__ = "policy_arguments"
    id: Mapped[int] = mapped_column(primary_key=True)
    conflict_id: Mapped[int] = mapped_column(ForeignKey("conflicts.id", ondelete="CASCADE"), index=True)
    approach: Mapped[str] = mapped_column(String(120))
    stance: Mapped[str] = mapped_column(String(20))  # for | against
    argument: Mapped[str] = mapped_column(Text)
    argument_type: Mapped[str] = mapped_column(String(30))  # empirical | normative
    evidence_note: Mapped[str] = mapped_column(Text)
    conflict: Mapped[Conflict] = relationship(back_populates="arguments")


# ───────────────────────── Audit ─────────────────────────
class AnalysisRun(Base):
    """Minimal audit row. Stores a hash and aggregate metrics — never the submitted text."""
    __tablename__ = "analysis_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    input_kind: Mapped[str] = mapped_column(String(20))  # text | url | article
    input_sha256: Mapped[str] = mapped_column(String(64), index=True)
    engine: Mapped[str] = mapped_column(String(40))
    claim_count: Mapped[int] = mapped_column(Integer)
    coverage_score: Mapped[int | None] = mapped_column(Integer)
    duration_ms: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
