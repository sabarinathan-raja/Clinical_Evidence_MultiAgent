from __future__ import annotations

from backend.database.repositories import repository
from backend.graph.orchestrator import EvidenceWorkflow
from backend.models.schemas import QueryCreate, ResearchBrief


def execute_query(query: QueryCreate) -> ResearchBrief:
    report = EvidenceWorkflow().run(query)
    repository.save_report(report.model_dump(mode="json"))
    repository.audit("workflow_completed", {"query_id": report.query_id, "requires_human_review": report.requires_human_review})
    return report
