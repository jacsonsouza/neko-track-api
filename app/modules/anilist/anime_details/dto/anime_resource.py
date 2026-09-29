"""AniList payload wrapper for the anime details query.

This model only exists to parse the upstream ``{ "Media": {...} }`` envelope;
the API answers with :class:`AnimeDetailsResponse`.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.modules.anilist.anime_details.schemas import AnimeDetailsResponse


class AnimeResource(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    media: AnimeDetailsResponse = Field(..., alias="Media")
