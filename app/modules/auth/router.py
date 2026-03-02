from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.security import generate_state, save_state
from app.modules.auth.service import handle_anilist_callback

router = APIRouter(prefix="/auth/anilist", tags=["auth"])


@router.get("/start")
def start():
    state = generate_state()
    save_state(state)

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
async def callback(code: str, state: str):
    token = await handle_anilist_callback(code=code, state=state)
    return RedirectResponse(
        url=f"{settings.mobile_deeplink}?token={token}",
        status_code=302,
    )
