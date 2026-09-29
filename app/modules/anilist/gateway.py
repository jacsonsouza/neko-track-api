"""AniList gateway: the single place where the API talks to AniList.

Responsibilities kept here on purpose:

* the shared ``httpx.AsyncClient`` — created once by the application lifespan
  (``create_gateway``) and injected into routes by ``get_anilist_gateway``,
  never built inside a route;
* one timeout policy (``ANILIST_*_TIMEOUT_SECONDS``) applied to the transport;
* one rate-limit policy: a 429 becomes :class:`AnilistRateLimitError` carrying
  ``Retry-After`` — no hidden retries inside a request;
* one error vocabulary (:mod:`app.modules.anilist.errors`) instead of raw
  ``httpx``/``ValueError`` leaks;
* parsing of the GraphQL envelope: services receive ``data`` and never see
  ``{"data": ..., "errors": ...}``.

Application services depend on this gateway, never on ``httpx``. Tests replace
it with ``tests.fakes.FakeAnilistGateway``, which implements the same three
coroutines.
"""

from typing import Any

import httpx
from fastapi import Request

from app.core.config import settings
from app.modules.anilist.errors import (
    AnilistHttpError,
    AnilistRateLimitError,
    AnilistResponseError,
    AnilistTimeoutError,
)

ANILIST_OAUTH_TOKEN_URL = "https://anilist.co/api/v2/oauth/token"
ANILIST_GRAPHQL_URL = "https://graphql.anilist.co"

VIEWER_QUERY = """
query {
  Viewer {
    id
    name
    mediaListOptions {
      scoreFormat
    }
  }
}
"""


def _retry_after(response: httpx.Response) -> int:
    """Read the numeric ``Retry-After`` header (seconds), falling back to 0."""
    raw = response.headers.get("Retry-After", "")
    try:
        return max(int(raw), 0)
    except ValueError:
        return 0


class AnilistGateway:
    """Talks to AniList with one timeout, one rate-limit and one error policy."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def aclose(self) -> None:
        await self._http.aclose()

    # ------------------------------------------------------------------ OAuth
    async def exchange_code_for_token(self, code: str) -> str:
        data = await self._post_json(
            ANILIST_OAUTH_TOKEN_URL,
            json={
                "grant_type": "authorization_code",
                "client_id": settings.anilist_client_id,
                "client_secret": settings.anilist_client_secret,
                "redirect_uri": f"{settings.app_base_url}/auth/anilist/callback",
                "code": code,
            },
        )

        token = data.get("access_token") if isinstance(data, dict) else None
        if not token:
            raise AnilistResponseError(
                "AniList token endpoint returned no access_token"
            )

        return str(token)

    # ---------------------------------------------------------------- GraphQL
    async def viewer(self, access_token: str) -> dict[str, Any]:
        data = await self.graphql(
            access_token=access_token, query=VIEWER_QUERY, variables={}
        )

        viewer = data.get("Viewer")
        if not viewer:
            raise AnilistResponseError("AniList returned no Viewer")

        return viewer

    async def graphql(
        self, *, access_token: str, query: str, variables: dict[str, Any]
    ) -> dict[str, Any]:
        envelope = await self._post_json(
            ANILIST_GRAPHQL_URL,
            json={"query": query, "variables": variables or {}},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/json",
                "Accept": "application/json",
            },
        )

        if not isinstance(envelope, dict):
            raise AnilistResponseError(
                f"AniList returned a non-object payload: {envelope!r:.200}"
            )

        if envelope.get("errors"):
            raise AnilistResponseError(
                f"AniList GraphQL errors: {envelope['errors']!r:.200}"
            )

        data = envelope.get("data")
        if not isinstance(data, dict):
            raise AnilistResponseError(
                f"AniList returned no data field: {envelope!r:.200}"
            )

        return data

    # ---------------------------------------------------------------- helpers
    async def _post_json(self, url: str, **kwargs: Any) -> Any:
        """POST once, normalising every failure into an ``AnilistError``."""
        try:
            response = await self._http.post(url, **kwargs)
        except httpx.TimeoutException as exc:
            raise AnilistTimeoutError(f"AniList timed out calling {url}") from exc
        except httpx.HTTPError as exc:
            raise AnilistHttpError(
                f"AniList unreachable ({exc.__class__.__name__})"
            ) from exc

        if response.status_code == 429:
            raise AnilistRateLimitError(_retry_after(response))

        if response.is_error:
            raise AnilistHttpError(
                f"AniList answered {response.status_code} calling {url}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise AnilistResponseError(
                f"AniList returned a non-JSON body calling {url}"
            ) from exc


def create_gateway() -> AnilistGateway:
    """Build the gateway with the shared timeout policy.

    Called once from the application lifespan in :mod:`app.main`.
    """
    timeout = httpx.Timeout(
        settings.anilist_timeout_seconds,
        connect=settings.anilist_connect_timeout_seconds,
    )
    return AnilistGateway(httpx.AsyncClient(timeout=timeout))


def get_anilist_gateway(request: Request) -> AnilistGateway:
    """Route dependency: the gateway owned by the application lifespan."""
    gateway = getattr(request.app.state, "anilist_gateway", None)

    if gateway is None:
        raise RuntimeError(
            "AniList gateway is not initialised: the application lifespan "
            "did not run (use `with TestClient(app)` in tests)."
        )

    return gateway
