from pydantic import BaseModel
from typing import List

from schemas.lore import LoreResponse


class ThemeExtractionRequest(BaseModel):
    text: str


class ThemeExtractionResponse(BaseModel):
    themes: List[str]


class SummaryRequest(BaseModel):
    text: str


class SummaryResponse(BaseModel):
    summary: str


class DiscoveryRequest(BaseModel):
    query: str


class DiscoverResponse(BaseModel):
    query: str
    count: int
    results: list[LoreResponse]