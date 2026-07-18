from datetime import datetime
from pydantic import BaseModel
from .user import UserResponse


class LoreCreate(BaseModel):
    person: str
    profession: str
    years_experience: int
    theme: str
    question: str
    lore: str


class LoreUpdate(BaseModel):
    person: str | None = None
    profession: str | None = None
    years_experience: int | None = None
    theme: str | None = None
    question: str | None = None
    lore: str | None = None


class LoreResponse(BaseModel):
    id: int
    person: str
    profession: str
    years_experience: int
    theme: str
    question: str
    lore: str
    user_id: int
    created_at: datetime
    
    author: UserResponse

    model_config = {
        "from_attributes": True
    }