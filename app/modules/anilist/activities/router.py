from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.auth_dep import AuthClaims, get_claims
from app.modules.anilist.activities.schemas import (
    ActivitiesResponse,
    CreateActivityReplyRequest,
    ToggleLikeResponse,
)
from app.modules.anilist.activities.service import (
    get_user_activities,
    toggle_activity_like,
)
from app.modules.anilist.enums import LikeableType
from app.modules.anilist.gateway import AnilistGateway, get_anilist_gateway
from app.modules.anilist.replies.schemas import (
    ActivityRepliesResponse,
    ActivityReplyResponse,
)
from app.modules.anilist.replies.service import get_activity_replies, post_reply
from app.modules.auth.dependencies import get_current_anilist_access_token

activities_router = APIRouter(prefix="/api/v1/activities", tags=["activities"])
my_activities_router = APIRouter(prefix="/api/v1/me/activities", tags=["activities"])


@my_activities_router.get("", response_model=ActivitiesResponse)
async def user_activities(
    gateway: Annotated[AnilistGateway, Depends(get_anilist_gateway)],
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    claims: Annotated[AuthClaims, Depends(get_claims)] = None,
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
) -> ActivitiesResponse:
    return await get_user_activities(
        gateway, access_token, claims.anilist_id, page, per_page
    )


@activities_router.post("/{activity_id}/like", response_model=ToggleLikeResponse)
async def toggle_like(
    activity_id: int,
    type: LikeableType,
    gateway: Annotated[AnilistGateway, Depends(get_anilist_gateway)],
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
) -> ToggleLikeResponse:
    return await toggle_activity_like(gateway, access_token, activity_id, type)


@activities_router.get(
    "/{activity_id}/replies",
    response_model=ActivityRepliesResponse,
)
async def replies(
    activity_id: int,
    gateway: Annotated[AnilistGateway, Depends(get_anilist_gateway)],
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
) -> ActivityRepliesResponse:
    return await get_activity_replies(gateway, access_token, activity_id)


@activities_router.post("/{activity_id}/replies", response_model=ActivityReplyResponse)
async def reply(
    activity_id: int,
    body: CreateActivityReplyRequest,
    gateway: Annotated[AnilistGateway, Depends(get_anilist_gateway)],
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
) -> ActivityReplyResponse:
    return await post_reply(gateway, access_token, activity_id, body.text)
