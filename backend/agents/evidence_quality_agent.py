
import logging
from typing import Any

logger = logging.getLogger(__name__)


# This is an evidence hierarchy reference only.
# It is NOT a formal risk-of-bias assessment.
STUDY_RANK = {
    "meta_analysis": 1,
    "systematic_review": 2,
    "randomized_controlled_trial": 3,
    "cohort_study": 4,
    "case_control": 5,
    "case_report": 6,
    "other": 7,
    "unknown": 8,
}


EVIDENCE_TYPE_ALIASES = {
    "meta-analysis": "meta_analysis",
    "meta analysis": "meta_analysis",
    "systematic review": "systematic_review",
    "randomized controlled trial": "randomized_controlled_trial",
    "randomised controlled trial": "randomized_controlled_trial",
    "rct": "randomized_controlled_trial",
    "cohort": "cohort_study",
    "case-control": "case_control",
    "case control study": "case_control",
    "case report": "case_report",
}


class EvidenceQualityAgent:

    def run(self, evidence: list[dict]) -> dict:

        if not evidence:
            return {
                "assessments": [],
                "overall_quality": "insufficient",
                "evidence_count": 0,
                "warnings": [
                    "No evidence available for quality assessment."
                ]
            }

        assessments = []
        warnings = []

        for index, item in enumerate(evidence):

            if not isinstance(item, dict):
                warnings.append(
                    f"Evidence item {index + 1} is invalid."
                )
                continue

            evidence_id = item.get("id")

            title = (
                item.get("title")
                or item.get("metadata", {}).get("title")
                or "Untitled evidence"
            )

            metadata = item.get("metadata", {})

            if not isinstance(metadata, dict):
                metadata = {}

            # Use explicit study-type metadata only.
            # Do not guess the study design from the document text.
            raw_type = (
                item.get("evidence_type")
                or metadata.get("evidence_type")
                or metadata.get("study_type")
                or "unknown"
            )

            study_type = self._normalize_evidence_type(
                raw_type
            )

            relevance = self._relevance(
                item.get("relevance_score")
            )

            limitations = []

            source = (
                item.get("source")
                or metadata.get("source")
            )

            page = (
                item.get("page")
                if item.get("page") is not None
                else metadata.get("page")
            )

            if not source:
                limitations.append(
                    "Source metadata is missing."
                )

            # Page zero is valid. Only None or empty is missing.
            if page is None or page == "":
                limitations.append(
                    "Page locator is missing."
                )

            if study_type == "unknown":
                limitations.append(
                    "Study design could not be identified "
                    "from explicit metadata."
                )

            if relevance < 0.2:
                limitations.append(
                    "Low retrieval relevance."
                )

            if not evidence_id:
                limitations.append(
                    "Evidence identifier is missing."
                )

            assessments.append({
                "evidence_id": evidence_id,
                "title": title,
                "source": source,
                "page": page,
                "evidence_type": study_type,
                "relevance": relevance,
                "methodological_quality": None,
                "study_type_rank": STUDY_RANK.get(
                    study_type,
                    STUDY_RANK["unknown"]
                ),
                "limitations": limitations,
                "assessment_notes": (
                    "This assessment checks metadata and retrieval "
                    "relevance only. Study hierarchy does not establish "
                    "methodological quality or risk of bias."
                )
            })

        assessments.sort(
            key=lambda item: (
                item["study_type_rank"],
                -item["relevance"]
            )
        )

        if not assessments:
            overall_quality = "insufficient"
            warnings.append(
                "No valid evidence items could be assessed."
            )
        else:
            overall_quality = "requires_methodological_review"

        warnings.append(
            "Formal risk-of-bias and methodological assessment "
            "has not been performed."
        )

        warnings.append(
            "Evidence type is taken from explicit metadata. "
            "Unknown study designs are not automatically classified."
        )

        return {
            "assessments": assessments,
            "overall_quality": overall_quality,
            "evidence_count": len(assessments),
            "warnings": warnings
        }

    @staticmethod
    def _normalize_evidence_type(value: Any) -> str:

        if not isinstance(value, str):
            return "unknown"

        normalized = value.strip().lower()

        if not normalized:
            return "unknown"

        normalized = EVIDENCE_TYPE_ALIASES.get(
            normalized,
            normalized.replace(" ", "_").replace("-", "_")
        )

        if normalized in STUDY_RANK:
            return normalized

        return "unknown"

    @staticmethod
    def _relevance(value: Any) -> float:

        try:
            score = float(value)

            if score != score:  # NaN check
                return 0.0

            return max(0.0, min(1.0, score))

        except (TypeError, ValueError):
            return 0.0


evidence_quality_agent = EvidenceQualityAgent()
