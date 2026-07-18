from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user

from repositories.lore import LoreRepository
from schemas.lore import LoreCreate, LoreUpdate, LoreResponse
from services.recommendation_service import RecommendationService

router = APIRouter(prefix="/lore", tags=["Lore"])
repo = LoreRepository()


# CREATE
@router.post("/", response_model=LoreResponse)
def create_lore(
    payload: LoreCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = payload.model_dump()
    data["user_id"] = current_user.id

    created_lore = repo.create(db, data)
    RecommendationService.notify_interested_users_for_new_lore(db, created_lore)
    return created_lore


# LIST
@router.get("/", response_model=list[LoreResponse])
def list_lore(db: Session = Depends(get_db)):
    return repo.get_all(db)


# GET ONE
@router.get("/{lore_id}", response_model=LoreResponse)
def get_lore(lore_id: int, db: Session = Depends(get_db)):
    lore = repo.get_by_id(db, lore_id)

    if not lore:
        raise HTTPException(404, "Lore not found")

    return LoreResponse.model_validate(lore)


# UPDATE (safe partial update)
@router.put("/{lore_id}", response_model=LoreResponse)
def update_lore(
    lore_id: int,
    payload: LoreUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lore = repo.get_by_id(db, lore_id)

    if not lore:
        raise HTTPException(404, "Lore not found")

    if lore.user_id != current_user.id:
        raise HTTPException(403, "Not your lore entry")

    return repo.update(db, lore, payload.model_dump(exclude_unset=True))


# 🔥 DELETE
@router.delete("/{lore_id}")
def delete_lore(
    lore_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lore = repo.get_by_id(db, lore_id)

    if not lore:
        raise HTTPException(404, "Lore not found")

    if lore.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(403, "Not your lore entry")

    repo.delete(db, lore)

    return {"message": "Lore deleted"}