import os
from dataclasses import dataclass

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from pytest_factoryboy import register
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models.user import User
from app.db.session import get_db
from app.core.crypto import encrypt_token
from app.core.security import create_app_jwt
from app.main import app
from tests.factories.anilist_token_factory import AnilistTokenFactory
from tests.factories.user_factory import UserFactory

load_dotenv()


@dataclass(frozen=True)
class AuthenticatedAniListUser:
    user: User
    access_token: str
    headers: dict[str, str]


@pytest.fixture
def make_authenticated_anilist_user():
    def _make(
        *,
        anilist_id: int,
        access_token: str,
        name: str = "Test user",
    ) -> AuthenticatedAniListUser:
        anilist_token = AnilistTokenFactory.create(
            user__name=name,
            user__anilist_id=anilist_id,
            access_token_encrypted=encrypt_token(access_token),
        )

        app_jwt = create_app_jwt(
            user_id=anilist_token.user.id,
            anilist_id=anilist_token.user.anilist_id,
        )

        return AuthenticatedAniListUser(
            user=anilist_token.user,
            access_token=access_token,
            headers={"Authorization": f"Bearer {app_jwt}"},
        )

    return _make


@pytest.fixture(scope="session")
def test_db_url():
    return os.environ["DATABASE_URL_DIRECT"]


@pytest.fixture()
def db_session(test_db_url):
    engine = create_engine(test_db_url, pool_pre_ping=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def setup_factory_session(db_session):
    factories = [UserFactory, AnilistTokenFactory]

    for factory in factories:
        factory._meta.sqlalchemy_session = db_session

    yield

    for factory in factories:
        factory._meta.sqlalchemy_session = None
