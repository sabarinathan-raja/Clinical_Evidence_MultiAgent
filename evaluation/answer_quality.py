
def evaluate_answer_quality(
    report,
    expected_keywords=None
):

    expected_keywords = expected_keywords or []

    summary = report.get(
        "executive_summary", ""
    )

    findings = report.get("findings", [])

    limitations = report.get(
        "evidence_limitations", []
    )

    checks = {
        "summary_present": bool(summary.strip()),
        "findings_present": bool(findings),
        "limitations_present": bool(limitations),
        "citations_present": any(
            item.get("citation_ids")
            for item in findings
        )
    }

    text = summary.lower()

    keyword_matches = sum(
        1 for keyword in expected_keywords
        if keyword.lower() in text
    )

    keyword_score = (
        keyword_matches / len(expected_keywords)
        if expected_keywords else None
    )

    score = (
        sum(checks.values()) / len(checks)
    )

    return {
        "structural_score": round(score, 4),
        "checks": checks,
        "keyword_score": (
            round(keyword_score, 4)
            if keyword_score is not None
            else None
        ),
        "limitations_count": len(limitations)
    }
