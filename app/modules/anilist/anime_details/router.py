from typing import Annotated

import httpx
from fastapi import APIRouter, Depends

from app.modules.anilist.anime_details.dto.anime_resource import AnimeDetailsDTO
from app.modules.anilist.anime_details.service import get_anime_details
from app.modules.auth.dependencies import get_current_anilist_access_token

animes_router = APIRouter(prefix="/api/v1/animes", tags=["anilist", "details"])


@animes_router.get("/{anime_id}")
async def anime_details(
    anime_id: int,
    anilist_access_token: Annotated[
        str, Depends(get_current_anilist_access_token)
    ] = None,
) -> AnimeDetailsDTO:
    async with httpx.AsyncClient(timeout=15) as http:
        return await get_anime_details(http, anilist_access_token, anime_id)
