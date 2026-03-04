from sqlalchemy.orm import Session

from app.db.models.user import User


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).one_or_none()


def get_by_anilist_id(db: Session, anilist_id: int) -> User | None:
    return db.query(User).filter(User.anilist_id == anilist_id).one_or_none()


def upsert_by_anilist_id(db: Session, anilist_id: int, name: str) -> User:
    user = get_by_anilist_id(db, anilist_id)
    if user:
        user.name = name
        return user

    user = User(anilist_id=anilist_id, name=name)
    db.add(user)
    db.flush()

    return user
