import pytest
from fastapi import HTTPException

from app.core.auth_dep import get_claims
from app.core.security import create_app_jwt


def test_get_cliams_missing_header():
    with pytest.raises(HTTPException) as e:
        get_claims(None)
    assert e.value.status_code == 401


def test_get_claims_valid_token():
    token = create_app_jwt(user_id=1, anilist_id=99)
    claims = get_claims(f"Bearer {token}")
    assert claims.user_id == 1
    assert claims.anilist_id == 99
