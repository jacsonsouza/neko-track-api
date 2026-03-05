from pydantic import BaseModel


class AvatarDTO(BaseModel):
    large: str | None = None
    medium: str | None = None


class AnimeStatisticsDTO(BaseModel):
    count: int
    mean_score: float
    episodes_watched: int
    standard_deviation: float


class UserProfileDTO(BaseModel):
    id: int
    name: str
    about: str | None = None
    banner_image: str | None
    avatar: AvatarDTO
    anime_statistics: AnimeStatisticsDTO
