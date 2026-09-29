"""Contract-level assertions: error body, enums and response envelopes."""

import json

import httpx
import respx

from app.core.security import create_app_jwt
from app.modules.anilist.client import ANILIST_GRAPHQL_URL
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


@respx.mock
def test_toggle_like_unwraps_the_anilist_envelope(
    client, make_authenticated_anilist_user
):
    authenticated_user: AuthenticatedAniListUser = make_authenticated_anilist_user(
        anilist_id=13, access_token="token"
    )

    def assert_upstream_payload(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["variables"] == {"id": 7, "type": "ACTIVITY"}

        return httpx.Response(
            200,
            json={"data": {"ToggleLikeV2": {"id": 7, "likeCount": 3, "isLiked": True}}},
        )

    respx.post(ANILIST_GRAPHQL_URL).mock(side_effect=assert_upstream_payload)

    response = client.post(
        "/api/v1/activities/7/like",
        params={"type": "ACTIVITY"},
        headers=authenticated_user.headers,
    )

    assert response.status_code == 200
    assert response.json() == {"id": 7, "likeCount": 3, "isLiked": True}


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
