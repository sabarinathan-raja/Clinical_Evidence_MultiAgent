
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class EvidenceItem(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    source: str = ""
    citation: str = ""
    document_id: Optional[str] = None
    evidence_type: str = "other"
    relevance_score: Optional[float] = Field(
        default=None, ge=0, le=1
    )
    quality_score: Optional[float] = Field(
        default=None, ge=0, le=1
    )
    publication_year: Optional[int] = None
    doi: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class EvidenceCollection(BaseModel):
    query: str
    items: list[EvidenceItem] = Field(default_factory=list)
    total_retrieved: int = 0
    retrieval_method: str = "hybrid"


class Citation(BaseModel):
    citation_id: str
    title: str
    source: str
    locator: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    evidence_id: Optional[str] = None


class EvidenceQualityResult(BaseModel):
    evidence_id: str
    relevance: float = Field(ge=0, le=1)
    methodological_quality: Optional[float] = Field(
        default=None, ge=0, le=1
    )
    evidence_type: str
    limitations: list[str] = Field(default_factory=list)
    assessment_notes: str = ""
