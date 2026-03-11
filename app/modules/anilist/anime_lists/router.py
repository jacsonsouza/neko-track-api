import httpx
from fastapi import APIRouter, Depends, Query

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.anime_lists.service import get_user_anime_lists
from app.modules.auth.token_repo import get_anilist_access_token_for_user

router = APIRouter(prefix="/anilist/user", tags=["anilist", "lists"])


@router.get("/{user_id}/watch-lists")
async def watch_lists(
    user_id: int,
    status: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
):
    access_token = get_anilist_access_token_for_user(db, user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return get_user_anime_lists(
            http, access_token, claims.anilist_id, status, page, per_page
        )
