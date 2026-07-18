"""User model."""

from datetime import UTC, datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    """User entity."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    lore_entries = relationship(
        "Lore",
        back_populates="author",
    )
    recommendations = relationship(
        "Recommendation",
        back_populates="user",
        lazy="selectin",
    )
    received_notifications = relationship(
        "Notification",
        foreign_keys="Notification.recipient_id",
        back_populates="recipient",
        lazy="selectin",
    )
    sent_notifications = relationship(
        "Notification",
        foreign_keys="Notification.actor_id",
        back_populates="actor",
        lazy="selectin",
    )
    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        lazy="selectin",
    )