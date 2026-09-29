import httpx

from app.modules.anilist.anime_lists.models.anilist_media_list_response import (
    AniListMediaListResponse,
)
from app.modules.anilist.anime_lists.queries import (
    ANIME_LIST_ENTRIES,
    AVAILABLE_TO_WATCH_ENTRIES,
    SAVE_ANIME_LIST_ENTRY,
)
from app.modules.anilist.anime_lists.schemas import (
    AnimeListEntryItem,
    AnimeListEntryResponse,
    AnimeListResponse,
    AvailableToWatchResponse,
    UpdateAnimeListEntryRequest,
)
from app.modules.anilist.client import AnilistClient
from app.modules.anilist.enums import MediaListStatus


async def anime_list_entries(
    http: httpx.AsyncClient,
    access_token: str,
    anilist_user_id: int,
    list_status: MediaListStatus,
    page: int = 1,
    per_page: int = 10,
) -> AnimeListResponse:
    client = AnilistClient(http)

    payload = await client.graphql(
        access_token=access_token,
        query=ANIME_LIST_ENTRIES,
        variables={
            "userId": anilist_user_id,
            "status": list_status.value,
            "page": page,
            "perPage": per_page,
        },
    )

    return AnimeListResponse.from_graphql(payload)


async def available_to_watch_entries(
    http: httpx.AsyncClient,
    access_token: str,
    anilist_user_id: int,
) -> AvailableToWatchResponse:
    client = AnilistClient(http)

    payload = await client.graphql(
        access_token=access_token,
        query=AVAILABLE_TO_WATCH_ENTRIES,
        variables={
            "userId": anilist_user_id,
        },
    )

    # Payload model keeps the "available to watch" domain rules; the router
    # answers with the public schema only.
    response = AniListMediaListResponse.from_json(payload)
    entries = [
        AnimeListEntryItem.model_validate(entry.model_dump(by_alias=True))
        for entry in response.get_available_to_watch_entries()
    ]

    return AvailableToWatchResponse(entries=entries)


async def update_anime_list_entry(
    http: httpx.AsyncClient,
    access_token: str,
    anime_id: int,
    data: UpdateAnimeListEntryRequest,
) -> AnimeListEntryResponse:
    client = AnilistClient(http)

    variables = {
        "mediaId": anime_id,
        **data.to_anilist_variables(),
    }

    payload = await client.graphql(
        access_token=access_token,
        query=SAVE_ANIME_LIST_ENTRY,
        variables=variables,
    )

    return AnimeListEntryResponse.model_validate(
        payload["data"]["SaveMediaListEntry"]
    )
