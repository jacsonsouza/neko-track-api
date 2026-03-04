from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

_fernet = Fernet(settings.token_enc_key.encode())


def encrypt_token(token: str) -> str:
    return _fernet.encrypt(token.encode()).decode()


def decrypt_token(token_encrypted: str) -> str:
    try:
        return _fernet.decrypt(token_encrypted.encode()).decode()
    except InvalidToken:
        raise ValueError("Invalid encrypted token")
