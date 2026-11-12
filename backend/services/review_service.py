
import logging

from langgraph.types import interrupt

logger = logging.getLogger(__name__)


def approval_checks(state):

    validation = state.get("validation_result", {})
    safety = state.get("safety_result", {})

    if not isinstance(validation, dict):
        validation = {}

    if not isinstance(safety, dict):
        safety = {}

    validation_passed = all([
        validation.get("is_valid") is True,
        validation.get("schema_valid") is True,
        validation.get("citation_valid") is True,
        validation.get("groundedness_valid") is True,
        validation.get("safety_valid") is True
    ])

    safety_passed = (
        safety.get("is_safe") is True
        and safety.get("safety_level") != "blocked"
        and state.get("safety_blocked") is not True
    )

    return validation_passed and safety_passed


def human_review_node(state):

    validation = state.get("validation_result", {})
    report = state.get("report", {})

    if not isinstance(validation, dict):
        validation = {}

    if not isinstance(report, dict):
        report = {}

    can_approve = approval_checks(state)

    allowed_decisions = [
        "rejected",
        "revision_required"
    ]

    if can_approve:
        allowed_decisions.insert(0, "approved")

    review_payload = {
        "workflow_id": state.get("workflow_id"),
        "case_id": state.get("case_id"),
        "title": report.get("title"),
        "executive_summary": report.get(
            "executive_summary", ""
        ),
        "validation": validation,
        "safety": state.get("safety_result", {}),
        "allowed_decisions": allowed_decisions,
        "approval_allowed": can_approve
    }

    decision = interrupt(review_payload)

    if not isinstance(decision, dict):
        raise ValueError(
            "A valid human review decision is required."
        )

    raw_action = decision.get("decision")

    if not isinstance(raw_action, str):
        raise ValueError("Review decision must be a string.")

    action = raw_action.strip().lower()

    comments = decision.get("comments", "")

    if not isinstance(comments, str):
        raise ValueError("Review comments must be a string.")

    if action not in {
        "approved",
        "rejected",
        "revision_required"
    }:
        raise ValueError("Invalid review decision.")

    # Never allow approval when validation or safety checks fail.
    if action == "approved" and not approval_checks(state):
        raise ValueError(
            "Cannot approve a report that failed validation "
            "or was not explicitly cleared by the safety policy."
        )

    report = dict(report)

    if action == "approved":
        status = "approved"
        success = True

    elif action == "rejected":
        status = "rejected"
        success = False

    else:
        status = "revision_required"
        success = False

    report["review_status"] = status

    return {
        "report": report,
        "review_decision": action,
        "review_required": False,
        "review_comments": comments,
        "status": status,
        "success": success,
        "current_node": "human_review",
        "final_result": {
            "report": report,
            "validation": validation,
            "review": {
                "decision": action,
                "comments": comments
            },
            "safety": state.get("safety_result", {})
        }
    }


class ReviewService:

    VALID_DECISIONS = {
        "approved",
        "rejected",
        "revision_required"
    }

    def process_decision(
        self,
        workflow_id: str,
        decision: str,
        comments: str,
        reviewer_id: str
    ) -> dict:

        if not isinstance(decision, str):
            raise ValueError(
                "Review decision must be a string."
            )

        decision = decision.strip().lower()

        if decision not in self.VALID_DECISIONS:
            raise ValueError(
                "Unsupported human review decision."
            )

        if not workflow_id or not reviewer_id:
            raise ValueError(
                "Workflow and reviewer identifiers are required."
            )

        if not isinstance(comments, str):
            raise ValueError(
                "Review comments must be a string."
            )

        from backend.graph.orchestrator import (
            clinical_orchestrator
        )

        result = clinical_orchestrator.resume_review(
            workflow_id=workflow_id,
            decision=decision,
            comments=comments,
            reviewer_id=reviewer_id
        )

        return result


review_service = ReviewService()
