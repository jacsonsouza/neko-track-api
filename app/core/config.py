from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    app_base_url: str = "http://localhost:8000"
    mobile_deeplink: str = "nekotrack://auth"

    anilist_client_id: str
    anilist_client_secret: str

    jwt_secret: str
    jwt_issuer: str = "neko-track"
    jwt_expire_minutes: int = 60 * 24 * 7

    database_url_pooled: str
    database_url_direct: str
    token_enc_key: str


settings = Settings()
