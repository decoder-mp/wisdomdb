from pydantic import BaseModel
from datetime import datetime


class NotificationCreate(BaseModel):
    recipient_id: int
    actor_id: int | None = None
    lore_id: int | None = None
    comment_id: int | None = None
    type: str = "SYSTEM"
    message: str


class NotificationResponse(BaseModel):
    id: int
    recipient_id: int
    actor_id: int | None
    lore_id: int | None
    comment_id: int | None
    type: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class NotificationListResponse(BaseModel):
    count: int
    results: list[NotificationResponse]