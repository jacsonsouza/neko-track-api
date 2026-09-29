"""Public response schemas of the ``animes`` feature.

The AniList payload wrapper lives in ``dto/anime_resource.py`` and maps the
upstream ``Media`` envelope onto the response schema below.
"""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import PageInfoResponse
from app.modules.anilist.enums import MediaListStatus


class TitleDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    romaji: Optional[str] = None
    english: Optional[str] = None
    native: Optional[str] = None
    user_preferred: Optional[str] = Field(None, alias="userPreferred")


class CoverImageDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    extra_large: Optional[str] = Field(None, alias="extraLarge")
    large: Optional[str] = None
    medium: Optional[str] = None
    color: Optional[str] = None


class MediaListEntryDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    status: Optional[MediaListStatus] = None
    score: Optional[float] = None
    progress: Optional[int] = None
    repeat: Optional[int] = None
    private: Optional[bool] = None
    started_at: Optional[str] = Field(None, alias="startedAt")
    completed_at: Optional[str] = Field(None, alias="completedAt")

    @field_validator("started_at", "completed_at", mode="before")
    @classmethod
    def transform_fuzzy_date(cls, value) -> Optional[str]:
        if not value or not isinstance(value, dict):
            return None

        year = value.get("year")
        month = value.get("month") or 1
        day = value.get("day") or 1

        if not year:
            return None
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            return None


class StudioNode(BaseModel):
    id: int
    name: str


class StudiosDTO(BaseModel):
    nodes: List[StudioNode] = []


class CharacterNode(BaseModel):
    id: int
    name: dict
    image: dict


class CharacterEdge(BaseModel):
    role: str
    node: CharacterNode


class CharactersDTO(BaseModel):
    edges: List[CharacterEdge] = []


class RelationNode(BaseModel):
    id: int
    title: TitleDTO
    cover_image: Optional[CoverImageDTO] = Field(None, alias="coverImage")


class RelationEdge(BaseModel):
    relation_type: str = Field(..., alias="relationType")
    node: RelationNode


class RelationsDTO(BaseModel):
    edges: List[RelationEdge] = []


class StaffNode(BaseModel):
    id: int
    name: dict
    image: dict


class StaffEdge(BaseModel):
    role: str
    node: StaffNode


class StaffDTO(BaseModel):
    edges: List[StaffEdge] = []


class AnimeDetailsResponse(BaseModel):
    """Full detail of a single anime (``GET /api/v1/animes/{anime_id}``)."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: TitleDTO
    cover_image: Optional[CoverImageDTO] = Field(None, alias="coverImage")
    media_list_entry: Optional[MediaListEntryDTO] = Field(None, alias="mediaListEntry")
    description: Optional[str] = None
    status: Optional[str] = None
    episodes: Optional[int] = None
    duration: Optional[int] = None
    season: Optional[str] = None
    season_year: Optional[int] = Field(None, alias="seasonYear")
    average_score: Optional[int] = Field(None, alias="averageScore")
    genres: List[str] = []
    is_favourite: bool = Field(False, alias="isFavourite")
    studios: Optional[StudiosDTO] = None
    characters: Optional[CharactersDTO] = None
    relations: Optional[RelationsDTO] = None
    staff: Optional[StaffDTO] = None


class AnimeSummaryResponse(BaseModel):
    """One search result of ``GET /api/v1/animes``."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: TitleDTO
    description: Optional[str] = None
    cover_image: Optional[CoverImageDTO] = Field(None, alias="coverImage")
    genres: List[str] = []
    episodes: Optional[int] = None
    status: Optional[str] = None
    average_score: Optional[int] = Field(None, alias="averageScore")


class AnimeSearchResponse(BaseModel):
    """Paginated search results."""

    model_config = ConfigDict(populate_by_name=True)

    page_info: Optional[PageInfoResponse] = Field(default=None, alias="pageInfo")
    animes: list[AnimeSummaryResponse]

    @classmethod
    def from_graphql(cls, data: dict) -> "AnimeSearchResponse":
        """Build from the GraphQL ``data`` object (gateway already unwrapped)."""
        page = data.get("Page") or {}
        return cls(page_info=page.get("pageInfo"), animes=page.get("media") or [])
