import base64
import hashlib
import hmac
import json
import os
import time

from app.core.config import settings

_STATE_SECRET = settings.jwt_secret.encode()


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def __b64url_decode(data: str) -> bytes:
    pad = "=" * (len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def create_state(ttl_seconds: int = 600) -> str:
    payload = {"n": _b64url(os.urandom(16)), "exp": int(time.time() + ttl_seconds)}
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    payload_b64 = _b64url(payload_bytes)
    sig = hmac.new(_STATE_SECRET, payload_b64.encode(), hashlib.sha256).digest()
    sig_b64 = _b64url(sig)

    return f"{payload_b64}.{sig_b64}"


def validate_state(state: str) -> bool:
    try:
        payload_b64, sig_b64 = state.split(".", 1)
    except ValueError:
        return False

    expected_sig = hmac.new(_STATE_SECRET, payload_b64.encode(), hashlib.sha256).digest
    expected_sig_b64 = _b64url(expected_sig)

    if not hmac.compare_digest(expected_sig_b64, sig_b64):
        return False

    try:
        payload = json.loads(__b64url_decode(payload_b64))
        exp = int(payload["exp"])
    except Exception:
        return False

    return time.time() <= exp
