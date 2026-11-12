
from backend.utils.constants import SafetyLevel


class PolicyRules:

    SYSTEM_DISCLAIMER = (
        "This system provides evidence research assistance only. "
        "It is not intended for diagnosis, treatment selection, "
        "prescription or emergency medical decision-making."
    )

    PROHIBITED_ACTIONS = [
        "automatically prescribe medication",
        "make an autonomous diagnosis",
        "replace clinician judgment",
        "issue emergency treatment instructions"
    ]

    def evaluate(self, question, evidence=None):

        findings = []

        evidence = evidence or []

        if not evidence:

            findings.append({
                "rule": "evidence_required",
                "severity": "warning",
                "message": "No supporting evidence was retrieved."
            })

        if len(question.strip()) < 10:

            findings.append({
                "rule": "question_quality",
                "severity": "warning",
                "message": "The research question is too short."
            })

        blocked = any(
            item["severity"] == "blocked"
            for item in findings
        )

        level = (
            SafetyLevel.BLOCKED.value if blocked
            else SafetyLevel.WARNING.value if findings
            else SafetyLevel.SAFE.value
        )

        return {
            "level": level,
            "findings": findings,
            "disclaimer": self.SYSTEM_DISCLAIMER,
            "human_review_required": True
        }


policy_rules = PolicyRules()
