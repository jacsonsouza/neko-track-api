"""Contract-level assertions: error body, enums and response envelopes."""

from app.core.security import create_app_jwt
from app.modules.anilist.errors import (
    AnilistHttpError,
    AnilistRateLimitError,
    AnilistResponseError,
    AnilistTimeoutError,
)
from tests.conftest import AuthenticatedAniListUser


def test_unauthorized_response_carries_detail_and_code(client):
    response = client.get("/api/v1/me/profile")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Missing or malformed authorization header.",
        "code": "UNAUTHORIZED",
        "errors": [],
    }


def test_unknown_media_list_status_is_rejected_as_an_enumeration(
    client, make_authenticated_anilist_user
):
    authenticated_user: AuthenticatedAniListUser = make_authenticated_anilist_user(
        anilist_id=11, access_token="token"
    )

    response = client.get(
        "/api/v1/me/anime-list",
        params={"status": "NOT_A_STATUS"},
        headers=authenticated_user.headers,
    )

    assert response.status_code == 422

    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["errors"][0]["loc"] == "query.status"
    assert body["errors"][0]["type"] == "enum"


def test_unknown_likeable_type_is_rejected_as_an_enumeration(
    client, make_authenticated_anilist_user
):
    authenticated_user: AuthenticatedAniListUser = make_authenticated_anilist_user(
        anilist_id=12, access_token="token"
    )

    response = client.post(
        "/api/v1/activities/7/like",
        params={"type": "EVERYTHING"},
        headers=authenticated_user.headers,
    )

    assert response.status_code == 422
    assert response.json()["errors"][0]["loc"] == "query.type"


def test_me_answers_a_single_shape_when_the_user_row_is_missing(client):
    app_jwt = create_app_jwt(user_id=999_999, anilist_id=7)

    response = client.get(
        "/auth/anilist/me", headers={"Authorization": f"Bearer {app_jwt}"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 999999,
        "anilist_id": 7,
        "name": None,
        "exists": False,
    }


def test_toggle_like_unwraps_the_anilist_envelope(
    client, make_authenticated_anilist_user, anilist_gateway
):
    authenticated_user: AuthenticatedAniListUser = make_authenticated_anilist_user(
        anilist_id=13, access_token="token"
    )
    anilist_gateway.data = {"ToggleLikeV2": {"id": 7, "likeCount": 3, "isLiked": True}}

    response = client.post(
        "/api/v1/activities/7/like",
        params={"type": "ACTIVITY"},
        headers=authenticated_user.headers,
    )

    assert response.status_code == 200
    assert response.json() == {"id": 7, "likeCount": 3, "isLiked": True}

    call = anilist_gateway.last_call
    assert call.access_token == authenticated_user.access_token
    assert call.variables == {"id": 7, "type": "ACTIVITY"}


def test_create_reply_requires_a_json_body(
    client, make_authenticated_anilist_user
):
    authenticated_user: AuthenticatedAniListUser = make_authenticated_anilist_user(
        anilist_id=14, access_token="token"
    )

    response = client.post(
        "/api/v1/activities/7/replies",
        json={},
        headers=authenticated_user.headers,
    )

    assert response.status_code == 422
    assert response.json()["errors"][0]["loc"] == "body.text"


# --------------------------------------------------------------------------- #
# Provider failures raised by the gateway → the public error contract
# --------------------------------------------------------------------------- #


def _profile_headers(make_authenticated_anilist_user) -> dict[str, str]:
    authenticated_user: AuthenticatedAniListUser = make_authenticated_anilist_user(
        anilist_id=15, access_token="token"
    )
    return authenticated_user.headers


def test_rate_limit_answers_429_with_retry_after(
    client, make_authenticated_anilist_user, anilist_gateway
):
    anilist_gateway.graphql_error = AnilistRateLimitError(retry_after=30)

    response = client.get(
        "/api/v1/me/profile", headers=_profile_headers(make_authenticated_anilist_user)
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "30"
    assert response.json() == {
        "detail": "AniList rate limit exceeded",
        "code": "RATE_LIMITED",
        "errors": [],
    }


def test_timeout_answers_504(
    client, make_authenticated_anilist_user, anilist_gateway
):
    anilist_gateway.graphql_error = AnilistTimeoutError("AniList timed out")

    response = client.get(
        "/api/v1/me/profile", headers=_profile_headers(make_authenticated_anilist_user)
    )

    assert response.status_code == 504
    assert response.json()["detail"] == "AniList request timed out"
    assert response.json()["code"] == "UPSTREAM_ERROR"


def test_transport_failure_answers_502(
    client, make_authenticated_anilist_user, anilist_gateway
):
    anilist_gateway.graphql_error = AnilistHttpError("AniList answered 500")

    response = client.get(
        "/api/v1/me/profile", headers=_profile_headers(make_authenticated_anilist_user)
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "AniList request failed"


def test_unusable_payload_answers_502(
    client, make_authenticated_anilist_user, anilist_gateway
):
    anilist_gateway.graphql_error = AnilistResponseError("AniList GraphQL errors")

    response = client.get(
        "/api/v1/me/profile", headers=_profile_headers(make_authenticated_anilist_user)
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Invalid AniList response"
