import httpx

from app.modules.anilist.client import AnilistClient
from app.modules.anilist.replies.queries import DELETE_REPLY, POST_REPLY, REPLIES


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
