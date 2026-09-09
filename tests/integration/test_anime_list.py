import json

import httpx
import pytest
import respx

from app.core.security import create_app_jwt
from app.modules.anilist.client import ANILIST_GRAPHQL_URL
from tests.conftest import AuthenticatedAniListUser
from tests.factories.user_factory import UserFactory


def _empty_anime_list_response() -> dict:
    return {
        "data": {
            "Page": {
                "pageInfo": {
                    "currentPage": 1,
                    "perPage": 10,
                    "hasNextPage": False,
                },
                "mediaList": [],
            }
        }
    }


@respx.mock
def test_anime_list_uses_the_authenticated_users_anilist_token(
    client,
    make_authenticated_anilist_user,
):
    authenticated_user: AuthenticatedAniListUser = make_authenticated_anilist_user(
        anilist_id=101,
        access_token="anilist-token-for-user-a",
        name="User A",
    )
    make_authenticated_anilist_user(
        anilist_id=202,
        access_token="anilist-token-for-user-b",
        name="User B",
    )

    def assert_request_uses_user_as_token(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == (
            f"Bearer {authenticated_user.access_token}"
        )

        payload = json.loads(request.content)
        assert payload["variables"] == {
            "userId": authenticated_user.user.anilist_id,
            "status": "CURRENT",
            "page": 1,
            "perPage": 10,
        }

        return httpx.Response(200, json=_empty_anime_list_response())

    respx.post(ANILIST_GRAPHQL_URL).mock(side_effect=assert_request_uses_user_as_token)

    response = client.get(
        "/api/v1/me/anime-list",
        params={"status": "CURRENT"},
        headers=authenticated_user.headers,
    )

    assert response.status_code == 200


def test_anime_list_requires_a_connected_anilist_account(client):
    user = UserFactory.create(anilist_id=303)
    app_jwt = create_app_jwt(user.id, user.anilist_id)

    response = client.get(
        "/api/v1/me/anime-list",
        params={"status": "CURRENT"},
        headers={"Authorization": f"Bearer {app_jwt}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "AniList account is not connected"


@respx.mock
def test_update_anime_list_entry_sends_only_provided_fields(
    client,
    make_authenticated_anilist_user,
):
    authenticated_user: AuthenticatedAniListUser = make_authenticated_anilist_user(
        anilist_id=404,
        access_token="anilist-token-for-update",
    )

    def assert_partial_update_request(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == (
            f"Bearer {authenticated_user.access_token}"
        )

        payload = json.loads(request.content)
        assert payload["variables"] == {"mediaId": 999, "progress": 6}

        return httpx.Response(
            200,
            json={
                "data": {
                    "SaveMediaListEntry": {
                        "id": 1,
                        "mediaId": 999,
                        "status": "CURRENT",
                        "score": 8.0,
                        "progress": 6,
                    }
                }
            },
        )

    respx.post(ANILIST_GRAPHQL_URL).mock(side_effect=assert_partial_update_request)

    response = client.patch(
        "/api/v1/me/anime-list/999",
        json={"progress": 6},
        headers=authenticated_user.headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "mediaId": 999,
        "status": "CURRENT",
        "score": 8.0,
        "progress": 6,
    }


@pytest.mark.parametrize("body", [{}, {"progress": None}])
@respx.mock
def test_update_anime_list_entry_rejects_empty_or_null_fields(
    client,
    make_authenticated_anilist_user,
    body,
):
    authenticated_user: AuthenticatedAniListUser = make_authenticated_anilist_user(
        anilist_id=505,
        access_token="anilist-token-for-validation",
    )

    response = client.patch(
        "/api/v1/me/anime-list/999",
        json=body,
        headers=authenticated_user.headers,
    )

    assert response.status_code == 422
