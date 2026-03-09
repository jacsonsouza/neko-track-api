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
