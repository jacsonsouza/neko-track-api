ANIME_DETAILS = """
query ($id: Int) {
  Viewer {
    mediaListOptions {
      scoreFormat
    }
  }
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
