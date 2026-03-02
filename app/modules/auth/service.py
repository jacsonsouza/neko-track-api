from os import name

import httpx
from fastapi import HTTPException

from app.core.security import consume_state, create_app_jwt
from app.modules.auth.anilist_client import AnilistClient

_USERS: dict[int, dict] = {}
_NEXT_ID = 1


def _upsert_user(anilist_id: int, name: str) -> int:
    global _NEXT_ID
    for uid, u in _USERS.items():
        if u["anilist_id"] == anilist_id:
            u["name"] = name
            return uid
    uid = _NEXT_ID
    _NEXT_ID += 1
    _USERS[uid] = {"anilist_id": anilist_id, "name": name}
    return uid


async def handle_anilist_callback(code: str, state: str) -> str:
    if not consume_state(state):
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    async with httpx.AsyncClient() as http:
        client = AnilistClient(http)
        token = await client.exchange_code_for_token(code)
        viewer = await client.viewer(token)

    user_id = _upsert_user(anilist_id=int(viewer["id"]), name=str(viewer["name"]))
    app_jwt = create_app_jwt(user_id=user_id, anilist_id=int(viewer["id"]))
    return app_jwt
