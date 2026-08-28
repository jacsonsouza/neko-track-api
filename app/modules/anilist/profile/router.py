from typing import Annotated

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.profile.dto import UserProfileDTO
from app.modules.anilist.profile.service import get_profile, viewer
from app.modules.auth.dependencies import get_current_anilist_access_token

router = APIRouter(prefix="/api/v1/me", tags=["anilist", "profile"])


@router.get("/viewer")
async def get_viewer(
    claims: AuthClaims = Depends(get_claims), db: Session = Depends(get_db)
):
    return await viewer(db, user_id=claims.user_id)


@router.get("/profile", response_model=UserProfileDTO)
async def profile(
    anilist_access_token: Annotated[
        str, Depends(get_current_anilist_access_token)
    ] = None,
) -> UserProfileDTO:
    async with httpx.AsyncClient(timeout=15) as http:
        return await get_profile(http, anilist_access_token)
