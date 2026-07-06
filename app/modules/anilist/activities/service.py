import httpx

from app.modules.anilist.activities.dto.paginated_activities_dto import (
    UserActivitiesDataDTO,
)
from app.modules.anilist.activities.queries import TOGGLE_LIKE, USER_ACTIVITIES
from app.modules.anilist.client import AnilistClient


async def get_user_activities(
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


async def toggle_activity_like(
    http: httpx.AsyncClient, access_token: str, activity_id: int, type: str
):
    client = AnilistClient(http)

    return await client.graphql(
        access_token=access_token,
        query=TOGGLE_LIKE,
        variables={"id": activity_id, "type": type},
    )
