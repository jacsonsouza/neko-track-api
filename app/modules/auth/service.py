from dataclasses import dataclass

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.crypto import encrypt_token
from app.core.oauth_state import validate_state
from app.core.security import create_app_jwt
from app.modules.auth import token_repo
from app.modules.auth.anilist_client import AnilistClient
from app.modules.users import repo


@dataclass(frozen=True)
class LoginResult:
    app_jwt: str
    user_id: int
    anilist_id: int


async def login_with_anilist_callback(
    db: Session, *, code: str, state: str
) -> LoginResult:
    if not validate_state(state):
        raise HTTPException(400, "Invalid or expired state")

    async with httpx.AsyncClient(timeout=15) as http:
        client = AnilistClient(http)
        access_token = await client.exchange_code_for_token(code)
        viewer = await client.viewer(access_token)

        anilist_id = int(viewer["id"])
        name = str(viewer["name"])

        user = repo.upsert_by_anilist_id(db, anilist_id, name)

        encrypted = encrypt_token(access_token)

        token_repo.upsert_access_token_encrypted(db, user.id, encrypted)

        db.commit()

        token = create_app_jwt(user.id, anilist_id)

        return LoginResult(token, user.id, anilist_id)
