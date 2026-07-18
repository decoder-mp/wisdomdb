from sqlalchemy.orm import Session

from models.like import Like


def get_like(
    db: Session,
    user_id: int,
    lore_id: int,
):
    return (
        db.query(Like)
        .filter(
            Like.user_id == user_id,
            Like.lore_id == lore_id,
        )
        .first()
    )


def get_likes_by_user(
    db: Session,
    user_id: int,
):
    return (
        db.query(Like)
        .filter(Like.user_id == user_id)
        .all()
    )


def create_like(
    db: Session,
    user_id: int,
    lore_id: int,
):
    like = Like(
        user_id=user_id,
        lore_id=lore_id,
    )

    db.add(like)
    db.commit()
    db.refresh(like)

    return like


def delete_like(
    db: Session,
    like: Like,
):
    db.delete(like)
    db.commit()


def count_likes(
    db: Session,
    lore_id: int,
):
    return (
        db.query(Like)
        .filter(Like.lore_id == lore_id)
        .count()
    )