"""Schemas reused by more than one feature."""

from pydantic import BaseModel, ConfigDict, Field


class PageInfoResponse(BaseModel):
    """AniList ``PageInfo`` block, exposed as-is by every paginated endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    per_page: int = Field(default=10, alias="perPage")
    current_page: int = Field(default=1, alias="currentPage")
    has_next_page: bool = Field(default=False, alias="hasNextPage")


class AvatarResponse(BaseModel):
    """Avatar urls shared by profile, activities and replies payloads."""

    large: str | None = None
    medium: str | None = None
