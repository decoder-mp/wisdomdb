from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user

from repositories.lore import LoreRepository

from repositories.bookmarks import (
    get_bookmark,
    create_bookmark,
    delete_bookmark,
    get_user_bookmarks,
)

from services.notification_service import NotificationService

router = APIRouter(
    prefix="/bookmarks",
    tags=["Bookmarks"],
)


def _get_lore_or_404(db: Session, lore_id: int):
    lore = LoreRepository().get_by_id(db, lore_id)

    if not lore:
        raise HTTPException(
            status_code=404,
            detail="Lore not found",
        )

    return lore


# CREATE BOOKMARK
@router.post("/{lore_id}")
def bookmark_lore(
    lore_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _get_lore_or_404(db, lore_id)

    existing = get_bookmark(
        db,
        current_user.id,
        lore_id,
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Already bookmarked",
        )

    bookmark = create_bookmark(
        db,
        current_user.id,
        lore_id,
    )

    NotificationService.create_bookmark_notification(
        db,
        lore_id,
        current_user,
    )

    return bookmark



# REMOVE BOOKMARK
@router.delete("/{lore_id}")
def remove_bookmark(
    lore_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    bookmark = get_bookmark(
        db,
        current_user.id,
        lore_id,
    )

    if not bookmark:
        raise HTTPException(
            status_code=404,
            detail="Bookmark not found",
        )

    delete_bookmark(db, bookmark)

    return {"message": "Bookmark removed"}


# GET MY BOOKMARKS
@router.get("/me")
def my_bookmarks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_user_bookmarks(db, current_user.id)