
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.repositories import (
    CaseRepository,
    WorkflowRepository
)
from backend.api.auth import get_current_user
from backend.graph.orchestrator import clinical_orchestrator


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/workflows",
    tags=["AI Workflows"]
)


# --------------------------------------------------
# RUN AI WORKFLOW
# --------------------------------------------------

@router.post("/{case_id}/run")
def run_workflow(
    case_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    case = CaseRepository(db).get(case_id)

    if not case or case.created_by != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    repository = WorkflowRepository(db)

    # Create workflow record before execution
    workflow = repository.create(
        case_id=case.id,
        status="running",
        result={}
    )

    try:

        result = clinical_orchestrator.run(
            clinical_question=case.clinical_question,
            patient_context=case.patient_context or {},
            case_id=case.id,
            title=case.title,
            thread_id=workflow.id
        )

        if not isinstance(result, dict):
            raise ValueError(
                "Invalid workflow result returned by orchestrator."
            )

        # Store workflow identifiers in the result
        result["workflow_id"] = workflow.id
        result["thread_id"] = workflow.id
        result["case_id"] = case.id

        # Update saved workflow record
        repository.update(
            workflow.id,
            status=result.get("status", "completed"),
            current_node=result.get("current_node"),
            result=result
        )

        # Update case status
        CaseRepository(db).update(
            case.id,
            status=result.get("status", "completed")
        )

        return {
            "success": True,
            "data": result
        }

    except Exception:

        logger.exception(
            "Clinical workflow execution failed for case %s",
            case_id
        )

        repository.update(
            workflow.id,
            status="failed",
            error_message="Workflow execution failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to execute clinical workflow."
        )


# --------------------------------------------------
# LIST SAVED WORKFLOWS
# --------------------------------------------------

@router.get("/")
def list_workflows(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    repository = WorkflowRepository(db)

    # Admin, reviewer and clinician can view all workflows
    if current_user.role in {
        "admin",
        "reviewer",
        "clinician"
    }:
        workflows = repository.list_all()

    else:
        # Normal users can view only their own workflows
        workflows = repository.list_by_user(
            current_user.id
        )

    return {
        "success": True,
        "data": [
            {
                "workflow_id": workflow.id,
                "case_id": workflow.case_id,
                "status": workflow.status,
                "current_node": workflow.current_node,
                "started_at": (
                    workflow.started_at.isoformat()
                    if workflow.started_at
                    else None
                )
            }
            for workflow in workflows
        ]
    }


# --------------------------------------------------
# GET WORKFLOW DETAILS BY ID
# --------------------------------------------------

@router.get("/{workflow_id}")
def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    workflow = WorkflowRepository(db).get(
        workflow_id
    )

    if not workflow:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found."
        )

    case = CaseRepository(db).get(
        workflow.case_id
    )

    if not case or (
        case.created_by != current_user.id
        and current_user.role not in {
            "admin",
            "reviewer",
            "clinician"
        }
    ):
        raise HTTPException(
            status_code=404,
            detail="Workflow not found."
        )

    return {
        "success": True,
        "data": {
            "workflow_id": workflow.id,
            "case_id": workflow.case_id,
            "status": workflow.status,
            "current_node": workflow.current_node,
            "started_at": (
                workflow.started_at.isoformat()
                if workflow.started_at
                else None
            ),
            "completed_at": (
                workflow.completed_at.isoformat()
                if workflow.completed_at
                else None
            ),
            "error_message": workflow.error_message,
            "result": workflow.result or {}
        }
    }
