from typing import List, Optional

from pydantic import BaseModel, Field

from app.modules.anilist.models.cover_image_model import CoverImage
from app.modules.anilist.models.title_model import Title


class NextAiringEpisode(BaseModel):
    id: int
    airing_at: int = Field(..., alias="airingAt")
    time_until_airing: int = Field(..., alias="timeUntilAiring")
    episode: int


class AnimeListMedia(BaseModel):
    id: int
    mean_score: Optional[int] = Field(None, alias="meanScore")
    episodes: Optional[int] = None
    title: Title
    cover_image: CoverImage = Field(..., alias="coverImage")
    next_airing_episode: Optional[NextAiringEpisode] = Field(
        None, alias="nextAiringEpisode"
    )


class AnimeListEntry(BaseModel):
    status: str
    progress: int
    media: AnimeListMedia

    @property
    def is_behind_released_episodes(self) -> bool:
        if not self.media.next_airing_episode:
            return False

        latest_released = max(0, self.media.next_airing_episode.episode - 1)

        return self.progress < latest_released

    @property
    def is_finished_with_unwatched_episodes(self) -> bool:
        if self.media.episodes is None:
            return False

        has_no_more_airing = self.media.next_airing_episode is None
        return (self.progress < self.media.episodes) and has_no_more_airing

    @property
    def has_available_unwatched_episodes(self) -> bool:
        return (
            self.is_behind_released_episodes or self.is_finished_with_unwatched_episodes
        )


class AniListMediaListResponse(BaseModel):
    media_list: List[AnimeListEntry] = Field(..., alias="mediaList")

    @classmethod
    def from_json(cls, raw_data: dict) -> "AniListMediaListResponse":
        page_data = raw_data.get("data", {}).get("Page", {})
        return cls(**page_data)

    def get_available_to_watch_entries(self) -> List[AnimeListEntry]:
        return [
            entry for entry in self.media_list if entry.has_available_unwatched_episodes
        ]
