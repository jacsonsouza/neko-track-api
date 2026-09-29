from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Query

from app.core.auth_dep import AuthClaims, get_claims
from app.modules.anilist.anime_lists.schemas import (
    AnimeListEntryResponse,
    AnimeListResponse,
    AvailableToWatchResponse,
    UpdateAnimeListEntryRequest,
)
from app.modules.anilist.anime_lists.service import (
    anime_list_entries,
    available_to_watch_entries,
    update_anime_list_entry,
)
from app.modules.anilist.enums import MediaListStatus
from app.modules.auth.dependencies import get_current_anilist_access_token

router = APIRouter(prefix="/api/v1/me/anime-list", tags=["anime-list"])


@router.get("", response_model=AnimeListResponse)
async def get_my_anime_list(
    status: MediaListStatus = Query(..., description="AniList media list status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    claims: Annotated[AuthClaims, Depends(get_claims)] = None,
    access_token: Annotated[
        str,
        Depends(get_current_anilist_access_token),
    ] = None,
) -> AnimeListResponse:
    async with httpx.AsyncClient(timeout=15) as http:
        return await anime_list_entries(
            http=http,
            access_token=access_token,
            anilist_user_id=claims.anilist_id,
            list_status=status,
            page=page,
            per_page=per_page,
        )


@router.get("/available-to-watch", response_model=AvailableToWatchResponse)
async def get_my_available_to_watch_animes(
    claims: Annotated[AuthClaims, Depends(get_claims)] = None,
    access_token: Annotated[
        str,
        Depends(get_current_anilist_access_token),
    ] = None,
) -> AvailableToWatchResponse:
    async with httpx.AsyncClient(timeout=15) as http:
        return await available_to_watch_entries(
            http=http,
            access_token=access_token,
            anilist_user_id=claims.anilist_id,
        )


@router.patch("/{anime_id}", response_model=AnimeListEntryResponse)
async def update_my_anime_list_entry(
    anime_id: int,
    body: UpdateAnimeListEntryRequest,
    anilist_access_token: Annotated[
        str, Depends(get_current_anilist_access_token)
    ] = None,
) -> AnimeListEntryResponse:
    async with httpx.AsyncClient(timeout=15) as http:
        return await update_anime_list_entry(http, anilist_access_token, anime_id, body)
