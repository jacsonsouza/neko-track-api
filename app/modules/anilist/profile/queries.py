VIEWER_PROFILE = """
query ViewerProfile {
    Viewer {
        id
        name
        about
        avatar {
            large
            medium
        }
        bannerImage
        statistics {
            anime {
                count
                meanScore
                episodesWatched
                standardDeviation
            }
        }
    }
}
"""
