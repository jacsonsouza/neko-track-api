from app.modules.anilist.activities.queries import TOGGLE_LIKE, USER_ACTIVITIES
from app.modules.anilist.activities.schemas import (
    ActivitiesResponse,
    ToggleLikeResponse,
)
from app.modules.anilist.enums import LikeableType
from app.modules.anilist.gateway import AnilistGateway


async def get_user_activities(
    gateway: AnilistGateway,
    access_token: str,
    user_id: int,
    page: int = 1,
    per_page: int = 10,
) -> ActivitiesResponse:
    data = await gateway.graphql(
        access_token=access_token,
        query=USER_ACTIVITIES,
        variables={
            "userId": user_id,
            "page": page,
            "perPage": per_page,
        },
    )

    return ActivitiesResponse.from_json(data)


async def toggle_activity_like(
    gateway: AnilistGateway,
    access_token: str,
    activity_id: int,
    type: LikeableType,
) -> ToggleLikeResponse:
    data = await gateway.graphql(
        access_token=access_token,
        query=TOGGLE_LIKE,
        variables={"id": activity_id, "type": type.value},
    )

    return ToggleLikeResponse.from_graphql(data)
