import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.profile.dto import UserProfileDTO
from app.modules.anilist.profile.service import get_profile, viewer
from app.modules.auth.token_repo import get_anilist_access_token_for_user

router = APIRouter(prefix="/anilist", tags=["anilist", "profile"])


@router.get("/viewer")
async def get_viewer(
    claims: AuthClaims = Depends(get_claims), db: Session = Depends(get_db)
):
    return await viewer(db, user_id=claims.user_id)


@router.get("/profile", response_model=UserProfileDTO)
async def profile(
    claims: AuthClaims = Depends(get_claims), db=Depends(get_db)
) -> UserProfileDTO:
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await get_profile(http, access_token)
