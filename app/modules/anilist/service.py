import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_token
from app.modules.anilist.client import AnilistClient
from app.modules.anilist.queries.activities import DELETE_REPLY, POST_REPLY, REPLIES
from app.modules.auth.token_repo import get_by_user_id


async def viewer(db: Session, *, user_id: int) -> dict:
    row = get_by_user_id(db, user_id)
    if not row:
        raise HTTPException(404, "Anilist token not found")

    access_token = decrypt_token(row.access_token_encrypted)

    async with httpx.AsyncClient(timeout=15) as http:
        client = AnilistClient(http)
        return await client.viewer(access_token)


async def get_activity_replies(
    http: httpx.AsyncClient, access_token: str, activity_id: int
):
    client = AnilistClient(http)

    return await client.graphql(
        access_token=access_token,
        query=REPLIES,
        variables={"activityId": activity_id},
    )


async def post_reply(
    http: httpx.AsyncClient, access_token: str, activity_id: int, text: str
):
    client = AnilistClient(http)

    return await client.graphql(
        access_token=access_token,
        query=POST_REPLY,
        variables={"activityId": activity_id, "text": text},
    )


async def remove_reply(http: httpx.AsyncClient, access_token: str, reply_id: int):
    client = AnilistClient(http)

    return await client.graphql(
        access_token=access_token, query=DELETE_REPLY, variables={"id": reply_id}
    )
