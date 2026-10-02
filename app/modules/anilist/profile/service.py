from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_token
from app.modules.anilist.gateway import AnilistGateway
from app.modules.anilist.profile.queries import VIEWER_PROFILE
from app.modules.anilist.profile.schemas import UserProfileResponse, ViewerResponse
from app.modules.auth.token_repo import get_by_user_id


async def viewer(
    gateway: AnilistGateway, db: Session, *, user_id: int
) -> ViewerResponse:
    row = get_by_user_id(db, user_id)
    if not row:
        raise HTTPException(404, "Anilist token not found")

    access_token = decrypt_token(row.access_token_encrypted)

    return ViewerResponse.from_json(await gateway.viewer(access_token))


async def get_profile(
    gateway: AnilistGateway, access_token: str
) -> UserProfileResponse:
    data = await gateway.graphql(
        access_token=access_token, query=VIEWER_PROFILE, variables={}
    )

    return UserProfileResponse.from_json(data["Viewer"])
