"""Lore repository helpers."""

from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.bookmark import Bookmark
from models.comment import Comment
from models.like import Like
from models.lore import Lore


class LoreRepository:
    def get_by_id(self, db: Session, lore_id: int):
        return db.query(Lore).filter(Lore.id == lore_id).first()

    def get_all(self, db: Session):
        return db.query(Lore).order_by(Lore.created_at.desc()).all()

    def get_for_user(self, db: Session, user_id: int):
        return (
            db.query(Lore)
            .filter(Lore.user_id == user_id)
            .order_by(Lore.created_at.desc())
            .all()
        )

    def get_excluding_user(self, db: Session, user_id: int):
        return (
            db.query(Lore)
            .filter(Lore.user_id != user_id)
            .order_by(Lore.created_at.desc())
            .all()
        )

    def get_by_theme(self, db: Session, theme: str, limit: int | None = None):
        query = (
            db.query(Lore)
            .filter(Lore.theme.ilike(f"%{theme}%"))
            .order_by(Lore.created_at.desc())
        )
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def list_lore(self, db: Session, limit: int | None = None):
        query = db.query(Lore).order_by(Lore.created_at.desc())
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def update(self, db: Session, lore: Lore, data: dict):
        for key, value in data.items():
            if value is not None:
                setattr(lore, key, value)
        db.commit()
        db.refresh(lore)
        return lore

    def delete(self, db: Session, lore: Lore):
        db.query(Comment).filter(Comment.lore_id == lore.id).delete(synchronize_session=False)
        db.query(Like).filter(Like.lore_id == lore.id).delete(synchronize_session=False)
        db.query(Bookmark).filter(Bookmark.lore_id == lore.id).delete(synchronize_session=False)
        db.delete(lore)
        db.commit()

    def discover_lore(self, db: Session, query: str, limit: int = 20):
        q = f"%{query.strip()}%"
        if not query.strip():
            return []

        return (
            db.query(Lore)
            .filter(
                or_(
                    Lore.theme.ilike(q),
                    Lore.profession.ilike(q),
                    Lore.question.ilike(q),
                    Lore.lore.ilike(q),
                    Lore.person.ilike(q),
                )
            )
            .order_by(Lore.created_at.desc())
            .limit(limit)
            .all()
        )

    def create(self, db: Session, lore_data: dict):
        lore_data.pop("embedding", None)
        lore = Lore(**lore_data)
        db.add(lore)
        db.commit()
        db.refresh(lore)
        return lore


def get_lore_by_theme(db: Session, theme: str, limit: int | None = None):
    return LoreRepository().get_by_theme(db, theme, limit)


def list_lore(db: Session, limit: int | None = None):
    return LoreRepository().list_lore(db, limit)


def hybrid_search(db: Session, query: str, embedding: list[float], limit: int = 20):
    _ = embedding
    sql = text(
        """
        SELECT *
        FROM lore
        WHERE
            theme ILIKE :query_like OR
            profession ILIKE :query_like OR
            question ILIKE :query_like OR
            lore ILIKE :query_like OR
            person ILIKE :query_like
        ORDER BY created_at DESC
        LIMIT :limit
        """
    )
    return db.execute(
        sql,
        {
            "query_like": f"%{query}%",
            "limit": limit,
        },
    ).fetchall()
