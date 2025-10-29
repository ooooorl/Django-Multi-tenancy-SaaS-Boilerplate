import pytest

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:

    def test_create_user_success(self):
        user = User.objects.create_user(
            username="testuser",
            password="securepassword123",
            first_name="Test",
            last_name="User",
        )
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_staff is False
        assert str(user) == "testuser"

    def test_create_superuser_success(self):
        superuser = User.objects.create_superuser(
            username="adminuser", password="adminsecurepass"
        )
        assert superuser.username == "adminuser"
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.is_active is True

    @pytest.mark.parametrize(
        "method,username,password,error_field",
        [
            ("create_user", "", "pass", "username"),
            ("create_user", "testuser", None, "password"),
            ("create_superuser", "", "adminpass", "username"),
            ("create_superuser", "adminuser", None, "password"),
        ],
    )
    def test_user_creation_failures(self, method, username, password, error_field):
        with pytest.raises(ValueError) as exc:
            getattr(User.objects, method)(username=username, password=password)
        assert error_field in str(exc.value).lower()
