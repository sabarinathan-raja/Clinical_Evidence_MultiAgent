
class SafetyValidator:

    def validate(self, report: dict, evidence: list) -> dict:

        issues = []

        if not report.get("executive_summary"):
            issues.append(
                "Executive summary is missing."
            )

        if not evidence and report.get("findings"):
            issues.append(
                "Report contains findings without retrieved evidence."
            )

        for index, finding in enumerate(
            report.get("findings", [])
        ):

            if not finding.get("citation_ids"):
                issues.append(
                    f"Finding {index + 1} has no citation."
                )

        if report.get("review_status") == "approved":
            issues.append(
                "Approval status must only be assigned through "
                "the authorized human review workflow."
            )

        return {
            "is_safe": len(issues) == 0,
            "requires_human_review": True,
            "issues": issues,
            "disclaimer": (
                "This output is research assistance and requires "
                "qualified human clinical review."
            )
        }


safety_validator = SafetyValidator()
