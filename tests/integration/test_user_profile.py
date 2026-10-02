import pytest

from app.core.crypto import encrypt_token
from app.core.security import create_app_jwt
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
def anilist_profile_data():
    return {
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


def test_should_get_user_profile_infos(
    client, auth_headers, anilist_profile_data, anilist_gateway
):
    anilist_gateway.data = anilist_profile_data

    response = client.get("/api/v1/me/profile", headers=auth_headers["headers"])

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == auth_headers["user"].anilist_id
    assert data["name"] == "Jacson"
    assert data["avatar"]["large"] == "anilist.co/large.img"
    assert data["statistics"]["anime"]["count"] == 10

    call = anilist_gateway.last_call
    assert call.access_token == auth_headers["access_token"]
    assert "ViewerProfile" in call.query


def test_should_not_allow_access_without_a_valid_jwt(client):
    response = client.get(
        "/api/v1/me/profile", headers={"Authorization": f"Bearer invalid_jwt"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token."


def test_should_not_allow_access_without_authorization_header(client):
    response = client.get("/api/v1/me/profile")

    assert response.status_code == 401


def test_should_return_error_when_user_has_no_anilist_token(client):
    user = UserFactory.create()

    jwt = create_app_jwt(user.id, user.anilist_id)

    response = client.get(
        "/api/v1/me/profile", headers={"Authorization": f"Bearer {jwt}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "AniList account is not connected"


def test_should_fail_when_anilist_payload_is_invalid(
    client, auth_headers, anilist_gateway
):
    anilist_gateway.data = {"Viewer": None}

    response = client.get("/api/v1/me/profile", headers=auth_headers["headers"])

    assert response.status_code == 502
    assert response.json()["detail"] == "Invalid AniList response"
