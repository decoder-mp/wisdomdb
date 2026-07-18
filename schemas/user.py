"""User schemas."""

from datetime import datetime

from pydantic import BaseModel
from pydantic import EmailStr


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }