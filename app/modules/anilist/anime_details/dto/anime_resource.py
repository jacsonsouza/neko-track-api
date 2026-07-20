from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class FuzzyDateDTO(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None


class TitleDTO(BaseModel):
    romaji: Optional[str] = None
    english: Optional[str] = None
    native: Optional[str] = None
    user_preferred: Optional[str] = Field(None, alias="userPreferred")


class CoverImageDTO(BaseModel):
    extra_large: Optional[str] = Field(None, alias="extraLarge")
    color: Optional[str] = None


class MediaListEntryDTO(BaseModel):
    id: int
    status: Optional[str] = None
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
    name: dict  # {"full": "..."}
    image: dict  # {"large": "..."}


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
    name: dict  # {"full": "..."}
    image: dict  # {"large": "..."}


class StaffEdge(BaseModel):
    role: str
    node: StaffNode


class StaffDTO(BaseModel):
    edges: List[StaffEdge] = []


class AnimeDetailsDTO(BaseModel):
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

    class ConfigDict:
        populate_by_name = True


class AnimeResource(BaseModel):
    media: AnimeDetailsDTO = Field(..., alias="Media")

    class ConfigDict:
        populate_by_name = True
