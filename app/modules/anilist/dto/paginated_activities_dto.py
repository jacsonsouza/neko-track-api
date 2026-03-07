from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


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


class PageInfoDTO(BaseModel):
    per_page: int = Field(default=10, alias="perPage")
    current_page: int = Field(default=1, alias="currentPage")
    has_next_page: bool = Field(default=False, alias="hasNextPage")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: dict) -> "PageInfoDTO":
        return cls.model_validate(data)


class PageDTO(BaseModel):
    page_info: PageInfoDTO = Field(alias="pageInfo")
    activities: list[ActivityDTO]

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: dict) -> "PageDTO":
        return cls.model_validate(data)


class UserActivitiesDataDTO(BaseModel):
    page: PageDTO = Field(alias="Page")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: dict) -> "UserActivitiesDataDTO":
        return cls.model_validate(data)


class UserActivitiesResponseDTO(BaseModel):
    data: UserActivitiesDataDTO

    @classmethod
    def from_json(cls, data: dict) -> "UserActivitiesResponseDTO":
        return cls.model_validate(data)
