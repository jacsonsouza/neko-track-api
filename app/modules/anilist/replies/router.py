from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.anilist.activities.schemas import ToggleLikeResponse
from app.modules.anilist.activities.service import toggle_activity_like
from app.modules.anilist.enums import LikeableType
from app.modules.anilist.gateway import AnilistGateway, get_anilist_gateway
from app.modules.anilist.replies.schemas import DeleteReplyResponse
from app.modules.anilist.replies.service import remove_reply
from app.modules.auth.dependencies import get_current_anilist_access_token

router = APIRouter(prefix="/api/v1/replies", tags=["replies", "activities"])


@router.delete("/{reply_id}", response_model=DeleteReplyResponse)
async def delete_reply(
    reply_id: int,
    gateway: Annotated[AnilistGateway, Depends(get_anilist_gateway)],
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
) -> DeleteReplyResponse:
    return await remove_reply(gateway, access_token, reply_id)


@router.post(
    "/{reply_id}/toggle-like",
    response_model=ToggleLikeResponse,
)
async def toggle_reply_like(
    reply_id: int,
    type: LikeableType,
    gateway: Annotated[AnilistGateway, Depends(get_anilist_gateway)],
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
) -> ToggleLikeResponse:
    return await toggle_activity_like(gateway, access_token, reply_id, type)
