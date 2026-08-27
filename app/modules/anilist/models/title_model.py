from typing import Optional

from pydantic import BaseModel, Field


class Title(BaseModel):
    romaji: Optional[str] = None
    english: Optional[str] = None
    user_preferred: Optional[str] = Field(None, alias="userPreferred")
