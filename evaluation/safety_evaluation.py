
def evaluate_safety(
    report,
    safety_result,
    validation_result
):

    issues = []

    if not safety_result:
        issues.append(
            "Safety evaluation result is missing."
        )

    if not validation_result:
        issues.append(
            "Output validation result is missing."
        )

    blocked = (
        safety_result.get("safety_level") == "blocked"
    )

    if blocked and report.get("review_status") == "approved":
        issues.append(
            "Blocked output must not be approved."
        )

    if report.get("review_status") == "approved":
        if not validation_result.get("is_valid"):
            issues.append(
                "Invalid output cannot be approved."
            )

    return {
        "is_safe": len(issues) == 0,
        "issues": issues,
        "requires_human_review": True
    }
