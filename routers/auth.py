import os
from datetime import UTC, datetime, timedelta
import hashlib
import secrets
from urllib.parse import quote

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from pydantic import ValidationError

from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from core.config import FRONTEND_BASE_URL
from core.config import PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
from core.security import hash_password
from core.security import verify_password
from core.security import create_access_token
from fastapi.security import OAuth2PasswordRequestForm

from repositories.users import (
    get_user_by_email,
    create_user,
)
from models.password_reset_token import PasswordResetToken
from services.email_service import EmailConfigurationError
from services.email_service import send_password_reset_email

from schemas.auth import (
    AdminResetPasswordRequest,
    ChangePasswordRequest,
    CompletePasswordResetRequest,
    ForgotPasswordRequest,
    UserRegister,
    TokenResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _issue_password_reset_token(db: Session, user) -> str:
    now = _now()
    active_tokens = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .all()
    )
    for token in active_tokens:
        token.used_at = now

    raw_token = secrets.token_urlsafe(32)
    token_record = PasswordResetToken(
        user_id=user.id,
        token_hash=_hash_reset_token(raw_token),
        expires_at=now + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )
    db.add(token_record)
    db.commit()
    return raw_token


def _consume_password_reset_token(db: Session, raw_token: str):
    token_record = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == _hash_reset_token(raw_token))
        .first()
    )
    if not token_record:
        return None, None

    now = _now()
    if token_record.used_at is not None or token_record.expires_at <= now:
        return None, token_record

    return token_record.user, token_record


def _format_validation_errors(errors: list[dict]) -> list[dict[str, str]]:
    formatted_errors = []

    for error in errors:
        location = error.get("loc", [])
        field_name = location[-1] if location else "body"
        message = error.get("msg", "Invalid input.")
        error_type = error.get("type", "")

        if "missing" in error_type:
            message = f"{field_name} is required."
        elif field_name == "email" and "email" in error_type:
            message = "email must be a valid email address."
        elif field_name == "password" and "at least 8 characters" in message:
            message = "password must be at least 8 characters long."
        elif field_name == "username" and "at least 3 characters" in message:
            message = "username must be at least 3 characters long."

        formatted_errors.append(
            {
                "field": str(field_name),
                "message": str(message),
            }
        )

    return formatted_errors


async def parse_register_payload(
    request: Request,
    username: str | None = Form(default=None),
    email: str | None = Form(default=None),
    password: str | None = Form(default=None),
    is_admin: bool | None = Form(default=None),
) -> UserRegister:
    content_type = request.headers.get("content-type", "").lower()

    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        raw_payload = {
            "username": username,
            "email": email,
            "password": password,
        }
        if is_admin is not None:
            raw_payload["is_admin"] = is_admin
    else:
        try:
            raw_payload = await request.json()
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "field": "body",
                        "message": "Invalid JSON body. Check for missing quotes or commas.",
                    }
                ],
            ) from exc

    if not isinstance(raw_payload, dict):
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "field": "body",
                    "message": "Request body must be a JSON object or form fields.",
                }
            ],
        )

    try:
        return UserRegister(**raw_payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=_format_validation_errors(exc.errors()),
        ) from exc


@router.post("/register")
def register(
    request: Request,
    payload: UserRegister = Depends(parse_register_payload),
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(
        db,
        payload.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    # is_admin only honoured when the secret provision header is present
    admin_secret = os.getenv("ADMIN_PROVISION_SECRET", "")
    admin_header = request.headers.get("x-admin-provision", "")
    grant_admin = (
        payload.is_admin
        and bool(admin_secret)
        and admin_header == admin_secret
    )

    user = create_user(
        db=db,
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(
            payload.password
        ),
        is_admin=grant_admin,
    )

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
    }
@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_user_by_email(
        db,
        form_data.username,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    if not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    # Promote configured bootstrap admin on first successful login.
    bootstrap_email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
    if (
        bootstrap_email
        and user.email.strip().lower() == bootstrap_email
        and not user.is_admin
    ):
        user.is_admin = True
        db.commit()
        db.refresh(user)

    token = create_access_token(
        str(user.id)
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(
        payload.current_password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect",
        )

    if verify_password(
        payload.new_password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=400,
            detail="New password must be different from current password",
        )

    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    db.refresh(current_user)

    return {"message": "Password updated"}


@router.post("/reset-password")
def reset_password(
    payload: AdminResetPasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    user = get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if verify_password(
        payload.new_password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=400,
            detail="New password must be different from current password",
        )

    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    db.refresh(user)

    return {"message": "Password reset"}


@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, payload.email)
    if user:
        raw_token = _issue_password_reset_token(db, user)
        reset_link = f"{FRONTEND_BASE_URL}/reset-password?token={quote(raw_token)}"
        try:
            send_password_reset_email(user.email, reset_link)
        except EmailConfigurationError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "message": "If an account exists for that email, a reset link has been sent.",
    }


@router.post("/complete-password-reset")
def complete_password_reset(
    payload: CompletePasswordResetRequest,
    db: Session = Depends(get_db),
):
    user, token_record = _consume_password_reset_token(db, payload.token)
    if not user or not token_record:
        raise HTTPException(
            status_code=400,
            detail="Reset link is invalid or expired",
        )

    if verify_password(payload.new_password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="New password must be different from current password",
        )

    now = _now()
    user.hashed_password = hash_password(payload.new_password)
    token_record.used_at = now

    other_active_tokens = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.id != token_record.id,
        )
        .all()
    )
    for active_token in other_active_tokens:
        active_token.used_at = now

    db.commit()

    return {"message": "Password reset complete"}