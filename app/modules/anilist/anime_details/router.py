import httpx
from fastapi import APIRouter, Depends

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.anime_details.dto.anime_resource import AnimeDetailsDTO
from app.modules.anilist.anime_details.service import (
    get_anime_details,
)
from app.modules.auth.token_repo import get_anilist_access_token_for_user

animes_router = APIRouter(prefix="/api/v1/animes", tags=["anilist", "details"])


@animes_router.get("/{anime_id}")
async def anime_details(
    anime_id: int,
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
) -> AnimeDetailsDTO:
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await get_anime_details(http, access_token, anime_id)
