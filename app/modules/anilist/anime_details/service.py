import httpx

from app.modules.anilist.anime_details.queries import ANIME_DETAILS
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
