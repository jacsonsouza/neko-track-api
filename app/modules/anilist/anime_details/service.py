import httpx

from app.modules.anilist.anime_details.dto.anime_progress_dto import (
    AnimeProgressDTO,
    FuzzyDateDTO,
)
from app.modules.anilist.anime_details.queries import (
    ANIME_DETAILS,
    SAVE_ANIME_PROGRESS,
)
from app.modules.anilist.client import AnilistClient


async def get_anime_details(
    http: httpx.AsyncClient,
    access_token: str,
    anime_id: int,
):
    client = AnilistClient(http)

    return await client.graphql(
        access_token=access_token,
        query=ANIME_DETAILS,
        variables={"id": anime_id},
    )


async def update_progress(
    http: httpx.AsyncClient, access_token: str, anime_id: int, data: AnimeProgressDTO
):
    client = AnilistClient(http)

    return await client.graphql(
        access_token=access_token,
        query=SAVE_ANIME_PROGRESS,
        variables={
            "mediaId": anime_id,
            "status": data.status,
            "score": data.score,
            "progress": data.progress,
            "startedAt": FuzzyDateDTO.from_date(data.started_at),
            "completedAt": FuzzyDateDTO.from_date(data.completed_at),
        },
    )
