
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReportSection(BaseModel):
    heading: str
    content: str
    citation_ids: list[str] = Field(default_factory=list)


class ClinicalEvidenceReport(BaseModel):
    report_id: Optional[str] = None
    case_id: Optional[str] = None
    title: str
    clinical_question: str
    executive_summary: str
    background: str = ""
    findings: list[ReportSection] = Field(
        default_factory=list
    )
    evidence_limitations: list[str] = Field(
        default_factory=list
    )
    safety_notes: list[str] = Field(default_factory=list)
    citations: list[dict] = Field(default_factory=list)
    conclusion: str = ""
    disclaimer: str = (
        "This report supports clinical evidence research "
        "and does not replace qualified professional judgment."
    )
    review_status: str = "pending"
    generated_at: Optional[datetime] = None


class ReportResponse(BaseModel):
    success: bool
    message: str
    report: Optional[ClinicalEvidenceReport] = None
