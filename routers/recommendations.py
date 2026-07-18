from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from schemas.recommendation import RecommendationListResponse
from schemas.recommendation import RecommendationResponse
from services.recommendation_service import RecommendationService

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


def _serialize(items) -> RecommendationListResponse:
    serialized = [RecommendationResponse.model_validate(item) for item in items]
    return RecommendationListResponse(
        count=len(serialized),
        results=serialized,
    )


@router.get("", response_model=RecommendationListResponse)
def get_recommendations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _serialize(
        RecommendationService.get_recommendations(db, current_user),
    )


@router.get("/refresh", response_model=RecommendationListResponse)
def refresh_recommendations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _serialize(
        RecommendationService.refresh_recommendations(db, current_user),
    )


@router.delete("")
def clear_recommendations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = RecommendationService.clear_recommendations(db, current_user)
    return {
        "deleted": deleted,
    }


@router.delete("/{recommendation_id}")
def dismiss_recommendation(
    recommendation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = RecommendationService.delete_recommendation(db, current_user, recommendation_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {
        "deleted": deleted,
    }
