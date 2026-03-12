ANIME_SEARCH = """
query ($search: String, $page: Int, $perPage: Int) {
    Page(page: $page, perPage: $perPage) {
        pageInfo {
            perPage
            currentPage
            hasNextPage
        }
        media(search: $search, type: ANIME, sort: POPULARITY_DESC) {
            id
            title {
                romaji
                english
                userPreferred
            }
            description
            coverImage {
                large
            }
            genres
            episodes
            status
            averageScore
        }
    }
}
"""
