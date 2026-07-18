"""User repository."""

from sqlalchemy.orm import Session

from models.user import User


def create_user(
    db: Session,
    username: str,
    email: str,
    hashed_password: str,
    is_admin: bool = False,
):
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_admin=is_admin,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_email(
    db: Session,
    email: str,
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

def get_user_by_id(
    db: Session,
    user_id: int,
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

def list_users(
    db: Session,
):
    return (
        db.query(User)
        .all()
    )


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()