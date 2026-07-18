from datetime import UTC, datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    legacy_user_id: Mapped[int | None] = mapped_column(
        "user_id",
        Integer,
        nullable=True,
    )

    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    lore_id: Mapped[int | None] = mapped_column(
        ForeignKey("lore.id"),
        nullable=True,
        index=True,
    )

    comment_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id"),
        nullable=True,
        index=True,
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="SYSTEM",
    )

    message: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )

    recipient = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="received_notifications",
        lazy="selectin",
    )
    actor = relationship(
        "User",
        foreign_keys=[actor_id],
        back_populates="sent_notifications",
        lazy="selectin",
    )
    lore = relationship(
        "Lore",
        foreign_keys=[lore_id],
        lazy="selectin",
    )
