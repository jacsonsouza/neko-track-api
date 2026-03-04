import pytest

from app.core.crypto import decrypt_token, encrypt_token


def test_encrypt_decrypt_roundtrip():
    enc = encrypt_token("abc123")
    assert enc != "abc123"
    dec = decrypt_token(enc)
    assert dec == "abc123"


def test_decrypt_rejects_invalid():
    with pytest.raises(ValueError):
        decrypt_token("not-a-valid-token")
