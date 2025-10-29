import factory

from user.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False

    @classmethod
    def create_superuser(cls, **kwargs):
        """Create a superuser with the given parameters."""
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        return cls.create(**kwargs)
