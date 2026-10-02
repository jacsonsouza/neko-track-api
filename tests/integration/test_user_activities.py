import json
from pathlib import Path

import pytest

from app.core.crypto import encrypt_token
from app.core.security import create_app_jwt
from tests.factories.anilist_token_factory import AnilistTokenFactory


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
def anilist_activities_data():
    payload = json.loads(Path("tests/fixtures/anilist_activities.json").read_text())
    return payload["data"]


def test_should_get_user_activities(
    client, auth_headers, anilist_activities_data, anilist_gateway
):
    anilist_gateway.data = anilist_activities_data

    response = client.get(
        "api/v1/me/activities",
        params={"page": 1, "per_page": 10},
        headers=auth_headers["headers"],
    )

    data = response.json()

    assert response.status_code == 200
    assert data["Page"]["pageInfo"]["currentPage"] == 1
    assert len(data["Page"]["activities"]) == 3

    call = anilist_gateway.last_call
    assert call.access_token == auth_headers["access_token"]
    assert call.variables == {"userId": 123, "page": 1, "perPage": 10}
