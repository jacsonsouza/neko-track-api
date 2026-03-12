ANIME_SEARCH = """
query ($search: String, $page: Int, $perPage: Int) {
    Page(page: $page, perPage: $perPage) {
        media(search: $search, type: ANIME, sort: POPULARITY_DESC) {
            id
            title {
                romaji
                english
                userPreferred
            }
            genres
            description
            coverImage {
                large
            }
            episodes
            status
            averageScore
        }
    }
}
"""
