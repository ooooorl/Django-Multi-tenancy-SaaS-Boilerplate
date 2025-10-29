import factory

from user.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")

    @factory.post_generation
    def set_user_password(self, create, extracted, **kwargs):
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password(factory.Faker("password").generate())

    @classmethod
    def create_superuser(cls, **kwargs):
        """Return created superuser instance."""
        return cls(is_superuser=True, is_staff=True, **kwargs)
