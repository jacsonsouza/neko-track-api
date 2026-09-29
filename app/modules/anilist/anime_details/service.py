import httpx

from app.modules.anilist.anime_details.dto.anime_resource import AnimeResource
from app.modules.anilist.anime_details.queries import ANIME_DETAILS, ANIMES
from app.modules.anilist.anime_details.schemas import (
    AnimeDetailsResponse,
    AnimeSearchResponse,
)
from app.modules.anilist.client import AnilistClient


async def get_animes(
    http: httpx.AsyncClient,
    access_token: str,
    search: str,
    page: int,
    per_page: int,
) -> AnimeSearchResponse:
    client = AnilistClient(http)

    payload = await client.graphql(
        access_token=access_token,
        query=ANIMES,
        variables={"search": search, "page": page, "perPage": per_page},
    )

    return AnimeSearchResponse.from_graphql(payload)


async def get_anime_details(
    http: httpx.AsyncClient,
    access_token: str,
    anime_id: int,
) -> AnimeDetailsResponse:
    client = AnilistClient(http)

    payload = await client.graphql(
        access_token=access_token,
        query=ANIME_DETAILS,
        variables={"id": anime_id},
    )

    return AnimeResource.model_validate(payload["data"]).media
