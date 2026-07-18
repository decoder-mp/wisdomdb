from pydantic import BaseModel
from datetime import datetime


class ReportCreate(BaseModel):
    lore_id: int
    reason: str
    details: str = ""


class ReportResponse(BaseModel):
    id: int
    reporter_id: int
    lore_id: int
    reason: str
    details: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }