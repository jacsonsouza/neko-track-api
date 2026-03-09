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
    mutation ($id: Int, $type: LikeableType) {
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

REPLIES = """
    query GetReplies($activityId: Int!) {
        Page {
            activityReplies(activityId: $activityId) {
                id
                userId
                activityId
                text(asHtml: true)
                createdAt
                likeCount
                isLiked
                user {
                    id
                    name
                    avatar {
                        large
                        medium
                    }
                }
            }
        }
    }
"""

POST_REPLY = """
    mutation PostReply($activityId: Int!, $text: String!) {
        SaveActivityReply(activityId: $activityId, text: $text) {
                id
                userId
                activityId
                text
                createdAt
                likeCount
                isLiked
                user {
                id
                name
                avatar {
                    large
                    medium
                }
            }
        }
    }
"""

DELETE_REPLY = """
    mutation DeleteActivity($id: Int!) {
        DeleteActivityReply(id: $id) {
            deleted
        }
    }
"""
