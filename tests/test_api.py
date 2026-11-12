
from backend.main import app

from backend.models.intake_schema import IntakeRequest
from backend.models.schemas import CaseCreateRequest

from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


def test_root_route_exists():

    paths = [
        route.path
        for route in app.routes
    ]

    assert "/" in paths
    assert "/health" in paths


def test_api_routes_exist():

    paths = [
        route.path
        for route in app.routes
    ]

    assert "/auth/login" in paths
    assert "/auth/register" in paths
    assert "/cases/" in paths
    assert "/queries/analyze" in paths


def test_intake_schema():

    request = IntakeRequest(
        clinical_question=(
            "What evidence exists for this research question?"
        )
    )

    assert request.clinical_question


def test_case_schema():

    request = CaseCreateRequest(
        title="Synthetic research case",
        clinical_question=(
            "What evidence exists for this research question?"
        )
    )

    assert request.title


def test_password_hashing():

    password = "SyntheticPassword123!"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_token_creation():

    token = create_access_token(
        "synthetic-user-id"
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "synthetic-user-id"
    assert payload["type"] == "access"
