from typing import Optional

from pydantic import BaseModel, Field


class CoverImage(BaseModel):
    extra_large: Optional[str] = Field(None, alias="extraLarge")
    large: Optional[str] = Field(None, alias="large")
    medium: Optional[str] = Field(None, alias="medium")
    color: Optional[str] = None
