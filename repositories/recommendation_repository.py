from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from models.recommendation import Recommendation


def create(
    db: Session,
    user_id: int,
    lore_id: int,
    score: float,
    reason: str,
):
    recommendation = Recommendation(
        user_id=user_id,
        lore_id=lore_id,
        score=score,
        reason=reason,
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return recommendation


def get_for_user(
    db: Session,
    user_id: int,
):
    return (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .order_by(Recommendation.score.desc(), Recommendation.created_at.desc())
        .all()
    )


def delete_old(
    db: Session,
    user_id: int,
    older_than_hours: int = 24,
):
    threshold = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=older_than_hours)
    deleted = (
        db.query(Recommendation)
        .filter(
            Recommendation.user_id == user_id,
            Recommendation.created_at < threshold,
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted


def exists(
    db: Session,
    user_id: int,
    lore_id: int,
):
    return (
        db.query(Recommendation)
        .filter(
            Recommendation.user_id == user_id,
            Recommendation.lore_id == lore_id,
        )
        .first()
        is not None
    )


def clear_for_user(
    db: Session,
    user_id: int,
):
    deleted = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted


def get_by_id(
    db: Session,
    recommendation_id: int,
):
    return (
        db.query(Recommendation)
        .filter(Recommendation.id == recommendation_id)
        .first()
    )


def delete_recommendation(
    db: Session,
    recommendation: Recommendation,
):
    db.delete(recommendation)
    db.commit()
