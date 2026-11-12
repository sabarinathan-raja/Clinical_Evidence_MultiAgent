from __future__ import annotations

from backend.database.repositories import repository
from backend.models.schemas import CaseCreate, CaseRecord


def create_case(payload: CaseCreate) -> CaseRecord:
    return CaseRecord(**repository.create_case(payload.title, payload.patient_context.model_dump()))


def list_cases() -> list[CaseRecord]:
    return [CaseRecord(**item) for item in repository.list_cases()]


def get_case(case_id: str) -> CaseRecord | None:
    record = repository.get_case(case_id)
    return CaseRecord(**record) if record else None
