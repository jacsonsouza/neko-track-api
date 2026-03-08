USER_ACTIVITIES = """
query ($userId: Int!, $page: Int, $perPage: Int) {
    Page(page: $page, perPage: $perPage) {
        pageInfo {
            perPage
            currentPage
            hasNextPage
        }
        activities(userId: $userId, sort: ID_DESC) {
            ... on ListActivity {
                id
                __typename
                userId
                createdAt
                progress
                status
                type
                replyCount
                likeCount
                isLiked
                isPinned
                media {
                    id
                    title {
                        userPreferred
                        romaji
                    }
                    coverImage {
                        medium
                        large
                    }
                    episodes
                    chapters
                    format
                    status
                    averageScore
                }
                user {
                    id
                    name
                    avatar {
                        medium
                        large
                    }
                }
            }

            ... on TextActivity {
                id
                __typename
                userId
                createdAt
                text(asHtml: true)
                replyCount
                likeCount
                isLiked
                isSubscribed
                isLocked
                isPinned
                user {
                    id
                    name
                    avatar {
                        medium
                        large
                    }
                }
            }

            ... on MessageActivity {
                id
                __typename
                createdAt
                message
                replyCount
                likeCount
                isLiked
                isSubscribed
                isLocked
                messenger {
                    id
                    name
                    avatar {
                        medium
                        large
                    }
                }
                recipient {
                    id
                    name
                    avatar {
                        medium
                        large
                    }
                }
            }
        }
    }
}
"""

TOGGLE_LIKE = """
    mutation ($id: Int) {
        ToggleLikeV2 (id: $id, type: $type) {
            ... on ListActivity {
                id
                likeCount
                isLiked
            }
            ... on TextActivity {
                id
                likeCount
                isLiked
            }
            ... on MessageActivity {
                id
                likeCount
                isLiked
            }
        }
    }
"""
