import factory
from faker import Factory as FakerFactory
from pytest_factoryboy import register

from app.db.models.user import User

faker = FakerFactory.create()


@register
class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    name = faker.name()
    anilist_id = faker.random_int(min=0, max=100)
