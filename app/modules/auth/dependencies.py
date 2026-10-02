from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.core.auth_dep import AuthClaims, get_claims
from app.core.crypto import decrypt_token
from app.db.session import get_db
from app.modules.auth.token_repository import AnilistTokenRepository


def get_token_repository(
    db: Annotated[Session, Depends(get_db)],
) -> AnilistTokenRepository:
    return AnilistTokenRepository(db)


def get_current_anilist_access_token(
    claims: Annotated[AuthClaims, Depends(get_claims)],
    token_repository: Annotated[
        AnilistTokenRepository,
        Depends(get_token_repository),
    ],
) -> str:
    encrypted_token = token_repository.find_encrypted_by_user_id(claims.user_id)

    if encrypted_token is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AniList account is not connected",
        )

    return decrypt_token(encrypted_token)
