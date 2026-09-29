import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_token
from app.modules.anilist.client import AnilistClient
from app.modules.anilist.profile.queries import VIEWER_PROFILE
from app.modules.anilist.profile.schemas import UserProfileResponse, ViewerResponse
from app.modules.auth.token_repo import get_by_user_id


async def viewer(db: Session, *, user_id: int) -> ViewerResponse:
    row = get_by_user_id(db, user_id)
    if not row:
        raise HTTPException(404, "Anilist token not found")

    access_token = decrypt_token(row.access_token_encrypted)

    async with httpx.AsyncClient(timeout=15) as http:
        client = AnilistClient(http)
        return ViewerResponse.from_json(await client.viewer(access_token))


async def get_profile(
    http: httpx.AsyncClient, access_token: str
) -> UserProfileResponse:
    client = AnilistClient(http)
    data = await client.graphql(
        access_token=access_token, query=VIEWER_PROFILE, variables={}
    )

    return UserProfileResponse.from_json(data["data"]["Viewer"])
