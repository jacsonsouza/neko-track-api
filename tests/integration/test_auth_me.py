def test_me_requires_auth(client):
    r = client.get("/auth/anilist/me")
    assert r.status_code == 401


def test_me_returns_user_after_login(client, anilist_gateway):
    r1 = client.get("/auth/anilist/start", follow_redirects=False)
    state = r1.headers["location"].split("state=")[1]

    r2 = client.get(
        f"/auth/anilist/callback?code=abc&state={state}", follow_redirects=False
    )

    token = r2.headers["location"].split("token=")[1]

    r3 = client.get("/auth/anilist/me", headers={"Authorization": f"Bearer {token}"})

    assert r3.status_code == 200

    data = r3.json()

    assert data["anilist_id"] == 99
    assert data["name"] == "Jacson"

    assert [call.method for call in anilist_gateway.calls] == [
        "exchange_code_for_token",
        "viewer",
    ]
    assert anilist_gateway.calls[0].code == "abc"
