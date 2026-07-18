# schemas/bookmark.py

from pydantic import BaseModel


class BookmarkResponse(BaseModel):
    id: int
    user_id: int
    lore_id: int

    model_config = {
        "from_attributes": True
    }