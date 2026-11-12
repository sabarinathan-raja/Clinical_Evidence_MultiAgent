
from typing import Any

from backend.models.validation_schema import (
    ValidationResult,
    ValidationIssue
)


class OutputValidationAgent:

    REQUIRED_FIELDS = [
        "executive_summary",
        "findings",
        "evidence_limitations"
    ]

    def run(
        self,
        report: dict,
        allowed_citations: list[dict]
    ) -> dict:

        issues = []
        missing_citations = []

        if not isinstance(report, dict):
            return ValidationResult(
                is_valid=False,
                schema_valid=False,
                citation_valid=False,
                groundedness_valid=False,
                safety_valid=False,
                issues=[
                    ValidationIssue(
                        category="invalid_report",
                        message="Report must be a JSON object.",
                        severity="error"
                    )
                ],
                missing_citations=[]
            ).model_dump()

        allowed_citations = (
            allowed_citations
            if isinstance(allowed_citations, list)
            else []
        )

        # Build the authoritative citation lookup from
        # the evidence retrieval/context-building pipeline.
        allowed_map = {}

        for item in allowed_citations:
            if not isinstance(item, dict):
                continue

            citation_id = item.get("citation_id")

            if citation_id:
                allowed_map[str(citation_id).strip()] = item

        allowed_ids = set(allowed_map.keys())

        # 1. Required fields
        for field in self.REQUIRED_FIELDS:
            if field not in report:
                issues.append(
                    ValidationIssue(
                        category="missing_field",
                        message=f"Missing required field: {field}",
                        severity="error"
                    )
                )

        # 2. Field types
        if (
            "executive_summary" in report
            and not isinstance(report["executive_summary"], str)
        ):
            issues.append(
                ValidationIssue(
                    category="invalid_field_type",
                    message="executive_summary must be a string.",
                    severity="error"
                )
            )

        if (
            "findings" in report
            and not isinstance(report["findings"], list)
        ):
            issues.append(
                ValidationIssue(
                    category="invalid_field_type",
                    message="findings must be a list.",
                    severity="error"
                )
            )

        if (
            "evidence_limitations" in report
            and not isinstance(report["evidence_limitations"], list)
        ):
            issues.append(
                ValidationIssue(
                    category="invalid_field_type",
                    message="evidence_limitations must be a list.",
                    severity="error"
                )
            )

        # 3. Validate report citation records
        report_citations = report.get("citations", [])

        if not isinstance(report_citations, list):
            issues.append(
                ValidationIssue(
                    category="invalid_citation_format",
                    message="Report citations must be a list.",
                    severity="error"
                )
            )
            report_citations = []

        report_citation_map = {}

        for index, citation in enumerate(report_citations):

            if not isinstance(citation, dict):
                issues.append(
                    ValidationIssue(
                        category="invalid_citation_record",
                        message=(
                            f"Citation record {index + 1} "
                            "must be an object."
                        ),
                        severity="error"
                    )
                )
                continue

            citation_id = citation.get("citation_id")

            if not isinstance(citation_id, str) or not citation_id.strip():
                issues.append(
                    ValidationIssue(
                        category="invalid_citation_record",
                        message=(
                            f"Citation record {index + 1} "
                            "has no valid citation_id."
                        ),
                        severity="error"
                    )
                )
                continue

            citation_id = citation_id.strip()

            if citation_id in report_citation_map:
                issues.append(
                    ValidationIssue(
                        category="duplicate_citation",
                        message=f"Duplicate citation ID: {citation_id}",
                        severity="error"
                    )
                )
                continue

            report_citation_map[citation_id] = citation

            if citation_id not in allowed_map:
                issues.append(
                    ValidationIssue(
                        category="invalid_citation",
                        message=(
                            f"Citation {citation_id} "
                            "does not exist in retrieved evidence."
                        ),
                        severity="error"
                    )
                )
                continue

            original = allowed_map[citation_id]

            # Source verification
            report_source = citation.get("source")
            original_source = original.get("source")

            if not report_source or not original_source:
                issues.append(
                    ValidationIssue(
                        category="incomplete_citation_metadata",
                        message=(
                            f"Citation {citation_id} "
                            "has missing source metadata."
                        ),
                        severity="error"
                    )
                )
            elif str(report_source).strip() != str(original_source).strip():
                issues.append(
                    ValidationIssue(
                        category="citation_source_mismatch",
                        message=(
                            f"Citation {citation_id} source "
                            "does not match retrieved evidence."
                        ),
                        severity="error"
                    )
                )

            # Page verification. Page 0 is valid.
            report_page = citation.get("page")
            original_page = original.get("page")

            if report_page is None or original_page is None:
                issues.append(
                    ValidationIssue(
                        category="incomplete_citation_metadata",
                        message=(
                            f"Citation {citation_id} "
                            "has missing page metadata."
                        ),
                        severity="error"
                    )
                )
            elif str(report_page).strip() != str(original_page).strip():
                issues.append(
                    ValidationIssue(
                        category="citation_page_mismatch",
                        message=(
                            f"Citation {citation_id} page "
                            "does not match retrieved evidence."
                        ),
                        severity="error"
                    )
                )

            # Chunk ID verification
            report_chunk = citation.get("chunk_id")
            original_chunk = original.get("chunk_id")

            if not report_chunk or not original_chunk:
                issues.append(
                    ValidationIssue(
                        category="incomplete_citation_metadata",
                        message=(
                            f"Citation {citation_id} "
                            "has missing chunk ID."
                        ),
                        severity="error"
                    )
                )
            elif str(report_chunk).strip() != str(original_chunk).strip():
                issues.append(
                    ValidationIssue(
                        category="citation_chunk_mismatch",
                        message=(
                            f"Citation {citation_id} chunk ID "
                            "does not match retrieved evidence."
                        ),
                        severity="error"
                    )
                )

        # 4. Validate findings
        findings = report.get("findings", [])

        if isinstance(findings, list):

            if not findings:
                issues.append(
                    ValidationIssue(
                        category="empty_findings",
                        message=(
                            "No supported findings were generated. "
                            "Check retrieved evidence and summary generation."
                        ),
                        severity="error"
                    )
                )

            for index, finding in enumerate(findings):

                if not isinstance(finding, dict):
                    issues.append(
                        ValidationIssue(
                            category="invalid_finding",
                            message=(
                                f"Finding {index + 1} must be an object."
                            ),
                            severity="error"
                        )
                    )
                    continue

                for key in ["heading", "content", "citation_ids"]:
                    if key not in finding:
                        issues.append(
                            ValidationIssue(
                                category="missing_finding_field",
                                message=(
                                    f"Finding {index + 1} "
                                    f"is missing {key}."
                                ),
                                severity="error"
                            )
                        )

                heading = finding.get("heading")
                content = finding.get("content")
                citation_ids = finding.get("citation_ids", [])

                if not isinstance(heading, str) or not heading.strip():
                    issues.append(
                        ValidationIssue(
                            category="invalid_finding",
                            message=(
                                f"Finding {index + 1} "
                                "has an empty or invalid heading."
                            ),
                            severity="error"
                        )
                    )

                if not isinstance(content, str) or not content.strip():
                    issues.append(
                        ValidationIssue(
                            category="invalid_finding",
                            message=(
                                f"Finding {index + 1} "
                                "has empty or invalid content."
                            ),
                            severity="error"
                        )
                    )

                if not isinstance(citation_ids, list):
                    issues.append(
                        ValidationIssue(
                            category="invalid_citation_format",
                            message=(
                                f"Finding {index + 1} "
                                "citation_ids must be a list."
                            ),
                            severity="error"
                        )
                    )
                    continue

                if not citation_ids:
                    missing_citations.append(
                        f"finding_{index + 1}"
                    )

                    issues.append(
                        ValidationIssue(
                            category="missing_citation",
                            message=(
                                f"Finding {index + 1} "
                                "has no supporting citation."
                            ),
                            severity="error"
                        )
                    )

                for citation_id in citation_ids:

                    if not isinstance(citation_id, str):
                        issues.append(
                            ValidationIssue(
                                category="invalid_citation",
                                message=(
                                    f"Finding {index + 1} "
                                    "contains a non-string citation ID."
                                ),
                                severity="error"
                            )
                        )
                        continue

                    citation_id = citation_id.strip()

                    if citation_id not in allowed_ids:
                        issues.append(
                            ValidationIssue(
                                category="invalid_citation",
                                message=(
                                    f"Unknown citation: {citation_id}"
                                ),
                                severity="error"
                            )
                        )

                    elif citation_id not in report_citation_map:
                        issues.append(
                            ValidationIssue(
                                category="missing_citation_record",
                                message=(
                                    f"Citation {citation_id} is allowed "
                                    "but missing from report citations."
                                ),
                                severity="error"
                            )
                        )

        # 5. Validation result categories
        schema_categories = {
            "missing_field",
            "invalid_field_type",
            "invalid_finding",
            "missing_finding_field",
            "invalid_citation_format",
            "empty_findings"
        }

        citation_categories = {
            "invalid_citation",
            "duplicate_citation",
            "invalid_citation_record",
            "incomplete_citation_metadata",
            "citation_source_mismatch",
            "citation_page_mismatch",
            "citation_chunk_mismatch",
            "missing_citation_record"
        }

        schema_error = any(
            issue.severity == "error"
            and issue.category in schema_categories
            for issue in issues
        )

        citation_error = any(
            issue.severity == "error"
            and issue.category in citation_categories
            for issue in issues
        )

        groundedness_error = (
            bool(missing_citations)
            or citation_error
        )

        has_errors = any(
            issue.severity == "error"
            for issue in issues
        )

        # Safety is not independently assessed by this validator.
        # The graph's safety policy result must be checked separately.
        result = ValidationResult(
            is_valid=not has_errors,
            schema_valid=not schema_error,
            citation_valid=not citation_error,
            groundedness_valid=not groundedness_error,
            safety_valid=True,
            issues=issues,
            missing_citations=missing_citations
        )

        return result.model_dump()

    def validate_citations(
        self,
        report: dict,
        allowed_citations: list[dict]
    ) -> bool:

        result = self.run(report, allowed_citations)

        return result["citation_valid"]


output_validation_agent = OutputValidationAgent()
