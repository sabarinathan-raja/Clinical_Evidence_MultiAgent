
def evaluate_citations(
    report,
    allowed_citations
):

    allowed = {
        item.get("citation_id")
        for item in allowed_citations
    }

    used = set()
    invalid = []
    uncited = []

    findings = report.get("findings", [])

    for index, finding in enumerate(findings):

        citations = finding.get(
            "citation_ids", []
        )

        if not citations:
            uncited.append(index)

        for citation in citations:

            used.add(citation)

            if citation not in allowed:
                invalid.append(citation)

    valid_used = used & allowed

    accuracy = (
        len(valid_used) / len(used)
        if used else 0.0
    )

    coverage = (
        (len(findings) - len(uncited)) / len(findings)
        if findings else 0.0
    )

    return {
        "citation_accuracy": accuracy,
        "citation_coverage": coverage,
        "invalid_citations": list(set(invalid)),
        "uncited_findings": uncited,
        "is_valid": len(invalid) == 0
    }
