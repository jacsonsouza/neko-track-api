from app.modules.anilist.gateway import AnilistGateway
from app.modules.anilist.replies.queries import DELETE_REPLY, POST_REPLY, REPLIES
from app.modules.anilist.replies.schemas import (
    ActivityReplyResponse,
    ActivityRepliesResponse,
    DeleteReplyResponse,
)


async def get_activity_replies(
    gateway: AnilistGateway, access_token: str, activity_id: int
) -> ActivityRepliesResponse:
    data = await gateway.graphql(
        access_token=access_token,
        query=REPLIES,
        variables={"activityId": activity_id},
    )

    return ActivityRepliesResponse.from_graphql(data)


async def post_reply(
    gateway: AnilistGateway, access_token: str, activity_id: int, text: str
) -> ActivityReplyResponse:
    data = await gateway.graphql(
        access_token=access_token,
        query=POST_REPLY,
        variables={"activityId": activity_id, "text": text},
    )

    return ActivityReplyResponse.from_graphql(data, key="SaveActivityReply")


async def remove_reply(
    gateway: AnilistGateway, access_token: str, reply_id: int
) -> DeleteReplyResponse:
    data = await gateway.graphql(
        access_token=access_token, query=DELETE_REPLY, variables={"id": reply_id}
    )

    return DeleteReplyResponse.from_graphql(data)
