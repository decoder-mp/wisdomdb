from pydantic import BaseModel, Field
from datetime import datetime


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    user_id: int
    lore_id: int
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }