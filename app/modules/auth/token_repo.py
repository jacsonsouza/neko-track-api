from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_token
from app.db.models.anilist_token import AnilistToken
from app.db.models.user import User


def get_by_user_id(db: Session, user_id: int) -> AnilistToken | None:
    return db.query(AnilistToken).filter(AnilistToken.user_id == user_id).one_or_none()


def upsert_access_token_encrypted(
    db: Session, user_id: int, access_token_encrypted: str
) -> None:
    row = get_by_user_id(db, user_id)
    if row:
        row.access_token_encrypted = access_token_encrypted
        return

    db.add(AnilistToken(user_id=user_id, access_token_encrypted=access_token_encrypted))


def get_anilist_access_token_for_user(db: Session, user_id: int) -> str:
    token_row = (db.query(AnilistToken).filter(AnilistToken.user_id == user_id)).first()

    if not token_row:
        raise HTTPException(404, "Anilist token not found for user")

    return decrypt_token(token_row.access_token_encrypted)
