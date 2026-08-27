import httpx

from app.modules.anilist.anime_lists.models.anilist_response_model import (
    AniListResponse,
)
from app.modules.anilist.anime_lists.queries import (
    AVAILABLE_TO_WATCH_ENTRIES,
    USER_ANIME_LISTS,
)
from app.modules.anilist.client import AnilistClient


async def get_user_anime_lists(
    http: httpx.AsyncClient,
    access_token: str,
    user_id: int,
    status: str,
    page: int = 1,
    per_page: int = 10,
):
    client = AnilistClient(http)

    return await client.graphql(
        access_token=access_token,
        query=USER_ANIME_LISTS,
        variables={
            "userId": user_id,
            "status": status,
            "page": page,
            "perPage": per_page,
        },
    )


async def list_available_to_watch_entries(
    http: httpx.AsyncClient,
    access_token: str,
    user_id: int,
) -> AniListResponse:
    client = AnilistClient(http)

    json = await client.graphql(
        access_token=access_token,
        query=AVAILABLE_TO_WATCH_ENTRIES,
        variables={
            "userId": user_id,
        },
    )

    return AniListResponse.from_json(json)
