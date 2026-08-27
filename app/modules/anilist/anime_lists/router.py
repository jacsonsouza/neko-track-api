from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Query

from app.core.auth_dep import AuthClaims, get_claims
from app.modules.anilist.anime_lists.service import (
    get_user_anime_lists,
    list_available_to_watch_entries,
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
        return await get_user_anime_lists(
            http=http,
            access_token=access_token,
            user_id=claims.anilist_id,
            status=status,
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
):
    async with httpx.AsyncClient(timeout=15) as http:
        response = await list_available_to_watch_entries(
            http=http,
            access_token=access_token,
            user_id=claims.anilist_id,
        )

    return response.get_filtered_entries()
