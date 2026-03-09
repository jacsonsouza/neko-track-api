import httpx
from fastapi import APIRouter, Depends

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.activities.service import toggle_activity_like
from app.modules.anilist.replies.service import remove_reply
from app.modules.auth.token_repo import get_anilist_access_token_for_user

router = APIRouter(prefix="/anilist/replies", tags=["anilist"])


@router.delete("/{reply_id}")
async def delete_reply(
    reply_id: int, claims: AuthClaims = Depends(get_claims), db=Depends(get_db)
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await remove_reply(http, access_token, reply_id)


@router.post("/{reply_id}/toggle-like")
async def toggle_reply_like(
    reply_id: int,
    type: str,
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await toggle_activity_like(http, access_token, reply_id, type)
