USER_WATCHING_ANIME_LISTS = """
    query ($userId: Int!, $page: Int) {
        Page(page: $page, perPage: 10) {
            pageInfo {
                perPage
                currentPage
                hasNextPage
            }
            mediaList(
                userId: $userId
                type: ANIME
                status: CURRENT
                sort: [UPDATED_TIME_DESC]
            ) {
                status
                progress
                media {
                    id
                    meanScore
                    episodes
                    nextAiringEpisode {
                        id
                        airingAt
                        timeUntilAiring
                        episode
                    }
                    title {
                        romaji
                        english
                        userPreferred
                    }
                    coverImage {
                        extraLarge
                        large
                        medium
                        color
                    }
                }
            }
        }
    }
"""

UPDATE_ANIME_PROGRESS = """
    mutation($mediaId, $progress) {
        SaveMediaListEntry(
            mediaId: $mediaId,
            progress: $progress
        ) {
            id
            mediaId
            progress
        }
    }
"""
