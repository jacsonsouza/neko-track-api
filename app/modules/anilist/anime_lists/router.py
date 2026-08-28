from typing import Annotated, List

import httpx
from fastapi import APIRouter, Depends, Query

from app.core.auth_dep import AuthClaims, get_claims
from app.modules.anilist.anime_lists.models.anilist_media_list_response import (
    AnimeListEntry,
)
from app.modules.anilist.anime_lists.schemas import (
    AnimeListEntryResponse,
    UpdateAnimeListEntryRequest,
)
from app.modules.anilist.anime_lists.service import (
    anime_list_entries,
    available_to_watch_entries,
    update_anime_list_entry,
)
from app.modules.auth.dependencies import get_current_anilist_access_token

router = APIRouter(
    prefix="/api/v1/me/anime-list",
    tags=["anime-list"],
)


@router.get("")
async def get_my_anime_list(
    status: str = Query(..., description="AniList media-list status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    claims: Annotated[AuthClaims, Depends(get_claims)] = None,
    access_token: Annotated[
        str,
        Depends(get_current_anilist_access_token),
    ] = None,
):
    async with httpx.AsyncClient(timeout=15) as http:
        return await anime_list_entries(
            http=http,
            access_token=access_token,
            anilist_user_id=claims.anilist_id,
            list_status=status,
            page=page,
            per_page=per_page,
        )


@router.get("/available-to-watch")
async def get_my_available_to_watch_animes(
    claims: Annotated[AuthClaims, Depends(get_claims)] = None,
    access_token: Annotated[
        str,
        Depends(get_current_anilist_access_token),
    ] = None,
) -> List[AnimeListEntry]:
    async with httpx.AsyncClient(timeout=15) as http:
        response = await available_to_watch_entries(
            http=http,
            access_token=access_token,
            anilist_user_id=claims.anilist_id,
        )

    return response.get_available_to_watch_entries()


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
