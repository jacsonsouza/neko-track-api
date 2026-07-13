ANIME_DETAILS = """
query ($id: Int) {
  Media (id: $id, type: ANIME) {
    id
    title {
      romaji
      english
      native
    }
    bannerImage
    coverImage {
      extraLarge
      color
    }
    mediaListEntry {
      id
      status
      score (format: POINT_10)
      progress
      repeat
      private
    }
    description
    status
    episodes
    duration
    season
    seasonYear
    averageScore
    genres
    isFavourite
    studios(isMain: true) {
      nodes {
        id
        name
      }
    }
    characters(sort: [ROLE, RELEVANCE, ID], perPage: 6) {
      edges {
        role
        node {
          id
          name {
            full
          }
          image {
            large
          }
        }
      }
    }
    relations {
      edges {
        relationType
        node {
          id
          title {
            romaji
            english
            native
          }
          coverImage {
            extraLarge
          }
        }
      }
    }
    staff(sort: [RELEVANCE, ID], perPage: 6) {
      edges {
        role
        node {
          id
          name {
            full
          }
          image {
            large
          }
        }
      }
    }
  }
}
"""

SAVE_ANIME_PROGRESS = """
mutation (
  $mediaId: Int
  $status: MediaListStatus
  $scoreRaw: Int
  $progress: Int
  $startedAt: FuzzyDateInput
  $completedAt: FuzzyDateInput
) {
  SaveMediaListEntry (
    mediaId: $mediaId
    status: $status
    scoreRaw: $scoreRaw
    progress: $progress
    startedAt: $startedAt
    completedAt: $completedAt
  ) {
    id
    mediaId
    status
    scoreRaw
    progress
    startedAt {
      year
      month
      day
    }
    completedAt {
      year
      month
      day
    }
  }
}
"""
