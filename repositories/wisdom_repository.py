from sqlalchemy.orm import Session
from models.wisdom import WisdomEntry
from schemas.wisdom import WisdomCreate, WisdomUpdate
from typing import List, Optional

class WisdomRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, wisdom: WisdomCreate, owner_id: int):
        db_wisdom = WisdomEntry(**wisdom.dict(), owner_id=owner_id)
        self.db.add(db_wisdom)
        self.db.commit()
        self.db.refresh(db_wisdom)
        return db_wisdom

    def get_by_id(self, wisdom_id: int):
        return self.db.query(WisdomEntry).filter(WisdomEntry.id == wisdom_id).first()

    def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[WisdomEntry]:
        return self.db.query(WisdomEntry).filter(WisdomEntry.owner_id == owner_id).offset(skip).limit(limit).all()

    def update(self, wisdom_id: int, wisdom_update: WisdomUpdate):
        db_wisdom = self.get_by_id(wisdom_id)
        if db_wisdom:
            for key, value in wisdom_update.dict(exclude_unset=True).items():
                setattr(db_wisdom, key, value)
            self.db.commit()
            self.db.refresh(db_wisdom)
        return db_wisdom

    def delete(self, wisdom_id: int):
        db_wisdom = self.get_by_id(wisdom_id)
        if db_wisdom:
            self.db.delete(db_wisdom)
            self.db.commit()
        return db_wisdom