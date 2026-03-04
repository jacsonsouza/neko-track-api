from dataclasses import dataclass

from fastapi import Header, HTTPException
from jose import JWTError, jwt

from app.core.config import settings


@dataclass(frozen=True)
class AuthClaims:
    user_id: int
    anilist_id: int


def get_claims(authorization: str | None = Header(default=None)) -> AuthClaims:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return AuthClaims(
            user_id=int(payload["sub"]), anilist_id=int(payload["anilist_id"])
        )
    except (JWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid token")
