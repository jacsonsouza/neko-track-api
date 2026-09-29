from enum import Enum


class MediaListStatus(str, Enum):
    """AniList ``MediaListStatus`` — status of an entry in the user's list."""

    CURRENT = "CURRENT"
    PLANNING = "PLANNING"
    COMPLETED = "COMPLETED"
    DROPPED = "DROPPED"
    PAUSED = "PAUSED"
    REPEATING = "REPEATING"


class LikeableType(str, Enum):
    """AniList ``LikeableType`` — target accepted by the ToggleLike mutation."""

    THREAD = "THREAD"
    THREAD_COMMENT = "THREAD_COMMENT"
    ACTIVITY = "ACTIVITY"
    ACTIVITY_REPLY = "ACTIVITY_REPLY"
