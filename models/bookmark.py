# models/bookmark.py

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from core.database import Base

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lore_id = Column(Integer, ForeignKey("lore.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "lore_id", name="unique_user_lore_bookmark"),
    )