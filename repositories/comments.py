from sqlalchemy.orm import Session

from models.comment import Comment


def create_comment(
    db: Session,
    content: str,
    user_id: int,
    lore_id: int,
):
    comment = Comment(
        content=content,
        user_id=user_id,
        lore_id=lore_id,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def get_comments_by_lore(
    db: Session,
    lore_id: int,
):
    return (
        db.query(Comment)
        .filter(Comment.lore_id == lore_id)
        .all()
    )


def get_comment_by_id(
    db: Session,
    comment_id: int,
):
    return (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )


def update_comment(
    db: Session,
    comment: Comment,
    content: str,
):
    comment.content = content
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(
    db: Session,
    comment: Comment,
):
    db.delete(comment)
    db.commit()