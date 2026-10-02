from app.core.oauth_state import create_state
from app.modules.anilist.errors import AnilistHttpError, AnilistResponseError


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


def test_callback_exchange_code_and_redirects_to_deeplink(client, anilist_gateway):
    r1 = client.get("/auth/anilist/start", follow_redirects=False)
    assert r1.status_code == 302
    loc = r1.headers["location"]
    state = loc.split("state=")[1]

    r2 = client.get(
        f"/auth/anilist/callback?code=abc&state={state}", follow_redirects=False
    )

    assert r2.status_code == 302
    assert r2.headers["location"].startswith("nekotrack://auth?token=")

    assert [call.method for call in anilist_gateway.calls] == [
        "exchange_code_for_token",
        "viewer",
    ]
    assert anilist_gateway.last_call.access_token == anilist_gateway.access_token


def test_callback_returns_502_when_anilist_token_endpoint_fails(
    client, anilist_gateway
):
    # AniList rejected the code (HTTP 401 → AnilistHttpError in the gateway).
    anilist_gateway.exchange_error = AnilistHttpError(
        "AniList answered 401 calling https://anilist.co/api/v2/oauth/token"
    )

    state = create_state()
    r = client.get(
        f"/auth/anilist/callback?code=bad&state={state}", follow_redirects=False
    )

    assert r.status_code == 502
    assert r.json() == {
        "detail": "AniList request failed",
        "code": "UPSTREAM_ERROR",
        "errors": [],
    }


def test_callback_returns_502_when_anilist_viewer_is_unusable(
    client, anilist_gateway
):
    # AniList answered 200 with GraphQL errors[] (AnilistResponseError).
    anilist_gateway.viewer_error = AnilistResponseError(
        "AniList GraphQL errors: [{'message': 'Not found'}]"
    )

    state = create_state()
    r = client.get(
        f"/auth/anilist/callback?code=abc&state={state}", follow_redirects=False
    )

    assert r.status_code == 502
    assert r.json()["detail"] == "Invalid AniList response"


def test_callback_rejects_replayed_state(client, anilist_gateway):
    state = create_state()

    r1 = client.get(
        f"/auth/anilist/callback?code=abc&state={state}", follow_redirects=False
    )
    assert r1.status_code == 302

    calls_after_first_attempt = len(anilist_gateway.calls)

    r2 = client.get(
        f"/auth/anilist/callback?code=abc&state={state}", follow_redirects=False
    )
    assert r2.status_code == 400

    # The replayed attempt never reaches AniList again.
    assert len(anilist_gateway.calls) == calls_after_first_attempt
