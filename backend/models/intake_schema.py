
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class IntakeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    clinical_question: str = Field(
        min_length=10,
        max_length=5000
    )
    title: Optional[str] = Field(
        default="Clinical Evidence Research",
        max_length=255
    )
    research_scope: Optional[str] = Field(
        default=None,
        max_length=2000
    )
    population: Optional[str] = None
    intervention: Optional[str] = None
    comparison: Optional[str] = None
    outcome: Optional[str] = None
    study_types: list[str] = Field(default_factory=list)


class IntakeResult(BaseModel):
    is_valid: bool
    normalized_question: str
    research_scope: str
    extracted_keywords: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
