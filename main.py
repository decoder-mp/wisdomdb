"""Main application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session



from routers import (
    auth,
    users,
    lore,
    comments,
    likes,
    bookmarks,
    notifications,
    recommendations,
    ai,
    admin,
)
from core.config import BOOTSTRAP_ADMIN_EMAIL
from core.config import BOOTSTRAP_ADMIN_PASSWORD
from core.config import BOOTSTRAP_ADMIN_USERNAME
from core.config import ENABLE_BOOTSTRAP_ADMIN
from core.init_db import init_db
from core.database import SessionLocal
from core.security import hash_password
from models.user import User

init_db()


def ensure_bootstrap_admin() -> None:
    if not ENABLE_BOOTSTRAP_ADMIN:
        return

    bootstrap_email = BOOTSTRAP_ADMIN_EMAIL
    if not bootstrap_email or not BOOTSTRAP_ADMIN_PASSWORD:
        return

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == bootstrap_email).first()
        if user:
            if not user.is_admin:
                user.is_admin = True
                db.commit()
            return

        base_username = BOOTSTRAP_ADMIN_USERNAME or "lore_admin"
        candidate_username = base_username
        suffix = 1
        while db.query(User).filter(User.username == candidate_username).first():
            candidate_username = f"{base_username}_{suffix}"
            suffix += 1

        admin_user = User(
            username=candidate_username,
            email=bootstrap_email,
            hashed_password=hash_password(BOOTSTRAP_ADMIN_PASSWORD),
            is_active=True,
            is_admin=True,
        )
        db.add(admin_user)
        db.commit()
    finally:
        db.close()


ensure_bootstrap_admin()

app = FastAPI(
    title="Lore",
    version="1.9.1",
)

cors_origins_env = os.getenv("CORS_ORIGINS", "")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
if not cors_origins:
    cors_origins = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(lore.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(bookmarks.router)
app.include_router(notifications.router)
app.include_router(recommendations.router)
app.include_router(ai.router)
app.include_router(admin.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Lore",
        "version": "1.9.1",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.9.1",
    }