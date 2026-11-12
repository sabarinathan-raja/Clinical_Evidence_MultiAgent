
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer,
    ForeignKey, JSON, Float, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.connection import Base


def generate_id():
    return str(uuid.uuid4())


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True
    )
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(
        String(50), default="researcher"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    cases = relationship("ClinicalCase", back_populates="owner")


class ClinicalCase(Base):
    __tablename__ = "clinical_cases"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    title: Mapped[str] = mapped_column(String(255))
    clinical_question: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(50), default="pending", index=True
    )
    patient_context: Mapped[dict] = mapped_column(
        JSON, default=dict
    )
    created_by: Mapped[str] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now,
        onupdate=utc_now
    )

    owner = relationship("User", back_populates="cases")
    documents = relationship(
        "Document", back_populates="case",
        cascade="all, delete-orphan"
    )
    workflows = relationship(
        "WorkflowRun", back_populates="case",
        cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    case_id: Mapped[str] = mapped_column(
        ForeignKey("clinical_cases.id"), index=True
    )
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(Text)
    file_type: Mapped[str] = mapped_column(String(30))
    checksum: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    processing_status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )
    metadata_json: Mapped[dict] = mapped_column(
        JSON, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    case = relationship("ClinicalCase", back_populates="documents")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    case_id: Mapped[str] = mapped_column(
        ForeignKey("clinical_cases.id"), index=True
    )
    document_id: Mapped[str | None] = mapped_column(
        ForeignKey("documents.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(Text, default="")
    citation: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text)
    evidence_type: Mapped[str] = mapped_column(
        String(100), default="other"
    )
    quality_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    relevance_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    metadata_json: Mapped[dict] = mapped_column(
        JSON, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    case_id: Mapped[str] = mapped_column(
        ForeignKey("clinical_cases.id"), index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="pending", index=True
    )
    current_node: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    case = relationship("ClinicalCase", back_populates="workflows")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    case_id: Mapped[str] = mapped_column(
        ForeignKey("clinical_cases.id"), index=True
    )
    workflow_id: Mapped[str] = mapped_column(
        ForeignKey("workflow_runs.id"), index=True
    )
    reviewer_id: Mapped[str] = mapped_column(
        ForeignKey("users.id")
    )
    decision: Mapped[str] = mapped_column(String(50))
    comments: Mapped[str] = mapped_column(Text, default="")
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    case_id: Mapped[str | None] = mapped_column(
        ForeignKey("clinical_cases.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), index=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


Index("ix_case_status_created", ClinicalCase.status, ClinicalCase.created_at)
Index("ix_evidence_case_type", Evidence.case_id, Evidence.evidence_type)
