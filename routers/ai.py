from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from repositories.lore import LoreRepository
from schemas.ai import DiscoverResponse
from schemas.ai import SummaryRequest
from schemas.ai import SummaryResponse
from schemas.ai import ThemeExtractionRequest
from schemas.ai import ThemeExtractionResponse
from schemas.lore import LoreResponse
from services.ai_service import AIService

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


def _validated_text(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Text cannot be blank")
    return cleaned


@router.post("/extract-themes", response_model=ThemeExtractionResponse)
def extract_themes(payload: ThemeExtractionRequest):
    text = _validated_text(payload.text)
    themes = AIService.extract_themes(text)
    return ThemeExtractionResponse(themes=themes[:5])


@router.post("/summarize", response_model=SummaryResponse)
def summarize(payload: SummaryRequest):
    text = _validated_text(payload.text)
    return SummaryResponse(summary=AIService.summarize(text))


@router.get("/discover", response_model=DiscoverResponse)
def discover_feed(
    query: str = Query(...),
    db: Session = Depends(get_db),
):
    cleaned_query = _validated_text(query)
    results = LoreRepository().discover_lore(db, cleaned_query)
    serialized = [LoreResponse.model_validate(item) for item in results]
    return DiscoverResponse(
        query=cleaned_query,
        count=len(serialized),
        results=serialized,
    )


@router.get("/discover/me", response_model=DiscoverResponse)
def discover_for_me(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = LoreRepository()
    own_lore = repo.get_for_user(db, current_user.id)
    if not own_lore:
        return DiscoverResponse(query="", count=0, results=[])

    own_theme_terms = AIService.normalize_terms(
        [item.theme for item in own_lore]
        + [item.profession for item in own_lore]
        + AIService.extract_themes(" ".join(item.lore for item in own_lore))
    )

    candidates = []
    for lore in repo.get_excluding_user(db, current_user.id):
        candidate_terms = AIService.normalize_terms(
            [lore.theme, lore.profession]
            + AIService.extract_themes(f"{lore.question} {lore.lore}")
        )
        overlap = sorted(own_theme_terms.intersection(candidate_terms))
        if not overlap:
            continue
        candidates.append((len(overlap), lore, overlap))

    candidates.sort(key=lambda item: (item[0], item[1].created_at), reverse=True)
    serialized = [LoreResponse.model_validate(item[1]) for item in candidates[:20]]

    return DiscoverResponse(
        query=" ".join(sorted(own_theme_terms)[:5]),
        count=len(serialized),
        results=serialized,
    )
