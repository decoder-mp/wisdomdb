"""Application configuration."""

import os
from pathlib import Path

from dotenv import dotenv_values
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


def is_production_like_env() -> bool:
    return any(
        os.getenv(name)
        for name in (
            "RAILWAY_PROJECT_ID",
            "RAILWAY_ENVIRONMENT_ID",
            "RAILWAY_ENVIRONMENT_NAME",
            "RENDER",
            "FLY_APP_NAME",
        )
    ) or os.getenv("APP_ENV", "").strip().lower() in {"production", "prod"}


if is_production_like_env():
    DOTENV_VALUES = {}
else:
    load_dotenv(BASE_DIR / ".env", override=False)
    DOTENV_VALUES = dotenv_values(BASE_DIR / ".env")


def get_setting(name: str, default: str | None = None) -> str | None:
    env_value = os.getenv(name)
    dotenv_value = DOTENV_VALUES.get(name)

    if name == "DATABASE_URL":
        if dotenv_value and env_value and any(marker in env_value for marker in ("localhost", "127.0.0.1", "::1")):
            return dotenv_value
        return env_value or dotenv_value or default

    return env_value or dotenv_value or default


def normalize_database_url(database_url: str | None) -> str | None:
    if not database_url:
        return None

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return database_url


def build_database_url() -> str:
    postgres_override_keys = (
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
    )
    has_explicit_postgres_overrides = any(
        os.getenv(key) is not None for key in postgres_override_keys
    )

    runtime_database_url = os.getenv("DATABASE_URL")
    dotenv_database_url = DOTENV_VALUES.get("DATABASE_URL")

    # In deployed environments, require DATABASE_URL from runtime env vars.
    # This prevents accidental fallback to local .env database values.
    is_production_like = is_production_like_env()

    if is_production_like and not runtime_database_url:
        raise RuntimeError(
            "DATABASE_URL must be set in runtime environment for deployment."
        )

    if (
        is_production_like
        and runtime_database_url
        and any(marker in runtime_database_url.lower() for marker in ("localhost", "127.0.0.1", "::1"))
    ):
        raise RuntimeError(
            "DATABASE_URL cannot target localhost in deployment."
        )

    if has_explicit_postgres_overrides and runtime_database_url == dotenv_database_url:
        runtime_database_url = None

    database_url = normalize_database_url(
        runtime_database_url if has_explicit_postgres_overrides else get_setting("DATABASE_URL")
    )
    if database_url:
        return database_url

    postgres_host = get_setting("POSTGRES_HOST", "localhost")
    postgres_port = get_setting("POSTGRES_PORT", "5432")
    postgres_user = get_setting("POSTGRES_USER", "postgres")
    postgres_password = get_setting("POSTGRES_PASSWORD", "postgres")
    postgres_db = get_setting("POSTGRES_DB", "lore")

    return (
        f"postgresql+psycopg://{postgres_user}:{postgres_password}"
        f"@{postgres_host}:{postgres_port}/{postgres_db}"
    )


DATABASE_URL = build_database_url()

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "CHANGE_ME_IN_PRODUCTION"
)

ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30"
    )
)

OPENAI_API_KEY = os.getenv(
   "OPENAI_API_KEY", ""
)


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


ENABLE_BOOTSTRAP_ADMIN = _as_bool(
    os.getenv("ENABLE_BOOTSTRAP_ADMIN", "true")
)

BOOTSTRAP_ADMIN_EMAIL = os.getenv(
    "BOOTSTRAP_ADMIN_EMAIL",
    "admin@lore.app",
).strip().lower()

BOOTSTRAP_ADMIN_USERNAME = os.getenv(
    "BOOTSTRAP_ADMIN_USERNAME",
    "lore_admin",
).strip()

BOOTSTRAP_ADMIN_PASSWORD = os.getenv(
    "BOOTSTRAP_ADMIN_PASSWORD",
    "Admin1234!",
)

PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30")
)

FRONTEND_BASE_URL = os.getenv(
    "FRONTEND_BASE_URL",
    "http://127.0.0.1:5173",
).rstrip("/")

SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = _as_bool(os.getenv("SMTP_USE_TLS", "true"))
EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS", "").strip()