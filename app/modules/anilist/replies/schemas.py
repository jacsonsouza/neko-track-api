"""Public response and request schemas for the activity replies feature."""

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import AvatarResponse


class ActivityReplyUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    avatar: AvatarResponse | None = None


class ActivityReplyResponse(BaseModel):
    """A single reply, shared by the list, create and delete endpoints."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    user_id: int | None = Field(default=None, alias="userId")
    activity_id: int | None = Field(default=None, alias="activityId")
    text: str | None = None
    created_at: int | None = Field(default=None, alias="createdAt")
    like_count: int = Field(default=0, alias="likeCount")
    is_liked: bool = Field(default=False, alias="isLiked")
    user: ActivityReplyUser | None = None

    @classmethod
    def from_graphql(cls, payload: dict, *, key: str) -> "ActivityReplyResponse":
        node = (payload.get("data") or {}).get(key) or {}
        return cls.model_validate(node)


class ActivityRepliesResponse(BaseModel):
    replies: list[ActivityReplyResponse]

    @classmethod
    def from_graphql(cls, payload: dict) -> "ActivityRepliesResponse":
        page = (payload.get("data") or {}).get("Page") or {}
        return cls(replies=page.get("activityReplies") or [])


class DeleteReplyResponse(BaseModel):
    deleted: bool

    @classmethod
    def from_graphql(cls, payload: dict) -> "DeleteReplyResponse":
        node = (payload.get("data") or {}).get("DeleteActivityReply") or {}
        return cls.model_validate(node)


class CreateActivityReplyRequest(BaseModel):
    """Body of ``POST /api/v1/activities/{activity_id}/replies``."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=2000)
