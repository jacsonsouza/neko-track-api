import httpx

from app.modules.anilist.anime_lists.models.anilist_media_list_response import (
    AniListMediaListResponse,
)
from app.modules.anilist.anime_lists.queries import (
    ANIME_LIST_ENTRIES,
    AVAILABLE_TO_WATCH_ENTRIES,
)
from app.modules.anilist.client import AnilistClient


async def anime_list_entries(
    http: httpx.AsyncClient,
    access_token: str,
    anilist_user_id: int,
    list_status: str,
    page: int = 1,
    per_page: int = 10,
):
    client = AnilistClient(http)

    return await client.graphql(
        access_token=access_token,
        query=ANIME_LIST_ENTRIES,
        variables={
            "userId": anilist_user_id,
            "status": list_status,
            "page": page,
            "perPage": per_page,
        },
    )


async def available_to_watch_entries(
    http: httpx.AsyncClient,
    access_token: str,
    anilist_user_id: int,
) -> AniListMediaListResponse:
    client = AnilistClient(http)

    json = await client.graphql(
        access_token=access_token,
        query=AVAILABLE_TO_WATCH_ENTRIES,
        variables={
            "userId": anilist_user_id,
        },
    )

    return AniListMediaListResponse.from_json(json)
