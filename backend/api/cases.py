
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.repositories import CaseRepository
from backend.api.auth import get_current_user
from backend.models.schemas import CaseCreateRequest

router = APIRouter(
    prefix="/cases",
    tags=["Clinical Cases"]
)


def serialize_case(case):

    return {
        "id": case.id,
        "title": case.title,
        "clinical_question": case.clinical_question,
        "status": case.status,
        "created_by": case.created_by,
        "created_at": case.created_at
    }


@router.post("/")
def create_case(
    request: CaseCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    case = CaseRepository(db).create(
        title=request.title,
        clinical_question=request.clinical_question,
        patient_context=request.patient_context,
        created_by=current_user.id,
        status="pending"
    )

    return {
        "success": True,
        "data": serialize_case(case)
    }


@router.get("/")
def list_cases(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    cases = CaseRepository(db).list_by_user(
        current_user.id
    )

    return {
        "success": True,
        "total": len(cases),
        "data": [
            serialize_case(case)
            for case in cases
        ]
    }


@router.get("/{case_id}")
def get_case(
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

    return {
        "success": True,
        "data": serialize_case(case)
    }


@router.delete("/{case_id}")
def delete_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    repository = CaseRepository(db)

    case = repository.get(case_id)

    if not case or case.created_by != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    if case.workflows:
        raise HTTPException(
            status_code=409,
            detail="Cases with workflow history cannot be deleted."
        )

    repository.delete(case_id)

    return {
        "success": True,
        "message": "Case deleted successfully."
    }
