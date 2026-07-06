from pydantic import BaseModel, ConfigDict, Field


class AvatarDTO(BaseModel):
    large: str | None = None
    medium: str | None = None

    @classmethod
    def from_json(cls, data: dict) -> "AvatarDTO":
        return cls.model_validate(data)


class AnimeStatisticsDTO(BaseModel):
    count: int | None = None
    episodes_watched: int | None = Field(default=None, alias="episodesWatched")
    mean_score: float | None = Field(default=None, alias="meanScore")
    standard_deviation: float | None = Field(default=None, alias="standardDeviation")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: dict) -> "AnimeStatisticsDTO":
        return cls.model_validate(data)


class StatisticsDTO(BaseModel):
    anime: AnimeStatisticsDTO | None = None


class UserProfileDTO(BaseModel):
    id: int
    name: str
    about: str | None = None
    banner_image: str | None = Field(default=None, alias="bannerImage")
    avatar: AvatarDTO | None = None
    statistics: StatisticsDTO | None = None

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: dict) -> "UserProfileDTO":
        return cls.model_validate(data)
