from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, model_validator


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
    score: Optional[float]
    progress: Optional[int] = None
    started_at: Optional[date] = Field(None, alias="startedAt")
    completed_at: Optional[date] = Field(None, alias="completedAt")

    @model_validator(mode="after")
    def set_dates_based_on_status(self) -> "AnimeProgressDTO":
        current_date = date.today()

        if self.status == "CURRENT" and not self.started_at:
            self.started_at = current_date

        if self.status == "COMPLETED" and not self.completed_at:
            self.completed_at = current_date

        return self
