import json
from pathlib import Path

import httpx
import pytest
import respx

from app.core.crypto import encrypt_token
from app.core.security import create_app_jwt
from app.modules.anilist.client import ANILIST_GRAPHQL_URL
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
def anilist_activities_payload():
    return json.loads(Path("tests/fixtures/anilist_activities.json").read_text())


@respx.mock
def test_should_get_user_activities(client, auth_headers, anilist_activities_payload):
    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(200, json=anilist_activities_payload)
    )

    response = client.get(
        "anilist/user/activities",
        params={"page": 1, "per_page": 10},
        headers=auth_headers["headers"],
    )

    data = response.json()

    assert response.status_code == 200
    assert data["Page"]["pageInfo"]["currentPage"] == 1
    assert len(data["Page"]["activities"]) == 3
