from fastapi import APIRouter, Depends
import httpx

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.anime_details.service import get_anime_details
from app.modules.auth.token_repo import get_anilist_access_token_for_user

router = APIRouter(prefix="/anilist/animes", tags=["anilist", "details"])


@router.get("/{anime_id}")
async def anime_details(
    anime_id: int,
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await get_anime_details(http, access_token, anime_id)
