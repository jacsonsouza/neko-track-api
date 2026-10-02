"""Test double for :class:`app.modules.anilist.gateway.AnilistGateway`.

Integration tests override the gateway dependency with this fake instead of
mocking the HTTP transport: they assert on the recorded calls (access token,
query, variables) and answer with canned GraphQL ``data``. Envelope unwrapping,
timeouts and rate-limit translation belong to the real gateway and are covered
by ``tests/unit/test_anilist_gateway.py``.

The fake is duck-typed — FastAPI never checks the dependency's type.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GatewayCall:
    """One recorded gateway invocation."""

    method: str  # "exchange_code_for_token" | "viewer" | "graphql"
    access_token: str | None = None
    query: str | None = None
    variables: dict[str, Any] | None = None
    code: str | None = None


class FakeAnilistGateway:
    """Stands in for the gateway wired by the application lifespan."""

    def __init__(self) -> None:
        self.calls: list[GatewayCall] = []

        # Canned answers.
        self.access_token = "anilist-token"  # OAuth code exchange result
        self.viewer_payload: dict[str, Any] = {"id": 99, "name": "Jacson"}
        self.data: dict[str, Any] = {}  # GraphQL `data` object

        # Failures under test: set one and every call of that kind raises it.
        self.exchange_error: Exception | None = None
        self.viewer_error: Exception | None = None
        self.graphql_error: Exception | None = None

    # ------------------------------------------------------------- recording
    @property
    def last_call(self) -> GatewayCall:
        assert self.calls, "the AniList gateway was never called"
        return self.calls[-1]

    def graphql_calls(self) -> list[GatewayCall]:
        return [call for call in self.calls if call.method == "graphql"]

    # -------------------------------------------------------------- gateway
    async def aclose(self) -> None:
        return None

    async def exchange_code_for_token(self, code: str) -> str:
        self.calls.append(GatewayCall(method="exchange_code_for_token", code=code))

        if self.exchange_error is not None:
            raise self.exchange_error

        return self.access_token

    async def viewer(self, access_token: str) -> dict[str, Any]:
        self.calls.append(GatewayCall(method="viewer", access_token=access_token))

        if self.viewer_error is not None:
            raise self.viewer_error

        return self.viewer_payload

    async def graphql(
        self, *, access_token: str, query: str, variables: dict[str, Any]
    ) -> dict[str, Any]:
        self.calls.append(
            GatewayCall(
                method="graphql",
                access_token=access_token,
                query=query,
                variables=variables,
            )
        )

        if self.graphql_error is not None:
            raise self.graphql_error

        return self.data
