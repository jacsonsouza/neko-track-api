import httpx
import pytest
import respx

from app.core.crypto import encrypt_token
from app.core.security import create_app_jwt
from app.modules.auth.anilist_client import ANILIST_GRAPHQL_URL
from tests.factories.anilist_token_factory import AnilistTokenFactory
from tests.factories.user_factory import UserFactory


@pytest.fixture
def auth_headers():
    access_token = "anilist_token"
    encrypted_token = encrypt_token(access_token)

    anilist_token = AnilistTokenFactory.create(
        user__name="Jacson",
        user__anilist_id=123,
        access_token_encrypted=encrypted_token,
    )

    app_jwt = create_app_jwt(
        user_id=anilist_token.user.id,
        anilist_id=anilist_token.user.anilist_id,
    )

    return {
        "access_token": access_token,
        "jwt": app_jwt,
        "user": anilist_token.user,
        "headers": {"Authorization": f"Bearer {app_jwt}"},
    }


@pytest.fixture
def anilist_profile_payload():
    return {
        "data": {
            "Viewer": {
                "id": 123,
                "name": "Jacson",
                "about": "",
                "bannerImage": "anilist.co/x.img",
                "avatar": {
                    "large": "anilist.co/large.img",
                    "medium": "anilist.co/medium.img",
                },
                "statistics": {
                    "anime": {
                        "count": 10,
                        "meanScore": 8.0,
                        "episodesWatched": 240,
                        "standardDeviation": 8.0,
                    }
                },
            }
        }
    }


@respx.mock
def test_should_get_user_profile_infos(client, auth_headers, anilist_profile_payload):
    def _assert_and_reply(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("Authorization") == (
            f"Bearer {auth_headers['access_token']}"
        )

        return httpx.Response(200, json=anilist_profile_payload)

    route = respx.post(ANILIST_GRAPHQL_URL).mock(side_effect=_assert_and_reply)

    response = client.get("/anilist/profile", headers=auth_headers["headers"])
    data = response.json()
    user = auth_headers["user"]

    assert response.status_code == 200
    assert data["id"] == user.anilist_id
    assert data["name"] == user.name
    assert data["avatar"]["large"] == "anilist.co/large.img"
    assert data["statistics"]["anime"]["count"] == 10


@respx.mock
def test_should_not_allow_access_without_a_valid_jwt(client):
    response = client.get(
        "/anilist/profile", headers={"Authorization": f"Bearer invalid_jwt"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@respx.mock
def test_should_not_allow_access_without_authorization_header(client):
    response = client.get("/anilist/profile")

    assert response.status_code == 401


@respx.mock
def test_should_return_error_when_user_has_no_anilist_token(client):
    user = UserFactory.create()

    jwt = create_app_jwt(user.id, user.anilist_id)

    response = client.get(
        "/anilist/profile", headers={"Authorization": f"Bearer {jwt}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Anilist token not found for user"


@respx.mock
def test_should_fail_when_anilist_payload_is_invalid(client, auth_headers):
    invalid_payload = {"data": {"Viewer": None}}

    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(200, json=invalid_payload)
    )

    response = client.get("/anilist/profile", headers=auth_headers["headers"])

    assert response.status_code == 502
    assert response.json()["detail"] == "Invalid AniList response"
