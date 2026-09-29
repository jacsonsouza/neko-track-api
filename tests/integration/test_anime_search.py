import httpx
import respx

from app.modules.anilist.client import ANILIST_GRAPHQL_URL


def _search_payload() -> dict:
    return {
        "data": {
            "Page": {
                "pageInfo": {"perPage": 10, "currentPage": 1, "hasNextPage": True},
                "media": [
                    {
                        "id": 55,
                        "title": {
                            "romaji": "Cowboy Bebop",
                            "english": "Cowboy Bebop",
                            "userPreferred": "Cowboy Bebop",
                        },
                        "description": "Space bounty hunters.",
                        "coverImage": {"large": "img.jpg"},
                        "genres": ["Action", "Sci-Fi"],
                        "episodes": 26,
                        "status": "FINISHED",
                        "averageScore": 86,
                    }
                ],
            }
        }
    }


@respx.mock
def test_search_returns_page_info_and_animes(
    client, make_authenticated_anilist_user
):
    authenticated_user = make_authenticated_anilist_user(
        anilist_id=707,
        access_token="anilist-token-for-search",
    )

    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(200, json=_search_payload())
    )

    response = client.get(
        "/api/v1/animes",
        params={"search": "bebop"},
        headers=authenticated_user.headers,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["pageInfo"] == {"perPage": 10, "currentPage": 1, "hasNextPage": True}
    assert len(body["animes"]) == 1

    anime = body["animes"][0]
    assert anime["id"] == 55
    assert anime["genres"] == ["Action", "Sci-Fi"]
    assert anime["coverImage"]["large"] == "img.jpg"
    assert anime["coverImage"]["extraLarge"] is None
