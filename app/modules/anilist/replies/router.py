from typing import Annotated

import httpx
from fastapi import APIRouter, Depends

from app.modules.anilist.activities.service import toggle_activity_like
from app.modules.anilist.replies.service import remove_reply
from app.modules.auth.dependencies import get_current_anilist_access_token

router = APIRouter(prefix="/api/v1/replies", tags=["replies", "activities"])


@router.delete("/{reply_id}")
async def delete_reply(
    reply_id: int,
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
):
    async with httpx.AsyncClient(timeout=15) as http:
        return await remove_reply(http, access_token, reply_id)


@router.post("/{reply_id}/toggle-like")
async def toggle_reply_like(
    reply_id: int,
    type: str,
    access_token: Annotated[str, Depends(get_current_anilist_access_token)] = None,
):
    async with httpx.AsyncClient(timeout=15) as http:
        return await toggle_activity_like(http, access_token, reply_id, type)
