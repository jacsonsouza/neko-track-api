def test_viewer_requires_auth(client):
    r = client.get("/api/v1/me/viewer")
    assert r.status_code == 401


def test_viewer_returns_data_using_saved_token(client, anilist_gateway):
    r1 = client.get("/auth/anilist/start", follow_redirects=False)
    state = r1.headers["location"].split("state=")[1]

    r2 = client.get(
        f"/auth/anilist/callback?code=abc&state={state}", follow_redirects=False
    )

    token = r2.headers["location"].split("token=")[1]

    r3 = client.get("/api/v1/me/viewer", headers={"Authorization": f"Bearer {token}"})

    assert r3.status_code == 200

    data = r3.json()

    assert data["id"] == 99
    assert data["name"] == "Jacson"

    # The stored AniList token (not the app JWT) is what reaches the gateway.
    viewer_calls = [call for call in anilist_gateway.calls if call.method == "viewer"]
    assert viewer_calls[-1].access_token == anilist_gateway.access_token
