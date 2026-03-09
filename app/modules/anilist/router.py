import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.dto.paginated_activities_dto import UserActivitiesDataDTO
from app.modules.anilist.dto.user_profile_dto import UserProfileDTO
from app.modules.anilist.service import (
    get_activity_replies,
    get_profile,
    get_user_activities,
    post_reply,
    remove_reply,
    toggle_activity_like,
    viewer,
)
from app.modules.auth.token_repo import get_anilist_access_token_for_user

router = APIRouter(prefix="/anilist", tags=["anilist"])


@router.get("/viewer")
async def get_viewer(
    claims: AuthClaims = Depends(get_claims), db: Session = Depends(get_db)
):
    return await viewer(db, user_id=claims.user_id)


@router.get("/profile", response_model=UserProfileDTO)
async def profile(
    claims: AuthClaims = Depends(get_claims), db=Depends(get_db)
) -> UserProfileDTO:
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await get_profile(http, access_token)


@router.get("/user/activities", response_model=UserActivitiesDataDTO)
async def user_activities(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
) -> UserActivitiesDataDTO:
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await get_user_activities(
            http, access_token, claims.anilist_id, page, per_page
        )


@router.post("/activities/{activity_id}/like")
async def toggle_like(
    activity_id: int,
    type: str,
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await toggle_activity_like(http, access_token, activity_id, type)


@router.get("/activities/{activity_id}/replies")
async def replies(
    activity_id: int, claims: AuthClaims = Depends(get_claims), db=Depends(get_db)
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await get_activity_replies(http, access_token, activity_id)


@router.post("/activities/{activity_id}/replies")
async def reply(
    activity_id: int,
    text: str,
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await post_reply(http, access_token, activity_id, text)


@router.delete("/replies/{reply_id}")
async def delete_reply(
    reply_id: int, claims: AuthClaims = Depends(get_claims), db=Depends(get_db)
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await remove_reply(http, access_token, reply_id)


@router.post("/replies/{reply_id}/toggle-like")
async def toggle_reply_like(
    reply_id: int,
    type: str,
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await toggle_activity_like(http, access_token, reply_id, type)
