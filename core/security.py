"""Security utilities."""

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from jose import JWTError
from jose import jwt
from passlib.context import CryptContext

from core.config import ALGORITHM
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from core.config import SECRET_KEY

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    normalized_password = password[:72]
    return password_context.hash(normalized_password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a password."""
    normalized_password = plain_password[:72]
    return password_context.verify(
        normalized_password,
        hashed_password,
    )


def create_access_token(
    subject: str,
) -> str:
    """Create JWT access token."""

    expire = datetime.now(
        timezone.utc,
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    payload = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict | None:
    """Decode JWT token."""

    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except JWTError:
        return None