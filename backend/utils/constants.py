
from enum import Enum


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    INTAKE = "intake"
    RETRIEVING = "retrieving"
    EVALUATING = "evaluating"
    SAFETY_CHECK = "safety_check"
    GENERATING = "generating"
    VALIDATING = "validating"
    REVIEW_PENDING = "review_pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUIRED = "revision_required"
    FAILED = "failed"


class AgentName(str, Enum):
    INTAKE = "intake_scope_agent"
    PATIENT_CONTEXT = "patient_context_agent"
    EVIDENCE_RETRIEVAL = "evidence_retrieval_agent"
    EVIDENCE_QUALITY = "evidence_quality_agent"
    SAFETY_POLICY = "safety_policy_agent"
    SUMMARY_GENERATION = "summary_generation_agent"
    OUTPUT_VALIDATION = "output_validation_agent"


class EvidenceType(str, Enum):
    GUIDELINE = "guideline"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    RANDOMIZED_CONTROLLED_TRIAL = "randomized_controlled_trial"
    COHORT_STUDY = "cohort_study"
    CASE_CONTROL = "case_control"
    CASE_REPORT = "case_report"
    OTHER = "other"


class ReviewDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUIRED = "revision_required"


class SafetyLevel(str, Enum):
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"


DEFAULT_TOP_K = 5
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 150

SUPPORTED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md"
}

DEFAULT_SYSTEM_DISCLAIMER = (
    "This application provides clinical evidence research "
    "assistance only. It is not a diagnostic system and "
    "does not replace professional clinical judgment."
)
