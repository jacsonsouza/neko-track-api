from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Query

from app.modules.anilist.anime_details.dto.anime_resource import AnimeDetailsDTO
from app.modules.anilist.anime_details.service import get_anime_details, get_animes
from app.modules.auth.dependencies import get_current_anilist_access_token

animes_router = APIRouter(prefix="/api/v1/animes", tags=["anilist", "details"])


@animes_router.get("")
async def animes(
    search: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    anilist_access_token: Annotated[
        str, Depends(get_current_anilist_access_token)
    ] = None,
):
    async with httpx.AsyncClient(timeout=15) as http:
        return await get_animes(http, anilist_access_token, search, page, per_page)


@animes_router.get("/{anime_id}")
async def anime_details(
    anime_id: int,
    anilist_access_token: Annotated[
        str, Depends(get_current_anilist_access_token)
    ] = None,
) -> AnimeDetailsDTO:
    async with httpx.AsyncClient(timeout=15) as http:
        return await get_anime_details(http, anilist_access_token, anime_id)
