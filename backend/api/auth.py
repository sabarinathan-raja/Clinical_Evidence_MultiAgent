
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.repositories import UserRepository
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from backend.models.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    repository = UserRepository(db)

    email = request.email.strip().lower()

    if repository.get_by_email(email):
        raise HTTPException(
            status_code=409,
            detail="Email already registered."
        )

    user = repository.create(
        email=email,
        full_name=request.full_name.strip(),
        hashed_password=hash_password(request.password),
        role="researcher"
    )

    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token
    )


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    repository = UserRepository(db)

    user = repository.get_by_email(
        request.email.strip().lower()
    )

    if not user or not verify_password(
        request.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is inactive."
        )

    return TokenResponse(
        access_token=create_access_token(user.id)
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    try:
        payload = decode_access_token(token)

        user = UserRepository(db).get_by_id(
            payload["sub"]
        )

        if user is None or not user.is_active:
            raise ValueError("User not found or inactive.")

        return user

    except ValueError:

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )


def require_roles(*roles):

    def role_dependency(
        current_user=Depends(get_current_user)
    ):

        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions."
            )

        return current_user

    return role_dependency


@router.get("/me")
def get_profile(
    current_user=Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active
    }
