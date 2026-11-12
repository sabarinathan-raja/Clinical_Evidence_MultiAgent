
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.database.repositories import (
    ReviewRepository,
    WorkflowRepository,
    CaseRepository
)

from backend.models.validation_schema import ReviewRequest
from backend.api.auth import get_current_user
from backend.services.review_service import review_service

router = APIRouter(
    prefix="/reviews",
    tags=["Human Reviews"]
)


@router.post("/{workflow_id}/decision")
def submit_review(
    workflow_id: str,
    request: ReviewRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.role not in {
        "reviewer", "admin", "clinician"
    }:
        raise HTTPException(
            status_code=403,
            detail="Review authorization required."
        )

    decision = request.decision.lower()

    if decision not in {
        "approved", "rejected", "revision_required"
    }:
        raise HTTPException(
            status_code=400,
            detail="Invalid review decision."
        )

    workflow_repo = WorkflowRepository(db)

    workflow = workflow_repo.get(workflow_id)

    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found."
        )

    case = CaseRepository(db).get(workflow.case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    if (
        case.created_by != current_user.id
        and current_user.role not in {
            "admin", "reviewer", "clinician"
        }
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized."
        )

    if workflow.status != "review_pending":
        raise HTTPException(
            status_code=409,
            detail="Workflow is not awaiting review."
        )

    try:

        result = review_service.process_decision(
            workflow_id=workflow_id,
            decision=decision,
            comments=request.comments,
            reviewer_id=current_user.id
        )

        ReviewRepository(db).create(
            case_id=workflow.case_id,
            workflow_id=workflow_id,
            reviewer_id=current_user.id,
            decision=decision,
            comments=request.comments
        )

        workflow_repo.update(
            workflow_id,
            status=result["status"],
            current_node=result.get("current_node"),
            result=result
        )

        CaseRepository(db).update(
            workflow.case_id,
            status=result["status"]
        )

        return {
            "success": True,
            "message": "Review decision recorded.",
            "data": result
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to process review."
        )
