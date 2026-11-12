
import logging
import uuid

from datetime import datetime, timezone

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from backend.graph.state import ClinicalEvidenceState

from backend.graph.nodes import (
    intake_node,
    patient_context_node,
    evidence_retrieval_node,
    evidence_quality_node,
    safety_policy_node,
    safety_block_node,
    summary_generation_node,
    output_validation_node
)

from backend.graph.edges import route_after_safety
from backend.graph.checkpoints import checkpoint_manager
from backend.services.review_service import human_review_node

logger = logging.getLogger(__name__)


class ClinicalEvidenceOrchestrator:

    def __init__(self):
        self.graph = None
        self.checkpointer = checkpoint_manager.initialize()
        self.active_workflows = {}

    def build_graph(self):

        if self.graph is not None:
            return self.graph

        workflow = StateGraph(ClinicalEvidenceState)

        nodes = {
            "intake": intake_node,
            "patient_context": patient_context_node,
            "evidence_retrieval": evidence_retrieval_node,
            "evidence_quality": evidence_quality_node,
            "safety_policy": safety_policy_node,
            "safety_block": safety_block_node,
            "summary_generation": summary_generation_node,
            "output_validation": output_validation_node,
            "human_review": human_review_node,
        }

        for name, function in nodes.items():
            workflow.add_node(name, function)

        workflow.add_edge(START, "intake")
        workflow.add_edge("intake", "patient_context")
        workflow.add_edge("patient_context", "evidence_retrieval")
        workflow.add_edge("evidence_retrieval", "evidence_quality")
        workflow.add_edge("evidence_quality", "safety_policy")

        workflow.add_conditional_edges(
            "safety_policy",
            route_after_safety,
            {
                "safety_block": "safety_block",
                "summary_generation": "summary_generation"
            }
        )

        workflow.add_edge("safety_block", "output_validation")
        workflow.add_edge("summary_generation", "output_validation")
        workflow.add_edge("output_validation", "human_review")
        workflow.add_edge("human_review", END)

        self.graph = workflow.compile(
            checkpointer=self.checkpointer
        )

        logger.info("Clinical evidence graph compiled.")

        return self.graph

    def run(
        self,
        clinical_question,
        patient_context=None,
        case_id=None,
        title="Clinical Evidence Research",
        research_scope=None,
        thread_id=None
    ):

        if not clinical_question or len(
            clinical_question.strip()
        ) < 10:
            raise ValueError("Invalid clinical question.")

        graph = self.build_graph()

        # Database workflow ID and graph thread ID must match.
        workflow_id = thread_id or str(uuid.uuid4())
        thread_id = workflow_id

        initial_state: ClinicalEvidenceState = {
            "case_id": case_id or "",
            "workflow_id": workflow_id,
            "thread_id": thread_id,
            "clinical_question": clinical_question,
            "title": title,
            "research_scope": research_scope or "",
            "patient_context": patient_context or {},
            "deidentified_patient_context": {},
            "intake_result": {},
            "retrieval_result": {},
            "evidence": [],
            "citations": [],
            "evidence_context": "",
            "evidence_quality": {},
            "safety_result": {},
            "safety_blocked": False,
            "summary_result": {},
            "report": {},
            "validation_result": {},
            "status": "pending",
            "current_node": "start",
            "completed_agents": [],
            "warnings": [],
            "errors": [],
            "review_required": True,
            "review_decision": None,
            "review_comments": "",
            "success": False,
            "final_result": {},
            "started_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        config = checkpoint_manager.get_config(thread_id)

        result = graph.invoke(
            initial_state,
            config=config
        )

        self.active_workflows[workflow_id] = {
            "thread_id": thread_id,
            "case_id": case_id,
            "status": result.get("status", "review_pending")
        }

        return self._format_result(
            result,
            workflow_id,
            thread_id
        )

    
    def resume_review(
        self,
        workflow_id,
        decision,
        comments="",
        reviewer_id=None
    ):

        if not workflow_id:
            raise ValueError("Workflow ID is required.")

        # In this project, workflow_id and thread_id are identical.
        thread_id = str(workflow_id)

        graph = self.build_graph()

        config = checkpoint_manager.get_config(thread_id)

        # Recover workflow state from persistent checkpoint storage.
        snapshot = graph.get_state(config)

        if not snapshot or not snapshot.values:
            raise ValueError(
                "Workflow checkpoint not found. "
                "Check the workflow ID and checkpoint database."
            )

        # A completed workflow cannot be resumed.
        if not snapshot.next:
            raise ValueError(
                "This workflow has already completed."
            )

        # Ensure the workflow is waiting at the human review node.
        if "human_review" not in snapshot.next:
            raise ValueError(
                "Workflow is not waiting for human review."
            )

        result = graph.invoke(
            Command(
                resume={
                    "decision": decision,
                    "comments": comments,
                    "reviewer_id": reviewer_id
                }
            ),
            config=config
        )

        self.active_workflows[thread_id] = {
            "thread_id": thread_id,
            "case_id": result.get("case_id"),
            "status": result.get("status")
        }

        return self._format_result(
            result,
            workflow_id,
            thread_id
        )


    
    @staticmethod
    def _format_result(result, workflow_id, thread_id):

        interrupts = result.get("__interrupt__", [])

        return {
            "success": result.get("success", False),
            "workflow_id": workflow_id,
            "thread_id": thread_id,
            "case_id": result.get("case_id"),
            "status": result.get("status", "review_pending"),
            "current_node": result.get("current_node"),
            "completed_agents": result.get("completed_agents", []),
            "report": result.get("report", {}),
            "validation": result.get("validation_result", {}),
            "evidence_quality": result.get("evidence_quality", {}),
            "safety": result.get("safety_result", {}),
            "review_required": result.get("review_required", True),
            "review_decision": result.get("review_decision"),
            "warnings": result.get("warnings", []),
            "errors": result.get("errors", []),
            "interrupts": [
                item.value for item in interrupts
            ],
            "final_result": result.get("final_result", {})
        }


clinical_orchestrator = ClinicalEvidenceOrchestrator()
