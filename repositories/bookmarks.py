# repositories/bookmarks.py

from sqlalchemy.orm import Session
from models.bookmark import Bookmark


def get_bookmark(db: Session, user_id: int, lore_id: int):
    return (
        db.query(Bookmark)
        .filter(
            Bookmark.user_id == user_id,
            Bookmark.lore_id == lore_id,
        )
        .first()
    )


def create_bookmark(db: Session, user_id: int, lore_id: int):
    bookmark = Bookmark(
        user_id=user_id,
        lore_id=lore_id,
    )

    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    return bookmark


def delete_bookmark(db: Session, bookmark: Bookmark):
    db.delete(bookmark)
    db.commit()


def get_user_bookmarks(db: Session, user_id: int):
    return (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user_id)
        .all()
    )
def count_bookmarks(
    db: Session,
    lore_id: int,
):
    return (
        db.query(Bookmark)
        .filter(
            Bookmark.lore_id == lore_id
        )
        .count()
    )