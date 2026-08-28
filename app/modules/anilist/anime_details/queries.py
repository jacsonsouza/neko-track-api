ANIME_DETAILS = """
query ($id: Int) {
  Media (id: $id, type: ANIME) {
    id
    title {
      romaji
      english
      native
      userPreferred
    }
    coverImage {
      extraLarge
      color
    }
    mediaListEntry {
      id
      status
      score
      progress
      repeat
      private
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
