import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_token
from app.modules.anilist.dto.paginated_activities_dto import (
    PageDTO,
    UserActivitiesDataDTO,
)
from app.modules.anilist.dto.user_profile_dto import UserProfileDTO
from app.modules.anilist.queries.activities import USER_ACTIVITIES
from app.modules.anilist.queries.viewer import VIEWER_PROFILE
from app.modules.auth.anilist_client import AnilistClient
from app.modules.auth.token_repo import get_by_user_id
from app.modules.users.repo import get_by_id


async def viewer(db: Session, *, user_id: int) -> dict:
    row = get_by_user_id(db, user_id)
    if not row:
        raise HTTPException(404, "Anilist token not found")

    access_token = decrypt_token(row.access_token_encrypted)

    async with httpx.AsyncClient(timeout=15) as http:
        client = AnilistClient(http)
        return await client.viewer(access_token)


async def get_profile(http: httpx.AsyncClient, access_token: str) -> UserProfileDTO:
    client = AnilistClient(http)
    data = await client.graphql(
        access_token=access_token, query=VIEWER_PROFILE, variables={}
    )

    v = data["data"]["Viewer"]

    return UserProfileDTO.from_json(v)


async def get_user_activities(
    db: Session,
    http: httpx.AsyncClient,
    access_token: str,
    user_id: int,
    page: int = 1,
    per_page: int = 10,
) -> UserActivitiesDataDTO:
    client = AnilistClient(http)

    data = await client.graphql(
        access_token=access_token,
        query=USER_ACTIVITIES,
        variables={
            "userId": user_id,
            "page": page,
            "perPage": per_page,
        },
    )

    return UserActivitiesDataDTO.from_json(data["data"])
