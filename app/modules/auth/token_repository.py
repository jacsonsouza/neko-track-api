from sqlalchemy.orm import Session

from app.db.models.anilist_token import AnilistToken


class AnilistTokenRepository:
    def __init__(self, db: Session):
        self._db = db

    def find_encrypted_by_user_id(self, user_id: int) -> str | None:
        token = (
            self._db.query(AnilistToken)
            .filter(AnilistToken.user_id == user_id)
            .one_or_none()
        )

        return token.access_token_encrypted if token else None
