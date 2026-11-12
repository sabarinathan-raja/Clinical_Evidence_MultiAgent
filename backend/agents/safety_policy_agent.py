
import re

from backend.utils.constants import SafetyLevel


class SafetyPolicyAgent:

    BLOCKED_PATTERNS = [
        r"\bprescribe\b",
        r"\bdiagnose this patient\b",
        r"\bguarantee a cure\b",
        r"\bignore medical supervision\b",
        r"\bchange the prescribed dose\b"
    ]

    WARNING_PATTERNS = [
        r"\bemergency\b",
        r"\bsuicidal\b",
        r"\bchest pain\b",
        r"\bsevere bleeding\b",
        r"\boverdose\b",
        r"\bunconscious\b"
    ]

    def run(
        self,
        question: str,
        context: dict = None,
        evidence: list = None
    ) -> dict:

        text = (question or "").lower()

        findings = []
        blocked = False
        warning = False

        # 1. Check potentially unsafe requests
        for pattern in self.BLOCKED_PATTERNS:

            if re.search(pattern, text):

                blocked = True

                findings.append({
                    "type": "unsafe_request",
                    "message": (
                        "The request asks for a potentially "
                        "unsafe clinical action."
                    )
                })

        # 2. Check potentially urgent clinical context
        for pattern in self.WARNING_PATTERNS:

            if re.search(pattern, text):

                warning = True

                findings.append({
                    "type": "urgent_context",
                    "message": (
                        "Potential urgent clinical context detected. "
                        "Qualified human clinical assessment is required."
                    )
                })

        # 3. Check evidence availability
        if evidence is None:
            evidence = []

        if not evidence:

            warning = True

            findings.append({
                "type": "missing_evidence",
                "message": (
                    "No retrieved evidence is available."
                )
            })

        # 4. Determine safety level
        if blocked:

            level = SafetyLevel.BLOCKED.value

        elif warning:

            level = SafetyLevel.WARNING.value

        else:

            level = SafetyLevel.SAFE.value

        # 5. Return safety assessment
        return {
            "safety_level": level,

            # True means the request was not blocked.
            # It does not certify clinical safety.
            "is_safe": not blocked,

            # Every clinical report requires human review.
            "requires_human_review": True,

            "findings": findings,

            "disclaimer": (
                "Clinical research assistance only. "
                "Not a diagnostic or treatment recommendation."
            )
        }


safety_policy_agent = SafetyPolicyAgent()
