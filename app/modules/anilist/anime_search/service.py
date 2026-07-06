import httpx

from app.modules.anilist.anime_search.queries import ANIME_SEARCH
from app.modules.anilist.client import AnilistClient


async def anime_search(
    http: httpx.AsyncClient, access_token: str, search: str, page: int, per_page: int
):
    client = AnilistClient(http)

    return await client.graphql(
        access_token=access_token,
        query=ANIME_SEARCH,
        variables={"search": search, "page": page, "perPage": per_page},
    )
