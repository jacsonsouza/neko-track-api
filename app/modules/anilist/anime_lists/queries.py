USER_ANIME_LISTS = """
    query ($userId: Int!, $status: MediaListStatus!, $page: Int) {
        Page(page: $page, perPage: 20) {
            pageInfo {
                perPage
                currentPage
                hasNextPage
            }
            mediaList(
                userId: $userId
                type: ANIME
                status: $status
                sort: [MEDIA_TITLE_ENGLISH, MEDIA_ID]
            ) {
                status
                progress
                media {
                    id
                    meanScore
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

USER_WATCHING_ANIME_LISTS = """
query ($userId: Int!) {
  Page(perPage: 50) {
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
