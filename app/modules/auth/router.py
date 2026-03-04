from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from pytest import Session

from app.core.auth_dep import AuthClaims, claims
from app.core.config import settings
from app.core.oauth_state import create_state
from app.db.session import get_db
from app.modules.auth.service import login_with_anilist_callback
from app.modules.auth.token_repo import get_by_user_id

router = APIRouter(prefix="/auth/anilist", tags=["auth"])


@router.get("/start")
def start():
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


@router.get("/callback")
async def callback(code: str, state: str, db: Session = Depends(get_db)):
    result = await login_with_anilist_callback(db, code, state)

    return RedirectResponse(
        url=f"{settings.mobile_deeplink}?token={result.app_jwt}",
        status_code=302,
    )


@router.get("/me")
def me(claims: AuthClaims = Depends(claims), db: Session = Depends(get_db)):
    user = get_by_user_id(db, claims.user_id)

    if not user:
        return {
            "user_id": claims.user_id,
            "anilist_id": claims.anilist_id,
            "exists": False,
        }

    return {"id": user.id, "anilist_id": user.anilist_id, "name": user.name}
