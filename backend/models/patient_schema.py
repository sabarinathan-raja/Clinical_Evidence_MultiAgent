
from pydantic import BaseModel, Field
from typing import Optional


class PatientContext(BaseModel):
    age_group: Optional[str] = None
    sex: Optional[str] = None
    relevant_conditions: list[str] = Field(
        default_factory=list
    )
    relevant_medications: list[str] = Field(
        default_factory=list
    )
    allergies: list[str] = Field(
        default_factory=list
    )
    clinical_history: Optional[str] = None
    additional_context: Optional[str] = None


class DeidentifiedPatientContext(BaseModel):
    age_group: Optional[str] = None
    sex: Optional[str] = None
    relevant_conditions: list[str] = Field(
        default_factory=list
    )
    relevant_medications: list[str] = Field(
        default_factory=list
    )
    allergies: list[str] = Field(
        default_factory=list
    )
    clinical_history: Optional[str] = None
    additional_context: Optional[str] = None

    deidentified: bool = True
