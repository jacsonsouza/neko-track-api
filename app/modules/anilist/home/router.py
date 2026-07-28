import httpx
from fastapi import APIRouter, Depends, Query

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.home.services import get_user_watching_list
from app.modules.auth.token_repo import get_anilist_access_token_for_user

router = APIRouter(prefix="anilist/user", tags=["anilist", "user", "current"])


@router.get("/{user_id}/watching")
async def user_watching(
    user_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
):
    access_token = get_anilist_access_token_for_user(db, user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await get_user_watching_list(
            http,
            access_token,
            claims.anilist_id,
            page,
            per_page,
        )
