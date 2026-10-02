"""Public response and request schemas for the activities feature.

These models define what the API promises to its clients. The nested ``*DTO``
classes mirror the AniList fields we choose to expose and double as the parser
for the payload coming from the upstream query.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import PageInfoResponse
from app.modules.anilist.replies.schemas import (
    ActivityReplyResponse,
    CreateActivityReplyRequest,
)

__all__ = [
    "ActivitiesResponse",
    "CreateActivityReplyRequest",
    "ActivityReplyResponse",
    "ToggleLikeResponse",
]


class ImageDTO(BaseModel):
    large: str | None = None
    medium: str | None = None

    @classmethod
    def from_json(cls, data: dict) -> "ImageDTO":
        return cls.model_validate(data)


class UserDTO(BaseModel):
    id: int
    name: str
    avatar: ImageDTO | None = None

    @classmethod
    def from_json(cls, data: dict) -> "UserDTO":
        return cls.model_validate(data)


class TitleDTO(BaseModel):
    romaji: str | None = None
    user_preferred: str | None = Field(default=None, alias="userPreferred")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: dict) -> "TitleDTO":
        return cls.model_validate(data)


class MediaDTO(BaseModel):
    id: int
    title: TitleDTO
    episodes: int | None = None
    chapters: int | None = None
    format: str | None = None
    status: str | None = None
    average_score: int | None = Field(default=None, alias="averageScore")
    cover_image: ImageDTO | None = Field(default=None, alias="coverImage")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: dict) -> "MediaDTO":
        return cls.model_validate(data)


class BaseActivityDTO(BaseModel):
    id: int
    type_name: str = Field(alias="__typename")
    created_at: int | None = Field(default=None, alias="createdAt")
    reply_count: int | None = Field(default=None, alias="replyCount")
    like_count: int | None = Field(default=None, alias="likeCount")
    is_liked: bool | None = Field(default=None, alias="isLiked")
    is_pinned: bool | None = Field(default=None, alias="isPinned")

    model_config = ConfigDict(populate_by_name=True)


class ListActivityDTO(BaseActivityDTO):
    type_name: Literal["ListActivity"] = Field(alias="__typename")
    user_id: int | None = Field(default=None, alias="userId")
    progress: str | None = None
    status: str | None = None
    type: str | None = None
    media: MediaDTO | None = None
    user: UserDTO | None = None


class TextActivityDTO(BaseActivityDTO):
    type_name: Literal["TextActivity"] = Field(alias="__typename")
    user_id: int | None = Field(default=None, alias="userId")
    text: str | None = None
    is_subscribed: bool | None = Field(default=None, alias="isSubscribed")
    is_locked: bool | None = Field(default=None, alias="isLocked")
    user: UserDTO | None = None


class MessageActivityDTO(BaseActivityDTO):
    type_name: Literal["MessageActivity"] = Field(alias="__typename")
    message: str | None = None
    is_subscribed: bool | None = Field(default=None, alias="isSubscribed")
    is_locked: bool | None = Field(default=None, alias="isLocked")
    messenger: UserDTO | None = None
    recipient: UserDTO | None = None


ActivityDTO = Annotated[
    ListActivityDTO | TextActivityDTO | MessageActivityDTO,
    Field(discriminator="type_name"),
]


class PageDTO(BaseModel):
    page_info: PageInfoResponse = Field(alias="pageInfo")
    activities: list[ActivityDTO]

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: dict) -> "PageDTO":
        return cls.model_validate(data)


class ActivitiesResponse(BaseModel):
    """Paginated activity feed of the authenticated AniList user."""

    page: PageDTO = Field(alias="Page")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: dict) -> "ActivitiesResponse":
        return cls.model_validate(data)


class ToggleLikeResponse(BaseModel):
    """Result of liking/unliking an activity or a reply."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    like_count: int = Field(default=0, alias="likeCount")
    is_liked: bool = Field(default=False, alias="isLiked")

    @classmethod
    def from_graphql(
        cls, data: dict, *, key: str = "ToggleLikeV2"
    ) -> "ToggleLikeResponse":
        """Build from the GraphQL ``data`` object (gateway already unwrapped)."""
        node = data.get(key) or {}
        return cls.model_validate(node)
