from __future__ import annotations

from backend.database.repositories import repository


def get_report(report_id: str) -> dict | None:
    return repository.get_report(report_id)
