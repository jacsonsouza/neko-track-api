from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Query

from app.core.auth_dep import AuthClaims, get_claims
from app.modules.anilist.activities.dto.paginated_activities_dto import (
    UserActivitiesDataDTO,
)
from app.modules.anilist.activities.service import (
    get_user_activities,
    toggle_activity_like,
)
from app.modules.anilist.replies.service import get_activity_replies, post_reply
from app.modules.auth.dependencies import get_current_anilist_access_token

activities_router = APIRouter(prefix="/api/v1/activities", tags=["activities"])
my_activities_router = APIRouter(prefix="/api/v1/me/activities", tags=["activities"])


@my_activities_router.get("", response_model=UserActivitiesDataDTO)
async def user_activities(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    claims: Annotated[AuthClaims, Depends(get_claims)] = None,
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
) -> UserActivitiesDataDTO:
    async with httpx.AsyncClient(timeout=15) as http:
        return await get_user_activities(
            http, access_token, claims.anilist_id, page, per_page
        )


@activities_router.post("/{activity_id}/like")
async def toggle_like(
    activity_id: int,
    type: str,
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
):
    async with httpx.AsyncClient(timeout=15) as http:
        return await toggle_activity_like(http, access_token, activity_id, type)


@activities_router.get("/{activity_id}/replies")
async def replies(
    activity_id: int,
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
):
    async with httpx.AsyncClient(timeout=15) as http:
        return await get_activity_replies(http, access_token, activity_id)


@activities_router.post("/{activity_id}/replies")
async def reply(
    activity_id: int,
    text: str,
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
):
    async with httpx.AsyncClient(timeout=15) as http:
        return await post_reply(http, access_token, activity_id, text)
