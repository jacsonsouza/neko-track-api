import httpx
import respx
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.anilist_client import ANILIST_GRAPHQL_URL, ANILIST_OAUTH_TOKEN_URL


def test_start_redirects_to_anilist():
    client = TestClient(app)
    r = client.get("/auth/anilist/start", follow_redirects=False)
    assert r.status_code == 302
    assert "anilist.co/api/v2/oauth/authorize" in r.headers["location"]


@respx.mock
def test_callback_exchange_code_and_redirects_to_deeplink(monkeypatch):
    respx.post(ANILIST_OAUTH_TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "token123"})
    )
    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(
            200, json={"data": {"Viewer": {"id": 99, "name": "Jacson"}}}
        )
    )

    client = TestClient(app)

    r1 = client.get("/auth/anilist/start", follow_redirects=False)
    assert r1.status_code == 302
    loc = r1.headers["location"]
    state = loc.split("state=")[1]

    r2 = client.get(
        f"/auth/anilist/callback?code=abc&state={state}", follow_redirects=False
    )

    assert r2.status_code == 302
    assert r2.headers["location"].startswith("nekotrack://auth?token=")
