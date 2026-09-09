import httpx
import respx
from fastapi.testclient import TestClient

from app.core.oauth_state import create_state
from app.main import app
from app.modules.anilist.client import ANILIST_GRAPHQL_URL, ANILIST_OAUTH_TOKEN_URL


def test_start_redirects_to_anilist(client):
    r = client.get("/auth/anilist/start", follow_redirects=False)
    assert r.status_code == 302
    assert "anilist.co/api/v2/oauth/authorize" in r.headers["location"]


def test_start_includes_state_in_redirect_url(client):
    r = client.get("/auth/anilist/start", follow_redirects=False)
    loc = r.headers["location"]
    assert "state=" in loc
    state = loc.split("state=")[1]
    assert "." in state


def test_callback_rejects_invalid_state(client):
    r = client.get(
        "/auth/anilist/callback?code=abc&state=invalid", follow_redirects=False
    )
    assert r.status_code == 400


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


@respx.mock
def test_callback_returns_500_when_anilist_token_endpoint_fails(db_session):
    from app.db.session import get_db

    respx.post(ANILIST_OAUTH_TOKEN_URL).mock(
        return_value=httpx.Response(401, json={"error": "invalid_grant"})
    )

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(app, raise_server_exceptions=False)

    state = create_state()
    r = client.get(
        f"/auth/anilist/callback?code=bad&state={state}", follow_redirects=False
    )
    assert r.status_code == 500
    app.dependency_overrides.clear()


@respx.mock
def test_callback_returns_500_when_anilist_graphql_errors(db_session):
    from app.db.session import get_db

    respx.post(ANILIST_OAUTH_TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "tok"})
    )
    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(
            200, json={"errors": [{"message": "Not found"}]}
        )
    )

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(app, raise_server_exceptions=False)

    state = create_state()
    r = client.get(
        f"/auth/anilist/callback?code=abc&state={state}", follow_redirects=False
    )
    assert r.status_code == 500
    app.dependency_overrides.clear()


@respx.mock
def test_callback_rejects_replayed_state(client):
    respx.post(ANILIST_OAUTH_TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "token123"})
    )
    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(
            200, json={"data": {"Viewer": {"id": 99, "name": "Jacson"}}}
        )
    )

    state = create_state()

    r1 = client.get(
        f"/auth/anilist/callback?code=abc&state={state}", follow_redirects=False
    )
    assert r1.status_code == 302

    r2 = client.get(
        f"/auth/anilist/callback?code=abc&state={state}", follow_redirects=False
    )
    assert r2.status_code == 400
