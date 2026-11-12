
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from backend.models.intake_schema import (
    IntakeRequest,
    IntakeResult
)
from backend.models.patient_schema import (
    PatientContext,
    DeidentifiedPatientContext
)
from backend.models.evidence_schema import (
    EvidenceItem,
    EvidenceCollection,
    Citation,
    EvidenceQualityResult
)
from backend.models.report_schema import (
    ClinicalEvidenceReport,
    ReportResponse
)
from backend.models.validation_schema import (
    ValidationResult,
    ValidationIssue,
    ReviewRequest,
    ReviewResponse
)


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class CaseCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    clinical_question: str = Field(
        min_length=10, max_length=5000
    )
    patient_context: dict = Field(default_factory=dict)


class CaseResponse(BaseModel):
    id: str
    title: str
    clinical_question: str
    status: str
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkflowResponse(BaseModel):
    workflow_id: str
    case_id: str
    status: str
    current_node: Optional[str] = None
    result: dict = Field(default_factory=dict)


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    full_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


__all__ = [
    "IntakeRequest",
    "IntakeResult",
    "PatientContext",
    "DeidentifiedPatientContext",
    "EvidenceItem",
    "EvidenceCollection",
    "Citation",
    "EvidenceQualityResult",
    "ClinicalEvidenceReport",
    "ReportResponse",
    "ValidationResult",
    "ValidationIssue",
    "ReviewRequest",
    "ReviewResponse",
    "APIResponse",
    "CaseCreateRequest",
    "CaseResponse",
    "WorkflowResponse",
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
]
