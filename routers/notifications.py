from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from schemas.notification import NotificationListResponse
from schemas.notification import NotificationResponse
from services.notification_service import NotificationService

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


def _serialize(items) -> NotificationListResponse:
    serialized = [NotificationResponse.model_validate(item) for item in items]
    return NotificationListResponse(
        count=len(serialized),
        results=serialized,
    )


def _get_owned_notification(db: Session, current_user, notification_id: int):
    notification = NotificationService.get_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your notification")
    return notification


@router.get("", response_model=NotificationListResponse)
def get_notifications(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _serialize(
        NotificationService.get_notifications(db, current_user.id),
    )


@router.get("/unread", response_model=NotificationListResponse)
def get_unread_notifications(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _serialize(
        NotificationService.get_notifications(db, current_user.id, unread_only=True),
    )


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def read_notification(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_notification(db, current_user, notification_id)
    return NotificationService.mark_read(db, notification_id)


@router.patch("/read-all")
def read_all_notifications(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated = NotificationService.mark_all_read(db, current_user.id)
    return {
        "updated": updated,
    }


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_notification(db, current_user, notification_id)
    NotificationService.delete_notification(db, notification_id)
    return {
        "message": "Notification deleted",
    }
