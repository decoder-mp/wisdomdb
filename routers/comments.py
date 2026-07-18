from fastapi import APIRouter
from fastapi import Depends 
from fastapi import HTTPException 
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user

from repositories.lore import LoreRepository
from schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)

from repositories.comments import (
    create_comment,
    get_comments_by_lore,
    get_comment_by_id,
    update_comment,
    delete_comment,
)

from services.notification_service import NotificationService

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


def _get_lore_or_404(db: Session, lore_id: int):
    lore = LoreRepository().get_by_id(db, lore_id)

    if not lore:
        raise HTTPException(
            status_code=404,
            detail="Lore not found",
        )

    return lore


@router.post(
    "/{lore_id}",
    response_model=CommentResponse,
)
def add_comment(
    lore_id: int,
    payload: CommentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_lore_or_404(db, lore_id)

    comment = create_comment(
        db=db,
        content=payload.content,
        user_id=current_user.id,
        lore_id=lore_id,
    )

    NotificationService.create_comment_notification(
        db,
        lore_id,
        current_user,
        comment_id=comment.id,
    )

    return comment


@router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
)
def edit_comment(
    comment_id: int,
    payload: CommentUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = get_comment_by_id(
        db,
        comment_id,
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not your comment",
        )

    return update_comment(
        db,
        comment,
        payload.content,
    )

@router.delete(
    "/{comment_id}",
)
def remove_comment(
    comment_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = get_comment_by_id(
        db,
        comment_id,
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not your comment",
        )

    delete_comment(
        db,
        comment,
    )

    return {
        "message": "Comment deleted"
    }


@router.get(
    "/{lore_id}",
    response_model=list[CommentResponse],
)
def get_comments(
    lore_id: int,
    db: Session = Depends(get_db),
):
    _get_lore_or_404(db, lore_id)

    return get_comments_by_lore(
        db,
        lore_id,
    )