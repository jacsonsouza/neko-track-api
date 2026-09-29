from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import AvatarResponse


class ViewerMediaListOptions(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    score_format: str | None = Field(default=None, alias="scoreFormat")


class ViewerResponse(BaseModel):
    """The AniList account behind the current app session (``/me/viewer``)."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    media_list_options: ViewerMediaListOptions | None = Field(
        default=None, alias="mediaListOptions"
    )

    @classmethod
    def from_json(cls, data: dict) -> "ViewerResponse":
        return cls.model_validate(data)


class AnimeStatisticsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    count: int | None = None
    episodes_watched: int | None = Field(default=None, alias="episodesWatched")
    mean_score: float | None = Field(default=None, alias="meanScore")
    standard_deviation: float | None = Field(default=None, alias="standardDeviation")

    @classmethod
    def from_json(cls, data: dict) -> "AnimeStatisticsResponse":
        return cls.model_validate(data)


class StatisticsResponse(BaseModel):
    anime: AnimeStatisticsResponse | None = None


class UserProfileResponse(BaseModel):
    """Public profile of the authenticated AniList account (``/me/profile``)."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    about: str | None = None
    banner_image: str | None = Field(default=None, alias="bannerImage")
    avatar: AvatarResponse | None = None
    statistics: StatisticsResponse | None = None

    @classmethod
    def from_json(cls, data: dict) -> "UserProfileResponse":
        return cls.model_validate(data)
