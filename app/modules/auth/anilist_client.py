import json
from typing import Any
from wsgiref import headers

import httpx

from app.core.config import settings

ANILIST_OAUTH_TOKEN_URL = "https://anilist.co/api/v2/oauth/token"
ANILIST_GRAPHQL_URL = "https://graphql.anilist.co"


class AnilistClientError(RuntimeError):
    pass


class AnilistClient:
    def __init__(self, http: httpx.AsyncClient):
        self.http = http

    async def exchange_code_for_token(self, code: str) -> str:
        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.anilist_client_id,
            "client_secret": settings.anilist_client_secret,
            "redirect_uri": f"{settings.app_base_url}/auth/anilist/callback",
            "code": code,
        }
        r = await self.http.post(ANILIST_OAUTH_TOKEN_URL, json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        token = data.get("access_token")
        if not token:
            raise ValueError(f"Token endpoint sem access_token: {data}")
        return token

    async def viewer(self, access_token: str) -> dict:
        query = """
        query {
        Viewer {
            id
            name
        }
        }
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        r = await self.http.post(
            ANILIST_GRAPHQL_URL,
            json={"query": query},
            headers=headers,
            timeout=15,
        )
        r.raise_for_status()

        payload = r.json()

        if payload.get("errors"):
            raise ValueError(f"AniList GraphQL errors: {payload['errors']}")

        data = payload.get("data")
        if not data or not data.get("Viewer"):
            raise ValueError(f"AniList retornou data vazia: {payload}")

        return data["Viewer"]

    async def graphql(
        self, *, access_token: str, query: str, variables: dict[str, Any]
    ):
        payload: dict[str, Any] = {"query": query, "variables": variables or {}}

        res = await self.http.post(
            ANILIST_GRAPHQL_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            data = res.json()
        except Exception as e:
            raise AnilistClientError(
                f"graphql invalid json: {res.status_code} {res.text}"
            ) from e

        if res.status_code != 200:
            raise AnilistClientError(f"graphql errors: {data['errors']}")

        if not isinstance(data, dict) or "data" not in data:
            raise AnilistClientError(f"graphql missing data field: {data}")

        return data
