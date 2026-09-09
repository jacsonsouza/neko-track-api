import time

import pytest
from fastapi import HTTPException
from jose import jwt

from app.core.auth_dep import get_claims
from app.core.config import settings
from app.core.security import create_app_jwt


def test_get_claims_should_raise_401_when_auth_header_is_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_claims(None)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Missing or malformed authorization header."


def test_get_claims_should_return_auth_claims_when_token_is_valid():
    valid_token = create_app_jwt(user_id=1, anilist_id=99)

    claims = get_claims(valid_token)

    assert claims.user_id == 1
    assert claims.anilist_id == 99


def test_get_claims_should_return_auth_claims_without_anilist_id():
    payload = {
        "iss": settings.jwt_issuer,
        "sub": "1",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    token_without_anilist = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

    claims = get_claims(token_without_anilist)

    assert claims.user_id == 1
    assert claims.anilist_id is None


def test_get_claims_should_raise_401_when_token_format_is_malformed():
    with pytest.raises(HTTPException) as exc_info:
        get_claims("invalid-token-format")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token."


def test_get_claims_should_raise_401_when_issuer_is_untrusted():
    untrusted_payload = {
        "iss": "untrusted-issuer-identity",
        "sub": "1",
        "anilist_id": 99,
        "exp": int(time.time()) + 3600,
    }
    untrusted_token = jwt.encode(
        untrusted_payload, settings.jwt_secret, algorithm="HS256"
    )

    with pytest.raises(HTTPException) as exc_info:
        get_claims(untrusted_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token."


def test_get_claims_should_raise_401_when_token_is_expired():
    past_timestamp = int(time.time()) - 3600

    expired_payload = {
        "iss": settings.jwt_issuer,
        "sub": "1",
        "anilist_id": 99,
        "iat": past_timestamp - 60,
        "exp": past_timestamp,
    }
    expired_token = jwt.encode(expired_payload, settings.jwt_secret, algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        get_claims(expired_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has expired."


def test_get_claims_should_raise_401_when_signed_by_different_secret():
    payload = {
        "iss": settings.jwt_issuer,
        "sub": "1",
        "anilist_id": 99,
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        get_claims(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token."


def test_get_claims_should_raise_401_when_scheme_is_not_bearer():
    with pytest.raises(HTTPException) as exc_info:
        get_claims(None)
    assert exc_info.value.status_code == 401
