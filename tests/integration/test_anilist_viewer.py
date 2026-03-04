import httpx
import respx

from app.modules.auth.anilist_client import ANILIST_GRAPHQL_URL, ANILIST_OAUTH_TOKEN_URL


@respx.mock
def test_viewer_requires_auth(client):
    r = client.get("/anilist/viewer")
    assert r.status_code == 401


@respx.mock
def test_viewer_returns_data_using_saved_token(client):
    respx.post(ANILIST_OAUTH_TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "token123"})
    )

    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(
            200, json={"data": {"Viewer": {"id": 99, "name": "Jacson"}}}
        )
    )

    r1 = client.get("/auth/anilist/start", follow_redirects=False)
    state = r1.headers["location"].split("state=")[1]

    r2 = client.get(
        f"/auth/anilist/callback?code=abc&state={state}", follow_redirects=False
    )

    token = r2.headers["location"].split("token=")[1]

    r3 = client.get("/anilist/viewer", headers={"Authorization": f"Bearer {token}"})

    assert r3.status_code == 200

    data = r3.json()

    assert data["id"] == 99
    assert data["name"] == "Jacson"
