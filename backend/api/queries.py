
from fastapi import APIRouter, Depends, HTTPException

from backend.api.auth import get_current_user
from backend.models.intake_schema import IntakeRequest
from backend.agents.intake_scope_agent import intake_scope_agent

router = APIRouter(
    prefix="/queries",
    tags=["Clinical Queries"]
)


@router.post("/analyze")
def analyze_query(
    request: IntakeRequest,
    current_user=Depends(get_current_user)
):

    try:

        result = intake_scope_agent.run(
            request.model_dump()
        )

        return {
            "success": True,
            "message": "Clinical question analyzed.",
            "data": result
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Question analysis failed."
        )
