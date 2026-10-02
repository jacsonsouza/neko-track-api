from app.modules.anilist.anime_details.dto.anime_resource import AnimeResource
from app.modules.anilist.anime_details.queries import ANIME_DETAILS, ANIMES
from app.modules.anilist.anime_details.schemas import (
    AnimeDetailsResponse,
    AnimeSearchResponse,
)
from app.modules.anilist.gateway import AnilistGateway


async def get_animes(
    gateway: AnilistGateway,
    access_token: str,
    search: str,
    page: int,
    per_page: int,
) -> AnimeSearchResponse:
    data = await gateway.graphql(
        access_token=access_token,
        query=ANIMES,
        variables={"search": search, "page": page, "perPage": per_page},
    )

    return AnimeSearchResponse.from_graphql(data)


async def get_anime_details(
    gateway: AnilistGateway,
    access_token: str,
    anime_id: int,
) -> AnimeDetailsResponse:
    data = await gateway.graphql(
        access_token=access_token,
        query=ANIME_DETAILS,
        variables={"id": anime_id},
    )

    return AnimeResource.model_validate(data).media
