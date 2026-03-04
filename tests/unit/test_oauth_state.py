import time

from app.core.oauth_state import create_state, validate_state


def test_state_valid():
    state = create_state(ttl_seconds=60)
    assert validate_state(state) is True


def test_state_tampered_is_invalid():
    state = create_state(ttl_seconds=60)
    payload, sig = state.split(".", 1)
    tampered = payload[:-1] + ("A" if payload[-1] != "A" else "B")
    assert validate_state(f"{tampered}.{sig}") is False


def test_state_expires():
    state = create_state(ttl_seconds=1)
    time.sleep(2)
    assert validate_state(state) is False
