from __future__ import annotations

from sqlalchemy.orm import Session

from models.notification import Notification


def create_notification(
    db: Session,
    recipient_id: int,
    actor_id: int | None,
    lore_id: int | None,
    comment_id: int | None,
    notification_type: str,
    message: str,
):
    notification = Notification(
        recipient_id=recipient_id,
        legacy_user_id=recipient_id,
        actor_id=actor_id,
        lore_id=lore_id,
        comment_id=comment_id,
        type=notification_type,
        message=message,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notifications(
    db: Session,
    user_id: int,
):
    return (
        db.query(Notification)
        .filter(Notification.recipient_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_unread_notifications(
    db: Session,
    user_id: int,
):
    return (
        db.query(Notification)
        .filter(
            Notification.recipient_id == user_id,
            Notification.is_read.is_(False),
        )
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_by_id(
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
    notification = get_by_id(db, notification_id)
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification


def mark_all_read(
    db: Session,
    user_id: int,
):
    updated = (
        db.query(Notification)
        .filter(
            Notification.recipient_id == user_id,
            Notification.is_read.is_(False),
        )
        .update({Notification.is_read: True}, synchronize_session=False)
    )
    db.commit()
    return updated


def delete_notification(
    db: Session,
    notification_id: int,
):
    notification = get_by_id(db, notification_id)
    if notification:
        db.delete(notification)
        db.commit()
    return notification


def find_existing_event_notification(
    db: Session,
    recipient_id: int,
    actor_id: int | None,
    lore_id: int | None,
    notification_type: str,
):
    return (
        db.query(Notification)
        .filter(
            Notification.recipient_id == recipient_id,
            Notification.actor_id == actor_id,
            Notification.lore_id == lore_id,
            Notification.type == notification_type,
        )
        .first()
    )


def find_existing_lore_notification(
    db: Session,
    recipient_id: int,
    lore_id: int,
    notification_type: str,
):
    return (
        db.query(Notification)
        .filter(
            Notification.recipient_id == recipient_id,
            Notification.lore_id == lore_id,
            Notification.type == notification_type,
        )
        .first()
    )


def create(
    db: Session,
    recipient_id: int,
    actor_id: int | None,
    lore_id: int | None,
    comment_id: int | None,
    event_kind: str,
    message: str,
):
    return create_notification(
        db,
        recipient_id=recipient_id,
        actor_id=actor_id,
        lore_id=lore_id,
        comment_id=comment_id,
        notification_type=event_kind,
        message=message,
    )


def get_for_user(
    db: Session,
    user_id: int,
    unread_only: bool = False,
):
    if unread_only:
        return get_unread_notifications(db, user_id)
    return get_notifications(db, user_id)


def mark_read(
    db: Session,
    notification_id: int,
):
    return mark_notification_read(db, notification_id)


def delete(
    db: Session,
    notification_id: int,
):
    return delete_notification(db, notification_id)
