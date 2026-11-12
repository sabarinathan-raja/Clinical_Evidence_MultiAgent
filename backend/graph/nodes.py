
import logging
from datetime import datetime, timezone

from backend.agents import (
    intake_scope_agent,
    patient_context_agent,
    evidence_retrieval_agent,
    evidence_quality_agent,
    safety_policy_agent,
    summary_generation_agent,
    output_validation_agent,
)

logger = logging.getLogger(__name__)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def add_completed(state, name):
    completed = list(state.get("completed_agents", []))

    if name not in completed:
        completed.append(name)

    return completed


def add_warnings(state, warnings):
    return list(state.get("warnings", [])) + list(warnings or [])


def add_errors(state, error):
    return list(state.get("errors", [])) + [str(error)]


def intake_node(state):

    logger.info("Executing Intake Scope Agent")

    result = intake_scope_agent.run({
        "clinical_question": state.get(
            "clinical_question", ""
        ),
        "title": state.get("title"),
        "research_scope": state.get("research_scope")
    })

    return {
        "intake_result": result,
        "current_node": "intake",
        "status": "intake_completed",
        "completed_agents": add_completed(
            state, "intake_scope_agent"
        ),
        "warnings": add_warnings(
            state, result.get("warnings")
        )
    }


def patient_context_node(state):

    logger.info("Executing Patient Context Agent")

    context = state.get("patient_context", {})

    result = patient_context_agent.run(context)

    return {
        "deidentified_patient_context": (
            result["patient_context"]
        ),
        "current_node": "patient_context",
        "status": "patient_context_completed",
        "completed_agents": add_completed(
            state, "patient_context_agent"
        ),
        "warnings": add_warnings(
            state, result.get("warnings")
        )
    }


def evidence_retrieval_node(state):

    logger.info("Executing Evidence Retrieval Agent")

    question = state.get(
        "intake_result", {}
    ).get(
        "normalized_question",
        state.get("clinical_question", "")
    )

    result = evidence_retrieval_agent.run(
        query=question,
        top_k=5
    )

    return {
        "retrieval_result": result,
        "evidence": result.get("evidence", []),
        "citations": result.get("citations", []),
        "evidence_context": result.get("context", ""),
        "current_node": "evidence_retrieval",
        "status": "retrieval_completed",
        "completed_agents": add_completed(
            state, "evidence_retrieval_agent"
        ),
        "warnings": add_warnings(
            state, result.get("warnings")
        )
    }


def evidence_quality_node(state):

    logger.info("Executing Evidence Quality Agent")

    result = evidence_quality_agent.run(
        state.get("evidence", [])
    )

    return {
        "evidence_quality": result,
        "current_node": "evidence_quality",
        "status": "quality_assessed",
        "completed_agents": add_completed(
            state, "evidence_quality_agent"
        ),
        "warnings": add_warnings(
            state, result.get("warnings")
        )
    }


def safety_policy_node(state):

    logger.info("Executing Safety Policy Agent")

    result = safety_policy_agent.run(
        question=state.get("clinical_question", ""),
        context=state.get(
            "deidentified_patient_context", {}
        ),
        evidence=state.get("evidence", [])
    )

    blocked = result.get("safety_level") == "blocked"

    return {
        "safety_result": result,
        "safety_blocked": blocked,
        "current_node": "safety_policy",
        "status": (
            "safety_blocked"
            if blocked
            else "safety_checked"
        ),
        "completed_agents": add_completed(
            state, "safety_policy_agent"
        ),
        "warnings": add_warnings(
            state,
            [
                item.get("message", "")
                for item in result.get("findings", [])
            ]
        )
    }


def safety_block_node(state):

    logger.warning(
        "Workflow stopped due to safety policy."
    )

    report = {
        "title": state.get("title", "Clinical Evidence Report"),
        "clinical_question": state.get(
            "clinical_question", ""
        ),
        "executive_summary": (
            "Automated summary generation was blocked "
            "by the safety policy."
        ),
        "background": "",
        "findings": [],
        "evidence_limitations": [
            "The request requires additional human assessment."
        ],
        "safety_notes": [
            item.get("message", "")
            for item in state.get(
                "safety_result", {}
            ).get("findings", [])
        ],
        "citations": [],
        "conclusion": (
            "No automated clinical conclusion was generated."
        ),
        "review_status": "pending"
    }

    return {
        "report": report,
        "current_node": "safety_block",
        "status": "review_pending",
        "review_required": True,
        "success": False,
        "completed_agents": add_completed(
            state, "safety_block_node"
        )
    }



def summary_generation_node(state):

    logger.info("Executing Summary Generation Agent")

    # Read reviewer comments during a revision cycle.
    revision_comments = state.get("review_comments", "")

    result = summary_generation_agent.run(
        question=state.get("clinical_question", ""),
        context=state.get("evidence_context", ""),
        citations=state.get("citations", []),
        safety=state.get("safety_result", {}),
        revision_comments=revision_comments
    )

    findings = result.get("findings", [])

    retrieved_citations = state.get("citations", [])

    if not isinstance(retrieved_citations, list):
        retrieved_citations = []

    used_citation_ids = set()

    if isinstance(findings, list):
        for finding in findings:

            if not isinstance(finding, dict):
                continue

            citation_ids = finding.get("citation_ids", [])

            if isinstance(citation_ids, list):
                for citation_id in citation_ids:
                    if isinstance(citation_id, str):
                        used_citation_ids.add(
                            citation_id.strip()
                        )

    verified_report_citations = []

    for citation in retrieved_citations:

        if not isinstance(citation, dict):
            continue

        citation_id = citation.get("citation_id")

        if (
            isinstance(citation_id, str)
            and citation_id.strip() in used_citation_ids
        ):
            verified_report_citations.append(citation)

    report = {
        "title": state.get(
            "title", "Clinical Evidence Report"
        ),
        "clinical_question": state.get(
            "clinical_question", ""
        ),
        "executive_summary": result.get(
            "executive_summary", ""
        ),
        "background": result.get("background", ""),
        "findings": findings,
        "evidence_limitations": result.get(
            "evidence_limitations",
            result.get("limitations", [])
        ),
        "safety_notes": result.get("safety_notes", []),
        "citations": verified_report_citations,
        "conclusion": result.get("conclusion", ""),
        "review_status": "pending"
    }

    current_revision = state.get("revision_count", 0)

    return {
        "summary_result": result,
        "report": report,
        "review_comments": "",
        "current_node": "summary_generation",
        "status": "summary_generated",
        "review_required": True,
        "completed_agents": add_completed(
            state, "summary_generation_agent"
        ),
        "warnings": add_warnings(
            state,
            result.get("evidence_limitations", [])
        )
    }



def output_validation_node(state):

    logger.info("Executing Output Validation Agent")

    report = state.get("report", {})
    allowed_citations = state.get("citations", [])

    result = output_validation_agent.run(
        report=report,
        allowed_citations=allowed_citations
    )

    # Read the Safety Policy Agent result.
    safety_result = state.get("safety_result", {})

    if not isinstance(safety_result, dict):
        safety_result = {}

    safety_confirmed = (
        safety_result.get("is_safe") is True
        and safety_result.get("safety_level") != "blocked"
        and not state.get("safety_blocked", False)
    )

    # Safety validation must not automatically pass.
    result["safety_valid"] = safety_confirmed

    if not safety_confirmed:

        result["is_valid"] = False

        result.setdefault("issues", []).append({
            "category": "safety_policy_not_confirmed",
            "message": (
                "Safety Policy Agent did not explicitly confirm "
                "that the request is safe."
            ),
            "severity": "error",
            "reference": None
        })

    success = (
        result.get("is_valid", False)
        and result.get("schema_valid", False)
        and result.get("citation_valid", False)
        and result.get("groundedness_valid", False)
        and result.get("safety_valid", False)
        and not state.get("safety_blocked", False)
    )

    return {
        "validation_result": result,
        "current_node": "output_validation",
        "status": "review_pending",
        "review_required": True,
        "success": success,
        "final_result": {
            "report": report,
            "validation": result,
            "safety": safety_result,
            "evidence_quality": state.get(
                "evidence_quality", {}
            ),
            "review_required": True
        },
        "completed_agents": add_completed(
            state, "output_validation_agent"
        ),
        "warnings": add_warnings(
            state,
            result.get("warnings", [])
        )
    }




def error_node(state):

    logger.error("Workflow entered error state.")

    return {
        "status": "failed",
        "success": False,
        "current_node": "error",
        "errors": add_errors(
            state,
            "Workflow execution failed."
        )
    }
