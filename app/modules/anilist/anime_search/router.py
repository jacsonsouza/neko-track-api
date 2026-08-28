from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Query

from app.modules.anilist.anime_search.service import anime_search
from app.modules.auth.dependencies import get_current_anilist_access_token

router = APIRouter(prefix="/anilist/anime", tags=["search"])


@router.get("/search")
async def search(
    search: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    anilist_access_token: Annotated[
        str, Depends(get_current_anilist_access_token)
    ] = None,
):
    async with httpx.AsyncClient(timeout=15) as http:
        return await anime_search(http, anilist_access_token, search, page, per_page)
