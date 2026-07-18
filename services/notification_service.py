from __future__ import annotations

from sqlalchemy.orm import Session

from repositories.notification_repository import create_notification
from repositories.notification_repository import delete_notification
from repositories.notification_repository import find_existing_event_notification
from repositories.notification_repository import find_existing_lore_notification
from repositories.notification_repository import get_by_id
from repositories.notification_repository import get_notifications
from repositories.notification_repository import get_unread_notifications
from repositories.notification_repository import mark_all_read
from repositories.notification_repository import mark_notification_read
from repositories.lore import LoreRepository


class NotificationType:
    LIKE = "like"
    COMMENT = "comment"
    BOOKMARK = "bookmark"
    NEW_LORE_MATCH = "new_lore_match"
    RECOMMENDATION_REFRESH = "recommendation_refresh"
    SYSTEM = "system"


class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        recipient_id: int,
        actor_id: int | None,
        lore_id: int | None,
        comment_id: int | None,
        notification_type: str,
        message: str,
    ):
        return create_notification(
            db,
            recipient_id=recipient_id,
            actor_id=actor_id,
            lore_id=lore_id,
            comment_id=comment_id,
            notification_type=notification_type,
            message=message,
        )

    @staticmethod
    def create_comment_notification(
        db: Session,
        lore_id: int,
        actor_user,
        comment_id: int,
    ):
        lore = LoreRepository().get_by_id(db, lore_id)
        if not lore or lore.user_id == actor_user.id:
            return None

        return NotificationService.create_notification(
            db,
            recipient_id=lore.user_id,
            actor_id=actor_user.id,
            lore_id=lore.id,
            comment_id=comment_id,
            notification_type=NotificationType.COMMENT,
            message=f"{actor_user.username} commented on your Lore.",
        )

    @staticmethod
    def create_like_notification(
        db: Session,
        lore_id: int,
        actor_user,
    ):
        lore = LoreRepository().get_by_id(db, lore_id)
        if not lore or lore.user_id == actor_user.id:
            return None

        existing = find_existing_event_notification(
            db,
            recipient_id=lore.user_id,
            actor_id=actor_user.id,
            lore_id=lore.id,
            notification_type=NotificationType.LIKE,
        )
        if existing:
            return existing

        return NotificationService.create_notification(
            db,
            recipient_id=lore.user_id,
            actor_id=actor_user.id,
            lore_id=lore.id,
            comment_id=None,
            notification_type=NotificationType.LIKE,
            message=f"{actor_user.username} liked your Lore.",
        )

    @staticmethod
    def create_bookmark_notification(
        db: Session,
        lore_id: int,
        actor_user,
    ):
        lore = LoreRepository().get_by_id(db, lore_id)
        if not lore or lore.user_id == actor_user.id:
            return None

        existing = find_existing_event_notification(
            db,
            recipient_id=lore.user_id,
            actor_id=actor_user.id,
            lore_id=lore.id,
            notification_type=NotificationType.BOOKMARK,
        )
        if existing:
            return existing

        return NotificationService.create_notification(
            db,
            recipient_id=lore.user_id,
            actor_id=actor_user.id,
            lore_id=lore.id,
            comment_id=None,
            notification_type=NotificationType.BOOKMARK,
            message=f"{actor_user.username} bookmarked your Lore.",
        )

    @staticmethod
    def create_new_lore_interest_notification(
        db: Session,
        recipient_id: int,
        lore_id: int,
        theme: str,
    ):
        existing = find_existing_lore_notification(
            db,
            recipient_id=recipient_id,
            lore_id=lore_id,
            notification_type=NotificationType.NEW_LORE_MATCH,
        )
        if existing:
            return existing

        return NotificationService.create_notification(
            db,
            recipient_id=recipient_id,
            actor_id=None,
            lore_id=lore_id,
            comment_id=None,
            notification_type=NotificationType.NEW_LORE_MATCH,
            message=f"A new Lore about {theme} may interest you.",
        )

    @staticmethod
    def create_recommendation_refresh_notification(
        db: Session,
        recipient_id: int,
    ):
        return NotificationService.create_notification(
            db,
            recipient_id=recipient_id,
            actor_id=None,
            lore_id=None,
            comment_id=None,
            notification_type=NotificationType.RECOMMENDATION_REFRESH,
            message="Your recommendations have been updated.",
        )

    @staticmethod
    def create_interaction_notification(
        db: Session,
        lore_id: int,
        actor_user,
        event_kind: str,
        comment_id: int | None = None,
    ):
        if event_kind == NotificationType.COMMENT and comment_id is not None:
            return NotificationService.create_comment_notification(db, lore_id, actor_user, comment_id)
        if event_kind == NotificationType.LIKE:
            return NotificationService.create_like_notification(db, lore_id, actor_user)
        if event_kind == NotificationType.BOOKMARK:
            return NotificationService.create_bookmark_notification(db, lore_id, actor_user)
        return None

    @staticmethod
    def get_notifications(
        db: Session,
        user_id: int,
        unread_only: bool = False,
    ):
        if unread_only:
            return get_unread_notifications(db, user_id)
        return get_notifications(db, user_id)

    @staticmethod
    def get_notification(
        db: Session,
        notification_id: int,
    ):
        return get_by_id(db, notification_id)

    @staticmethod
    def mark_read(
        db: Session,
        notification_id: int,
    ):
        return mark_notification_read(db, notification_id)

    @staticmethod
    def mark_all_read(
        db: Session,
        user_id: int,
    ):
        return mark_all_read(db, user_id)

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: int,
    ):
        return delete_notification(db, notification_id)
