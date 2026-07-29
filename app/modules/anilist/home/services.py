import httpx

from app.modules.anilist.client import AnilistClient
from app.modules.anilist.home.queries import (
    UPDATE_ANIME_PROGRESS,
    USER_WATCHING_ANIME_LISTS,
)


async def get_user_watching_list(
    http: httpx.AsyncClient,
    access_token: str,
    user_id: int,
    page: int = 10,
    per_page: int = 10,
):
    client = AnilistClient(http)

    return await client.graphql(
        access_token=access_token,
        query=USER_WATCHING_ANIME_LISTS,
        variables={
            "userId": user_id,
            "page": page,
            "perPage": per_page,
        },
    )


async def update_anime_progress(
    http: httpx.AsyncClient,
    access_token: str,
    media_id: int,
    progress: int,
):
    client = AnilistClient(http)

    return await client.graphql(
        access_token=access_token,
        query=UPDATE_ANIME_PROGRESS,
        variables={
            "mediaId": media_id,
            "progress": progress,
        },
    )
