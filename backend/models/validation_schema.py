
from pydantic import BaseModel, Field
from typing import Optional


class ValidationIssue(BaseModel):
    category: str
    message: str
    severity: str = "warning"
    reference: Optional[str] = None


class ValidationResult(BaseModel):
    is_valid: bool
    schema_valid: bool = True
    citation_valid: bool = True
    groundedness_valid: bool = True
    safety_valid: bool = True

    issues: list[ValidationIssue] = Field(
        default_factory=list
    )

    missing_citations: list[str] = Field(
        default_factory=list
    )

    unsupported_claims: list[str] = Field(
        default_factory=list
    )

    warnings: list[str] = Field(
        default_factory=list
    )


class ReviewRequest(BaseModel):
    decision: str
    comments: str = ""


class ReviewResponse(BaseModel):
    review_id: str
    case_id: str
    decision: str
    comments: str = ""
    reviewer_id: str
