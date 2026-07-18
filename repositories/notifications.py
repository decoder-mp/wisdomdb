from sqlalchemy.orm import Session

from models.notification import Notification


def create_notification(
    db: Session,
    user_id: int,
    message: str,
):
    notification = Notification(
        recipient_id=user_id,
        legacy_user_id=user_id,
        message=message,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_user_notifications(
    db: Session,
    user_id: int,
):
    return (
        db.query(Notification)
        .filter(
            Notification.recipient_id == user_id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )


def get_notification_by_id(
    db: Session,
    notification_id: int,
):
    return (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )


def mark_notification_read(
    db: Session,
    notification_id: int,
):
    notification = get_notification_by_id(db, notification_id)

    if notification:
        notification.is_read = True

        db.commit()
        db.refresh(notification)

    return notification


def delete_notification(
    db: Session,
    notification_id: int,
):
    notification = get_notification_by_id(db, notification_id)

    if notification:
        db.delete(notification)
        db.commit()

    return notification