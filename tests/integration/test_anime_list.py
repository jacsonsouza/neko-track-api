import pytest

from app.core.security import create_app_jwt
from tests.conftest import AuthenticatedAniListUser
from tests.factories.user_factory import UserFactory


def _empty_anime_list_data() -> dict:
    return {
        "Page": {
            "pageInfo": {
                "currentPage": 1,
                "perPage": 10,
                "hasNextPage": False,
            },
            "mediaList": [],
        }
    }


def test_anime_list_uses_the_authenticated_users_anilist_token(
    client,
    make_authenticated_anilist_user,
    anilist_gateway,
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
    anilist_gateway.data = _empty_anime_list_data()

    response = client.get(
        "/api/v1/me/anime-list",
        params={"status": "CURRENT"},
        headers=authenticated_user.headers,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["pageInfo"] == {"perPage": 10, "currentPage": 1, "hasNextPage": False}
    assert body["entries"] == []

    # The gateway must be called with the token of the user making the request.
    call = anilist_gateway.last_call
    assert call.access_token == authenticated_user.access_token
    assert call.variables == {
        "userId": authenticated_user.user.anilist_id,
        "status": "CURRENT",
        "page": 1,
        "perPage": 10,
    }


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


def test_available_to_watch_returns_public_entries_only(
    client, make_authenticated_anilist_user, anilist_gateway
):
    authenticated_user: AuthenticatedAniListUser = make_authenticated_anilist_user(
        anilist_id=606,
        access_token="anilist-token-for-available",
    )

    anilist_gateway.data = {
        "Page": {
            "mediaList": [
                {
                    "status": "CURRENT",
                    "progress": 3,
                    "media": {
                        "id": 1,
                        "meanScore": 82,
                        "episodes": 12,
                        "nextAiringEpisode": {
                            "id": 900,
                            "airingAt": 1_700_000_000,
                            "timeUntilAiring": 100,
                            "episode": 6,
                        },
                        "title": {"romaji": "Frieren", "userPreferred": "Frieren"},
                        "coverImage": {"extraLarge": "img", "color": "#fff"},
                    },
                }
            ]
        }
    }

    response = client.get(
        "/api/v1/me/anime-list/available-to-watch",
        headers=authenticated_user.headers,
    )

    assert response.status_code == 200

    body = response.json()
    assert list(body) == ["entries"]

    entry = body["entries"][0]
    assert entry["status"] == "CURRENT"
    assert entry["progress"] == 3
    assert entry["media"]["meanScore"] == 82
    assert entry["media"]["title"]["userPreferred"] == "Frieren"
    assert entry["media"]["nextAiringEpisode"]["episode"] == 6

    call = anilist_gateway.last_call
    assert call.access_token == authenticated_user.access_token
    assert call.variables == {"userId": 606}


def test_update_anime_list_entry_sends_only_provided_fields(
    client,
    make_authenticated_anilist_user,
    anilist_gateway,
):
    authenticated_user: AuthenticatedAniListUser = make_authenticated_anilist_user(
        anilist_id=404,
        access_token="anilist-token-for-update",
    )
    anilist_gateway.data = {
        "SaveMediaListEntry": {
            "id": 1,
            "mediaId": 999,
            "status": "CURRENT",
            "score": 8.0,
            "progress": 6,
        }
    }

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

    call = anilist_gateway.last_call
    assert call.access_token == authenticated_user.access_token
    assert call.variables == {"mediaId": 999, "progress": 6}


@pytest.mark.parametrize("body", [{}, {"progress": None}])
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
