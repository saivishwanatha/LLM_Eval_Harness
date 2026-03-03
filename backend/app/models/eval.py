import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

def utcnow() -> datetime:
    return datetime.utcnow()

class EvalSuite(Base):
    __tablename__ = "eval_suites"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    suite_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    __table_args__ = (
        Index("ux_eval_suites_name_version", "name", "version", unique=True),
    )

class EvalCase(Base):
    __tablename__ = "eval_cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suite_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("eval_suites.id"), nullable=False)

    case_id: Mapped[str] = mapped_column(String(160), nullable=False)
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    context_text: Mapped[str] = mapped_column(Text, nullable=False)

    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)

    dimensions: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    __table_args__ = (
        Index("ux_eval_cases_suite_caseid", "suite_id", "case_id", unique=True),
    )

class EvalRun(Base):
    __tablename__ = "eval_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suite_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("eval_suites.id"), nullable=False)

    model: Mapped[str] = mapped_column(String(120), nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    git_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="running")

    __table_args__ = (
        Index("ix_eval_runs_suite_started", "suite_id", "started_at"),
    )

class EvalOutput(Base):
    __tablename__ = "eval_outputs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("eval_runs.id"), nullable=False)
    case_row_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("eval_cases.id"), nullable=False)

    output_text: Mapped[str] = mapped_column(Text, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ux_eval_outputs_run_case", "run_id", "case_row_id", unique=True),
    )

class EvalScore(Base):
    __tablename__ = "eval_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("eval_runs.id"), nullable=False)
    case_row_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("eval_cases.id"), nullable=False)

    dimension: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)

    judge_model: Mapped[str] = mapped_column(String(120), nullable=False)
    judge_prompt_version: Mapped[str] = mapped_column(String(32), nullable=False, default="v1")
    judge_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ux_eval_scores_run_case_dim", "run_id", "case_row_id", "dimension", unique=True),
    )