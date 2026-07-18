from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime
)

from datetime import UTC, datetime

from core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    reporter_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    lore_id = Column(
        Integer,
        ForeignKey("lore.id"),
        nullable=False
    )

    reason = Column(
        String,
        nullable=False
    )

    details = Column(Text)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )