from typing import Annotated

import httpx
from fastapi import APIRouter, Depends

from app.modules.anilist.activities.schemas import ToggleLikeResponse
from app.modules.anilist.activities.service import toggle_activity_like
from app.modules.anilist.enums import LikeableType
from app.modules.anilist.replies.schemas import DeleteReplyResponse
from app.modules.anilist.replies.service import remove_reply
from app.modules.auth.dependencies import get_current_anilist_access_token

router = APIRouter(prefix="/api/v1/replies", tags=["replies", "activities"])


@router.delete("/{reply_id}", response_model=DeleteReplyResponse)
async def delete_reply(
    reply_id: int,
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
) -> DeleteReplyResponse:
    async with httpx.AsyncClient(timeout=15) as http:
        return await remove_reply(http, access_token, reply_id)


@router.post(
    "/{reply_id}/toggle-like",
    response_model=ToggleLikeResponse,
)
async def toggle_reply_like(
    reply_id: int,
    type: LikeableType,
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
) -> ToggleLikeResponse:
    async with httpx.AsyncClient(timeout=15) as http:
        return await toggle_activity_like(http, access_token, reply_id, type)
