import httpx

from app.modules.anilist.client import AnilistClient
from app.modules.anilist.dto.user_profile_dto import UserProfileDTO
from app.modules.anilist.profile.queries import VIEWER_PROFILE


async def get_profile(http: httpx.AsyncClient, access_token: str) -> UserProfileDTO:
    client = AnilistClient(http)
    data = await client.graphql(
        access_token=access_token, query=VIEWER_PROFILE, variables={}
    )

    v = data["data"]["Viewer"]

    return UserProfileDTO.from_json(v)
