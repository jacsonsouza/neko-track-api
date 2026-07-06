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
  }
}
"""
