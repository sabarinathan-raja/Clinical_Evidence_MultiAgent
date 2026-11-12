from backend.database.repositories import repository


def record(event_type: str, payload: dict) -> None:
    repository.audit(event_type, payload)
