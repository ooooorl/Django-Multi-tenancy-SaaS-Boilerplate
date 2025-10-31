import factory

from user.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    tenant = None
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "Password123!")

    @classmethod
    def create_superuser(cls, **kwargs):
        password = kwargs.pop("password", "Password123!")
        user = cls(is_superuser=True, is_staff=True, **kwargs)
        user.set_password(password)
        user.save()
        return user
