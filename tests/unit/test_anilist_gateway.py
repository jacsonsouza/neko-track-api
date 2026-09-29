"""Unit tests for the AniList gateway: timeouts, rate limit and error mapping.

This is the only place where the HTTP transport itself is faked: the gateway
is the layer that talks to httpx, so respx belongs here. Integration tests
replace the gateway (see ``tests/fakes``), not the transport.
"""

import json

import httpx
import pytest
import respx

from app.core.config import settings
from app.modules.anilist.errors import (
    AnilistHttpError,
    AnilistRateLimitError,
    AnilistResponseError,
    AnilistTimeoutError,
)
from app.modules.anilist.gateway import (
    ANILIST_GRAPHQL_URL,
    AnilistGateway,
    create_gateway,
)


@pytest.fixture
def gateway():
    return AnilistGateway(httpx.AsyncClient())


# --------------------------------------------------------------- happy paths


@pytest.mark.asyncio
@respx.mock
async def test_graphql_returns_the_data_object(gateway):
    """The envelope is unwrapped here: services never see `{"data": ...}`."""
    route = respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(
            200, json={"data": {"Page": {"pageInfo": {"currentPage": 1}}}}
        )
    )

    data = await gateway.graphql(
        access_token="token-1", query="query Q", variables={"page": 1}
    )

    assert data == {"Page": {"pageInfo": {"currentPage": 1}}}

    request = route.calls[0].request
    assert request.headers["Authorization"] == "Bearer token-1"
    assert json.loads(request.content) == {
        "query": "query Q",
        "variables": {"page": 1},
    }


@pytest.mark.asyncio
@respx.mock
async def test_viewer_returns_the_viewer_object(gateway):
    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(
            200, json={"data": {"Viewer": {"id": 99, "name": "Jacson"}}}
        )
    )

    viewer = await gateway.viewer("token-1")

    assert viewer == {"id": 99, "name": "Jacson"}


@pytest.mark.asyncio
@respx.mock
async def test_exchange_code_returns_the_access_token(gateway):
    route = respx.post(
        "https://anilist.co/api/v2/oauth/token"
    ).mock(return_value=httpx.Response(200, json={"access_token": "tok"}))

    token = await gateway.exchange_code_for_token("the-code")

    assert token == "tok"

    payload = json.loads(route.calls[0].request.content)
    assert payload["grant_type"] == "authorization_code"
    assert payload["code"] == "the-code"
    assert payload["client_id"] == settings.anilist_client_id


# ----------------------------------------------------------- provider errors


@pytest.mark.asyncio
@respx.mock
async def test_graphql_errors_in_the_envelope_raise_response_error(gateway):
    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(
            200, json={"errors": [{"message": "Not found"}]}
        )
    )

    with pytest.raises(AnilistResponseError):
        await gateway.graphql(access_token="tok", query="query Q", variables={})


@pytest.mark.asyncio
@respx.mock
async def test_missing_data_field_raises_response_error(gateway):
    respx.post(ANILIST_GRAPHQL_URL).mock(return_value=httpx.Response(200, json={}))

    with pytest.raises(AnilistResponseError):
        await gateway.graphql(access_token="tok", query="query Q", variables={})


@pytest.mark.asyncio
@respx.mock
async def test_non_json_body_raises_response_error(gateway):
    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(200, text="<html>gateway</html>")
    )

    with pytest.raises(AnilistResponseError):
        await gateway.graphql(access_token="tok", query="query Q", variables={})


@pytest.mark.asyncio
@respx.mock
async def test_viewer_without_viewer_field_raises_response_error(gateway):
    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(200, json={"data": {"Viewer": None}})
    )

    with pytest.raises(AnilistResponseError):
        await gateway.viewer("tok")


@pytest.mark.asyncio
@respx.mock
async def test_exchange_code_without_access_token_raises_response_error(gateway):
    respx.post("https://anilist.co/api/v2/oauth/token").mock(
        return_value=httpx.Response(200, json={})
    )

    with pytest.raises(AnilistResponseError):
        await gateway.exchange_code_for_token("the-code")


@pytest.mark.asyncio
@respx.mock
async def test_upstream_status_error_raises_http_error(gateway):
    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(500, json={"error": "boom"})
    )

    with pytest.raises(AnilistHttpError):
        await gateway.graphql(access_token="tok", query="query Q", variables={})


# ------------------------------------------------------------- rate limiting


@pytest.mark.asyncio
@respx.mock
async def test_rate_limit_carries_the_retry_after_header(gateway):
    respx.post(ANILIST_GRAPHQL_URL).mock(
        return_value=httpx.Response(429, headers={"Retry-After": "42"})
    )

    with pytest.raises(AnilistRateLimitError) as exc_info:
        await gateway.graphql(access_token="tok", query="query Q", variables={})

    assert exc_info.value.retry_after == 42


@pytest.mark.asyncio
@respx.mock
async def test_rate_limit_without_retry_after_defaults_to_zero(gateway):
    respx.post(ANILIST_GRAPHQL_URL).mock(return_value=httpx.Response(429))

    with pytest.raises(AnilistRateLimitError) as exc_info:
        await gateway.graphql(access_token="tok", query="query Q", variables={})

    assert exc_info.value.retry_after == 0


# ------------------------------------------------------------------- timeouts


@pytest.mark.asyncio
@respx.mock
async def test_timeout_is_translated_to_a_gateway_timeout_error(gateway):
    respx.post(ANILIST_GRAPHQL_URL).mock(side_effect=httpx.ReadTimeout("slow"))

    with pytest.raises(AnilistTimeoutError):
        await gateway.graphql(access_token="tok", query="query Q", variables={})


@pytest.mark.asyncio
@respx.mock
async def test_connection_error_is_translated_to_an_http_error(gateway):
    respx.post(ANILIST_GRAPHQL_URL).mock(side_effect=httpx.ConnectError("down"))

    with pytest.raises(AnilistHttpError):
        await gateway.graphql(access_token="tok", query="query Q", variables={})


# ------------------------------------------------------------ timeout policy


@pytest.mark.asyncio
async def test_create_gateway_applies_the_configured_timeouts():
    """One timeout policy for every AniList call (no per-route timeouts)."""
    gateway = create_gateway()

    try:
        timeout = gateway._http.timeout  # the transport is the policy carrier
        assert timeout.read == settings.anilist_timeout_seconds
        assert timeout.write == settings.anilist_timeout_seconds
        assert timeout.connect == settings.anilist_connect_timeout_seconds
    finally:
        await gateway.aclose()
