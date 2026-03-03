from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.timestamp_mixin import TimestampMixin


class AnilistToken(Base, TimestampMixin):
    __tablename__ = "anilist_tokens"
    __table_args__ = (UniqueConstraint("user_id", name="uq_anilist_tokens_user_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    access_token_encrypted: Mapped[str] = mapped_column(String, nullable=False)

    user = relationship("User", back_populates="tokens")
