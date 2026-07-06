from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WisdomCreate(BaseModel):
    title: str
    content: str
    category: str
    source_type: str

class WisdomRead(BaseModel):
    id: int
    title: str
    content: str
    category: str
    source_type: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class WisdomUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    source_type: Optional[str] = None