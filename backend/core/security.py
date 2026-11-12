
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.core.config import settings


ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    if not password or len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    if not plain_password or not hashed_password:
        return False

    try:
        return pwd_context.verify(
            plain_password,
            hashed_password
        )
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:

    if not subject:
        raise ValueError("Token subject cannot be empty.")

    now = datetime.now(timezone.utc)

    expire = now + (
        expires_delta
        or timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "type": "access"
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> dict:

    if not token:
        raise ValueError("Token is required.")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            raise ValueError("Invalid token type.")

        if not payload.get("sub"):
            raise ValueError("Invalid token subject.")

        return payload

    except JWTError as exc:
        raise ValueError(
            "Invalid or expired authentication token."
        ) from exc


def get_token_subject(token: str) -> str:
    payload = decode_access_token(token)
    return payload["sub"]
