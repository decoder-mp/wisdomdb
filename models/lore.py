from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base



class Lore(Base):
    __tablename__ = "lore"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    person: Mapped[str] = mapped_column(String(255), nullable=False)
    profession: Mapped[str] = mapped_column(String(255), nullable=False)

    years_experience: Mapped[int] = mapped_column(Integer, nullable=False)

    theme: Mapped[str] = mapped_column(String(255), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    lore: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )
    embedding = Column(
        Text,
        nullable=True,
    )
    
    #  required ownership

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # safe relationship (prevents lazy-load crashes)
    author = relationship(
        "User",
        back_populates="lore_entries",
        lazy="selectin",
    )
    recommendations = relationship(
        "Recommendation",
        back_populates="lore",
        lazy="selectin",
    )