
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.repositories import (
    WorkflowRepository,
    CaseRepository
)

from backend.api.auth import get_current_user

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/{workflow_id}")
def get_report(
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
            detail="Report not found."
        )

    case = CaseRepository(db).get(workflow.case_id)

    if not case or (
        case.created_by != current_user.id
        and current_user.role not in {
            "admin", "reviewer", "clinician"
        }
    ):
        raise HTTPException(
            status_code=404,
            detail="Report not found."
        )

    result = workflow.result or {}

    report = result.get("report")

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report has not been generated."
        )

    return {
        "success": True,
        "workflow_id": workflow.id,
        "case_id": workflow.case_id,
        "status": workflow.status,
        "review_status": report.get(
            "review_status", "pending"
        ),
        "report": report,
        "validation": result.get("validation", {}),
        "safety": result.get("safety", {})
    }


@router.get("/case/{case_id}/history")
def report_history(
    case_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    case = CaseRepository(db).get(case_id)

    if not case or (
        case.created_by != current_user.id
        and current_user.role not in {
            "admin", "reviewer", "clinician"
        }
    ):
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    workflows = case.workflows

    return {
        "success": True,
        "total": len(workflows),
        "reports": [
            {
                "workflow_id": item.id,
                "status": item.status,
                "report": (
                    item.result or {}
                ).get("report")
            }
            for item in workflows
        ]
    }
