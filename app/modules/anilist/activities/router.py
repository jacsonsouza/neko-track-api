import httpx
from fastapi import APIRouter, Depends, Query

from app.core.auth_dep import AuthClaims, get_claims
from app.db.session import get_db
from app.modules.anilist.activities.dto.paginated_activities_dto import (
    UserActivitiesDataDTO,
)
from app.modules.anilist.activities.service import (
    get_user_activities,
    toggle_activity_like,
)
from app.modules.auth.token_repo import get_anilist_access_token_for_user

router = APIRouter(prefix="/anilist/user/activities", tags=["anilist", "activities"])


@router.get("", response_model=UserActivitiesDataDTO)
async def user_activities(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
) -> UserActivitiesDataDTO:
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await get_user_activities(
            http, access_token, claims.anilist_id, page, per_page
        )


@router.post("/{activity_id}/like")
async def toggle_like(
    activity_id: int,
    type: str,
    claims: AuthClaims = Depends(get_claims),
    db=Depends(get_db),
):
    access_token = get_anilist_access_token_for_user(db, claims.user_id)

    async with httpx.AsyncClient(timeout=15) as http:
        return await toggle_activity_like(http, access_token, activity_id, type)
