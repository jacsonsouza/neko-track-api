"""Schemas of the ``anime-list`` feature, split into requests and responses.

The AniList payload models used to filter entries live in
``models/anilist_media_list_response.py`` and are never exposed directly —
routers always answer with the response schemas below.
"""

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.schemas import PageInfoResponse
from app.modules.anilist.enums import MediaListStatus


# --------------------------------------------------------------------------
# Requests
# --------------------------------------------------------------------------
class FuzzyDateDTO(BaseModel):
    """AniList ``FuzzyDate`` built from the ``date`` fields of a request."""

    year: int | None = None
    month: int | None = None
    day: int | None = None

    @classmethod
    def from_date(cls, dt: date | None) -> dict | None:
        if not dt:
            return None
        return {"year": dt.year, "month": dt.month, "day": dt.day}


class UpdateAnimeListEntryRequest(BaseModel):
    """Body of ``PATCH /api/v1/me/anime-list/{anime_id}``."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    status: MediaListStatus | None = None
    score: float | None = Field(default=None, ge=0, le=100)
    progress: int | None = Field(default=None, ge=0)
    started_at: date | None = Field(default=None, alias="startedAt")
    completed_at: date | None = Field(default=None, alias="completedAt")

    @model_validator(mode="after")
    def check_at_least_one_field_set(self) -> "UpdateAnimeListEntryRequest":
        if all(
            v is None
            for v in [
                self.status,
                self.score,
                self.progress,
                self.started_at,
                self.completed_at,
            ]
        ):
            raise ValueError("At least one field must be provided")
        return self

    def to_anilist_variables(self) -> dict[str, Any]:
        variables = self.model_dump(by_alias=True, exclude_unset=True)

        if "status" in variables:
            variables["status"] = variables["status"].value

        if "startedAt" in variables:
            variables["startedAt"] = FuzzyDateDTO.from_date(variables["startedAt"])

        if "completedAt" in variables:
            variables["completedAt"] = FuzzyDateDTO.from_date(variables["completedAt"])

        return variables


# --------------------------------------------------------------------------
# Responses
# --------------------------------------------------------------------------
class MediaTitleResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    romaji: str | None = None
    english: str | None = None
    user_preferred: str | None = Field(default=None, alias="userPreferred")


class MediaCoverImageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    extra_large: str | None = Field(default=None, alias="extraLarge")
    large: str | None = None
    medium: str | None = None
    color: str | None = None


class AiringEpisodeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    airing_at: int = Field(alias="airingAt")
    time_until_airing: int = Field(alias="timeUntilAiring")
    episode: int


class AnimeListMediaResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: MediaTitleResponse
    mean_score: float | None = Field(default=None, alias="meanScore")
    episodes: int | None = None
    cover_image: MediaCoverImageResponse | None = Field(default=None, alias="coverImage")
    next_airing_episode: AiringEpisodeResponse | None = Field(
        default=None, alias="nextAiringEpisode"
    )


class AnimeListEntryItem(BaseModel):
    """One entry of a media list as returned by the list endpoints."""

    status: MediaListStatus
    progress: int
    media: AnimeListMediaResponse


class AnimeListResponse(BaseModel):
    """Paginated media list of the authenticated user."""

    model_config = ConfigDict(populate_by_name=True)

    page_info: PageInfoResponse | None = Field(default=None, alias="pageInfo")
    entries: list[AnimeListEntryItem]

    @classmethod
    def from_graphql(cls, payload: dict) -> "AnimeListResponse":
        page = (payload.get("data") or {}).get("Page") or {}
        return cls(
            page_info=page.get("pageInfo"),
            entries=page.get("mediaList") or [],
        )


class AvailableToWatchResponse(BaseModel):
    """Entries of the current list that already have an unwatched episode."""

    entries: list[AnimeListEntryItem]


class AnimeListEntryResponse(BaseModel):
    """Result of updating a media list entry (``SaveMediaListEntry``)."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    media_id: int = Field(alias="mediaId")
    status: MediaListStatus
    score: float | None
    progress: int
