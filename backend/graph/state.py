
from typing import TypedDict, Optional, Any


class ClinicalEvidenceState(TypedDict, total=False):

    # Request information
    case_id: str
    workflow_id: str
    thread_id: str

    clinical_question: str
    title: str
    research_scope: str

    # Patient information
    patient_context: dict
    deidentified_patient_context: dict

    # Intake results
    intake_result: dict

    # Retrieval results
    retrieval_result: dict
    evidence: list[dict]
    citations: list[dict]
    evidence_context: str

    # Evidence quality
    evidence_quality: dict

    # Safety
    safety_result: dict
    safety_blocked: bool

    # Summary
    summary_result: dict
    report: dict

    # Validation
    validation_result: dict

    # Workflow
    status: str
    current_node: str
    completed_agents: list[str]
    warnings: list[str]
    errors: list[str]

    # Human review
    review_required: bool
    review_decision: Optional[str]

    # Final response
    success: bool
    final_result: dict

    # Runtime metadata
    started_at: Optional[str]
    completed_at: Optional[str]
    # Human review
    review_required: bool
    review_decision: Optional[str]
    review_comments: str
    reviewer_id: Optional[str]

    # Revision management
    revision_count: int
    revision_history: list[dict]