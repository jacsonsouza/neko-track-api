from typing import List, Optional

from pydantic import BaseModel, Field

from app.modules.anilist.models.cover_image_model import CoverImage
from app.modules.anilist.models.page_info_model import PageInfo
from app.modules.anilist.models.title_model import Title


class NextAiringEpisode(BaseModel):
    id: int
    airing_at: int = Field(..., alias="airingAt")
    time_until_airing: int = Field(..., alias="timeUntilAiring")
    episode: int


class Media(BaseModel):
    id: int
    mean_score: Optional[int] = Field(None, alias="meanScore")
    episodes: Optional[int] = None
    title: Title
    cover_image: CoverImage = Field(..., alias="coverImage")
    next_airing_episode: Optional[NextAiringEpisode] = Field(
        None, alias="nextAiringEpisode"
    )


class MediaEntry(BaseModel):
    status: str
    progress: int
    media: Media

    @property
    def is_behind_airing(self) -> bool:
        if not self.media.next_airing_episode:
            return False

        latest_released = self.media.next_airing_episode.episode - 1
        return self.progress < latest_released

    @property
    def is_finished_but_watching(self) -> bool:
        if self.media.episodes is None:
            return False
        return (
            self.progress < self.media.episodes and not self.media.next_airing_episode
        )

    @property
    def should_include(self) -> bool:
        return self.is_behind_airing or self.is_finished_but_watching


class AniListResponse(BaseModel):
    page_info: PageInfo = Field(..., alias="pageInfo")
    media_list: List[MediaEntry] = Field(..., alias="mediaList")

    @classmethod
    def from_json(cls, raw_data: dict) -> "AniListResponse":
        page_data = raw_data.get("data", {}).get("Page", {})
        return cls(**page_data)

    def get_filtered_entries(self) -> List[MediaEntry]:
        return [entry for entry in self.media_list if entry.should_include]
