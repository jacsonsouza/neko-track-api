from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.modules.anilist.anime_details.schemas import (
    AnimeDetailsResponse,
    AnimeSearchResponse,
)
from app.modules.anilist.anime_details.service import get_anime_details, get_animes
from app.modules.anilist.gateway import AnilistGateway, get_anilist_gateway
from app.modules.auth.dependencies import get_current_anilist_access_token

animes_router = APIRouter(prefix="/api/v1/animes", tags=["anilist", "details"])


@animes_router.get("", response_model=AnimeSearchResponse)
async def animes(
    search: str,
    gateway: Annotated[AnilistGateway, Depends(get_anilist_gateway)],
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    anilist_access_token: Annotated[
        str, Depends(get_current_anilist_access_token)
    ] = None,
) -> AnimeSearchResponse:
    return await get_animes(gateway, anilist_access_token, search, page, per_page)


@animes_router.get("/{anime_id}", response_model=AnimeDetailsResponse)
async def anime_details(
    anime_id: int,
    gateway: Annotated[AnilistGateway, Depends(get_anilist_gateway)],
    anilist_access_token: Annotated[
        str, Depends(get_current_anilist_access_token)
    ] = None,
) -> AnimeDetailsResponse:
    return await get_anime_details(gateway, anilist_access_token, anime_id)
