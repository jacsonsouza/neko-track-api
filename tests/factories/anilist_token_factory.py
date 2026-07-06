import factory
from pytest_factoryboy import register

from app.db.models.anilist_token import AnilistToken
from tests.factories.user_factory import UserFactory


@register
class AnilistTokenFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AnilistToken
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    user = factory.SubFactory(UserFactory)
