from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from dependencies import get_current_user
from repositories.wisdom_repository import WisdomRepository
from schemas.wisdom import WisdomCreate, WisdomRead, WisdomUpdate
from models.user import User

router = APIRouter(prefix="/wisdom", tags=["wisdom"])

@router.post("/", response_model=WisdomRead)
def create_wisdom(wisdom: WisdomCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = WisdomRepository(db)
    return repo.create(wisdom, current_user.id)

@router.get("/", response_model=list[WisdomRead])
def read_own_wisdom(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = WisdomRepository(db)
    return repo.get_by_owner(current_user.id, skip=skip, limit=limit)

@router.get("/{wisdom_id}", response_model=WisdomRead)
def read_wisdom(wisdom_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = WisdomRepository(db)
    wisdom = repo.get_by_id(wisdom_id)
    if wisdom is None or wisdom.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Wisdom entry not found")
    return wisdom

@router.put("/{wisdom_id}", response_model=WisdomRead)
def update_wisdom(wisdom_id: int, wisdom_update: WisdomUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = WisdomRepository(db)
    wisdom = repo.get_by_id(wisdom_id)
    if wisdom is None or wisdom.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Wisdom entry not found")
    return repo.update(wisdom_id, wisdom_update)

@router.delete("/{wisdom_id}")
def delete_wisdom(wisdom_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = WisdomRepository(db)
    wisdom = repo.get_by_id(wisdom_id)
    if wisdom is None or wisdom.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Wisdom entry not found")
    repo.delete(wisdom_id)
    return {"detail": "Deleted successfully"}