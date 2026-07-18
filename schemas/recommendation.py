from datetime import datetime

from pydantic import BaseModel

from schemas.lore import LoreResponse


class RecommendationResponse(BaseModel):
    id: int
    user_id: int
    lore_id: int
    score: float
    reason: str
    created_at: datetime
    lore: LoreResponse

    model_config = {
        "from_attributes": True,
    }


class RecommendationListResponse(BaseModel):
    count: int
    results: list[RecommendationResponse]
