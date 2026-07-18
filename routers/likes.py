from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user

from repositories.lore import LoreRepository

from repositories.likes import (
    create_like,
    get_like,
    delete_like,
    count_likes,
    get_likes_by_user,
)

from schemas.like import LikeCountResponse, LikeResponse

from services.notification_service import NotificationService


router = APIRouter(
    prefix="/likes",
    tags=["Likes"],
)


def _get_lore_or_404(db: Session, lore_id: int):
    lore = LoreRepository().get_by_id(db, lore_id)

    if not lore:
        raise HTTPException(
            status_code=404,
            detail="Lore not found",
        )

    return lore


@router.post("/{lore_id}")
def like_lore(
    lore_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_lore_or_404(db, lore_id)

    existing_like = get_like(
        db,
        current_user.id,
        lore_id,
    )

    if existing_like:
        raise HTTPException(
            status_code=400,
            detail="Already liked",
        )

    create_like(
        
        db,
        current_user.id,
        lore_id,
    )

    NotificationService.create_like_notification(
        db,
        lore_id,
        current_user,
    )

    return {
        "message": "Lore liked"
    }

@router.get(
    "/me",
    response_model=list[LikeResponse],
)
def get_my_likes(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_likes_by_user(db, current_user.id)


@router.get(
    "/{lore_id}",
    response_model=LikeCountResponse,
)
def get_likes(
    lore_id: int,
    db: Session = Depends(get_db),
):
    _get_lore_or_404(db, lore_id)

    return {
        "lore_id": lore_id,
        "likes": count_likes(
            db,
            lore_id,
        ),
    }

@router.delete("/{lore_id}")
def unlike_lore(
    lore_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    like = get_like(
        db,
        current_user.id,
        lore_id,
    )

    if not like:
        raise HTTPException(
            status_code=404,
            detail="Like not found",
        )

    delete_like(
        db,
        like,
    )

    return {
        "message": "Like removed"
    }
