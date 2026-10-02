from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


@dataclass(frozen=True)
class AuthClaims:
    user_id: int
    anilist_id: int | None


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=["HS256"], issuer=settings.jwt_issuer
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer error='token_expired'"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer error='invalid_token'"},
        )


def get_claims(token: str | None = Depends(oauth2_scheme)) -> AuthClaims:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = _decode_token(token)

    return AuthClaims(
        user_id=int(payload["sub"]),
        anilist_id=(
            int(payload["anilist_id"])
            if payload.get("anilist_id") is not None
            else None
        ),
    )
