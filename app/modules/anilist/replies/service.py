import httpx

from app.modules.anilist.client import AnilistClient
from app.modules.anilist.replies.queries import DELETE_REPLY, POST_REPLY, REPLIES
from app.modules.anilist.replies.schemas import (
    ActivityReplyResponse,
    ActivityRepliesResponse,
    DeleteReplyResponse,
)


async def get_activity_replies(
    http: httpx.AsyncClient, access_token: str, activity_id: int
) -> ActivityRepliesResponse:
    client = AnilistClient(http)

    payload = await client.graphql(
        access_token=access_token,
        query=REPLIES,
        variables={"activityId": activity_id},
    )

    return ActivityRepliesResponse.from_graphql(payload)


async def post_reply(
    http: httpx.AsyncClient, access_token: str, activity_id: int, text: str
) -> ActivityReplyResponse:
    client = AnilistClient(http)

    payload = await client.graphql(
        access_token=access_token,
        query=POST_REPLY,
        variables={"activityId": activity_id, "text": text},
    )

    return ActivityReplyResponse.from_graphql(payload, key="SaveActivityReply")


async def remove_reply(
    http: httpx.AsyncClient, access_token: str, reply_id: int
) -> DeleteReplyResponse:
    client = AnilistClient(http)

    payload = await client.graphql(
        access_token=access_token, query=DELETE_REPLY, variables={"id": reply_id}
    )

    return DeleteReplyResponse.from_graphql(payload)
