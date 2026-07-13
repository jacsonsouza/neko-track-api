from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class FuzzyDateDTO(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None

    @classmethod
    def from_date(cls, dt: Optional[date]) -> Optional[dict]:
        if not dt:
            return None
        return {"year": dt.year, "month": dt.month, "day": dt.day}


class AnimeProgressDTO(BaseModel):
    media_id: int = Field(..., alias="mediaId")
    status: Optional[str] = None
    score_raw: Optional[int] = Field(None, alias="scoreRaw")
    progress: Optional[int] = None
    started_at: Optional[date] = Field(None, alias="startedAt")
    completed_at: Optional[date] = Field(None, alias="completedAt")
