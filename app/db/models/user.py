from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.timestamp_mixin import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    anilist_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)

    token = relationship("AnilistToken", back_populates="user", uselist=False)
