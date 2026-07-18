from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey

from core.database import Base


class Like(Base):
    __tablename__ = "likes"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    lore_id = Column(
        Integer,
        ForeignKey("lore.id"),
        nullable=False,
    )