"""Admin-only routes: stats, user management, content moderation."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from models.lore import Lore
from models.user import User
from models.comment import Comment
from models.like import Like
from schemas.user import UserResponse
from schemas.lore import LoreResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


def _require_admin(current_user):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/stats")
def admin_stats(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    return {
        "users": db.query(User).count(),
        "lore": db.query(Lore).count(),
        "comments": db.query(Comment).count(),
        "likes": db.query(Like).count(),
        "admins": db.query(User).filter(User.is_admin == True).count(),  # noqa: E712
    }


@router.get("/users", response_model=list[UserResponse])
def admin_list_users(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    return db.query(User).order_by(User.created_at.desc()).all()


@router.delete("/users/{user_id}")
def admin_delete_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


@router.get("/lore", response_model=list[LoreResponse])
def admin_list_lore(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    return db.query(Lore).order_by(Lore.created_at.desc()).all()


@router.delete("/lore/{lore_id}")
def admin_delete_lore(
    lore_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    lore = db.query(Lore).filter(Lore.id == lore_id).first()
    if not lore:
        raise HTTPException(status_code=404, detail="Lore not found")
    db.delete(lore)
    db.commit()
    return {"message": "Lore deleted"}


@router.patch("/users/{user_id}/toggle-admin")
def admin_toggle_admin(
    user_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own admin status")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "is_admin": user.is_admin}
