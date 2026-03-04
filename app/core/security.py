import base64
import datetime
import os
from datetime import datetime, timedelta, timezone
from hashlib import algorithms_available

from jose import jwt

from app.core.config import settings


def generate_state() -> str:
    return base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")


def create_app_jwt(user_id: int, anilist_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "iss": settings.jwt_issuer,
        "sub": str(user_id),
        "anilist_id": anilist_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
