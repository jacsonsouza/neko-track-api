import httpx
import pytest
import respx

from app.modules.auth.anilist_client import ANILIST_GRAPHQL_URL, ANILIST_OAUTH_TOKEN_URL


@respx.mock
@pytest.mark.asyncio
async def test_should_get_user_profile_infos(client):
    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "Viewer": {
                        "id": 1,
                        "name": "Jacson",
                        "about": "",
                        "bannerImage": "anilist.co/x.img",
                        "avatar": {
                            "large": "anilist.co/x.img",
                            "medium": "anilist.co/x.img",
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
            },
        )
    )

    response = client.get("/anilist/profile", follow_redirects=False)

    data = response.json()

    print(f"data: {data}")

    assert data["data"]["Viewer"]["id"] == 1
