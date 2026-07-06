import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.anime_search.service import anime_search
from app.modules.auth.token_repo import get_anilist_access_token_for_user

router = APIRouter(prefix="/anilist/anime", tags=["search"])


@router.get("/search")
async def search(
    search: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    claims: AuthClaims = Depends(get_claims),
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await anime_search(http, access_token, search, page, per_page)
