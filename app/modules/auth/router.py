from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.auth_dep import AuthClaims, get_claims
from app.core.config import settings
from app.core.oauth_state import create_state
from app.db.session import get_db
from app.modules.anilist.gateway import AnilistGateway, get_anilist_gateway
from app.modules.auth.schemas import MeResponse
from app.modules.auth.service import login_with_anilist_callback
from app.modules.users.repo import get_by_id as get_by_user_id

router = APIRouter(prefix="/auth/anilist", tags=["auth"])


@router.get(
    "/start",
    status_code=302,
    response_class=RedirectResponse,
    responses={"302": {"description": "Redirect to the AniList authorize URL"}},
)
def start() -> RedirectResponse:
    state = create_state()

    redirect_uri = f"{settings.app_base_url}/auth/anilist/callback"
    url = (
        "https://anilist.co/api/v2/oauth/authorize"
        f"?client_id={settings.anilist_client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        f"&state={state}"
    )
    return RedirectResponse(url=url, status_code=302)


@router.get(
    "/callback",
    status_code=302,
    response_class=RedirectResponse,
    responses={
        "302": {"description": "Redirect to the app deep link carrying the JWT"},
        "400": {"description": "Missing, invalid or replayed state"},
    },
)
async def callback(
    code: str,
    state: str,
    gateway: Annotated[AnilistGateway, Depends(get_anilist_gateway)],
    db: Session = Depends(get_db),
) -> RedirectResponse:
    result = await login_with_anilist_callback(
        db, gateway, code=code, state=state
    )

    return RedirectResponse(
        url=f"{settings.mobile_deeplink}?token={result.app_jwt}",
        status_code=302,
    )


@router.get("/me", response_model=MeResponse)
def me(
    claims: AuthClaims = Depends(get_claims), db: Session = Depends(get_db)
) -> MeResponse:
    user = get_by_user_id(db, claims.user_id)

    if not user:
        return MeResponse(
            id=claims.user_id,
            anilist_id=claims.anilist_id,
            name=None,
            exists=False,
        )

    return MeResponse(
        id=user.id,
        anilist_id=user.anilist_id,
        name=user.name,
        exists=True,
    )
