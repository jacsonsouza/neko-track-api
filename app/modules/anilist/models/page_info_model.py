from pydantic import BaseModel, Field


class PageInfo(BaseModel):
    per_page: int = Field(..., alias="perPage")
    current_page: int = Field(..., alias="currentPage")
    has_next_page: bool = Field(..., alias="hasNextPage")
