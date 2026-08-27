import httpx
from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, Field

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.anime_details.dto.anime_progress_dto import AnimeProgressDTO
from app.modules.anilist.anime_details.dto.anime_resource import AnimeDetailsDTO
from app.modules.anilist.anime_details.service import (
    get_anime_details,
    update_episode_progress,
    update_progress,
)
from app.modules.auth.token_repo import get_anilist_access_token_for_user

router = APIRouter(prefix="/anilist/animes", tags=["anilist", "details"])


@router.get("/{anime_id}")
async def anime_details(
    anime_id: int,
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
) -> AnimeDetailsDTO:
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await get_anime_details(http, access_token, anime_id)


@router.patch("/{anime_id}")
async def anime_progress(
    anime_id: int,
    data: AnimeProgressDTO,
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await update_progress(http, access_token, anime_id, data)


class UpdateProgressRequest(BaseModel):
    progress: int = Field(..., gt=0, description="Anime episodes progress")


@router.patch("/{anime_id}/episodes")
async def episodes_progress(
    anime_id: int = Path(..., gt=0, description="Anime ID"),
    body: UpdateProgressRequest = None,
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await update_episode_progress(
            http, access_token, anime_id, body.progress
        )
