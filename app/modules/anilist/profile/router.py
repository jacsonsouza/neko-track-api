from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.gateway import AnilistGateway, get_anilist_gateway
from app.modules.anilist.profile.schemas import UserProfileResponse, ViewerResponse
from app.modules.anilist.profile.service import get_profile, viewer
from app.modules.auth.dependencies import get_current_anilist_access_token

router = APIRouter(prefix="/api/v1/me", tags=["anilist", "profile"])


@router.get("/viewer", response_model=ViewerResponse)
async def get_viewer(
    gateway: Annotated[AnilistGateway, Depends(get_anilist_gateway)],
    claims: AuthClaims = Depends(get_claims),
    db: Session = Depends(get_db),
) -> ViewerResponse:
    return await viewer(gateway, db, user_id=claims.user_id)


@router.get("/profile", response_model=UserProfileResponse)
async def profile(
    gateway: Annotated[AnilistGateway, Depends(get_anilist_gateway)],
    anilist_access_token: Annotated[
        str, Depends(get_current_anilist_access_token)
    ] = None,
) -> UserProfileResponse:
    return await get_profile(gateway, anilist_access_token)
