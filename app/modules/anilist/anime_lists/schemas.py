from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.anilist.anime_details.dto.anime_progress_dto import FuzzyDateDTO
from app.modules.anilist.enums import AnimeListStatus


class UpdateAnimeListEntryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    status: AnimeListStatus | None = None
    score: float | None = Field(default=None, ge=0, le=100)
    progress: int | None = Field(default=None, ge=0)
    started_at: date | None = Field(default=None, alias="startedAt")
    completed_at: date | None = Field(default=None, alias="completedAt")

    def to_anilist_variables(self) -> dict[str, Any]:
        variables = self.model_dump(by_alias=True, exclude_unset=True)

        if "status" in variables:
            variables["status"] = variables["status"].value

        if "startedAt" in variables:
            variables["startedAt"] = FuzzyDateDTO.from_date(variables["startedAt"])

        if "completedAt" in variables:
            variables["completedAt"] = FuzzyDateDTO.from_date(variables["completedAt"])

        return variables


class AnimeListEntryResponse(BaseModel):
    id: int
    media_id: int = Field(alias="mediaId")
    status: AnimeListStatus
    score: float | None
    progress: int
