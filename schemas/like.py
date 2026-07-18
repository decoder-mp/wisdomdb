from pydantic import BaseModel


class LikeResponse(BaseModel):
    id: int
    user_id: int
    lore_id: int

    model_config = {
        "from_attributes": True,
    }


class LikeCountResponse(BaseModel):
    lore_id: int
    likes: int

    model_config = {
        "from_attributes": True,
    }