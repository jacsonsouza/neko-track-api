import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_token
from app.modules.auth.anilist_client import AnilistClient
from app.modules.auth.token_repo import get_by_user_id


async def viewer(db: Session, *, user_id: int) -> dict:
    row = get_by_user_id(db, user_id)
    if not row:
        raise HTTPException(404, "Anilist token not found")

    access_token = decrypt_token(row.access_token_encrypted)

    async with httpx.AsyncClient(timeout=15) as http:
        client = AnilistClient(http)
        return await client.viewer(access_token)
