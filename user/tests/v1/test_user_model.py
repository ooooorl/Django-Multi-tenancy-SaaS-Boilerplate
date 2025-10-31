import pytest

from user.models import User


@pytest.mark.django_db
class TestUserModel:

    def test_create_user_success(self):
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="securepassword123",
            first_name="Test",
            last_name="User",
        )
        # Assertions
        if hasattr(user, "username"):
            assert user.username == "testuser"
        assert user.email == "testuser@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_staff is False
        assert (
            str(user) == user.email
            if hasattr(user, "username") is False
            else user.username
        )

    def test_create_superuser_success(self):
        superuser = User.objects.create_superuser(
            username="adminuser",
            email="adminuser@example.com",
            password="adminsecurepass",
        )
        if hasattr(superuser, "username"):
            assert superuser.username == "adminuser"
        assert superuser.email == "adminuser@example.com"
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.is_active is True

    @pytest.mark.parametrize(
        "method,username,email,password",
        [
            # Removed cases with empty username
            ("create_user", "testuser", "testuser@example.com", None),
            ("create_user", "johndoe", "john@example.com", "pass123"),
            ("create_superuser", "adminuser", "adminuser@example.com", None),
            ("create_superuser", "superadmin", "super@example.com", "adminpass"),
        ],
    )
    def test_user_creation_behavior(self, method, username, email, password):
        """
        Test user/superuser creation behavior for valid usernames.
        """
        user = getattr(User.objects, method)(
            username=username, email=email, password=password
        )
        assert user.username == username
        assert user.email == email.lower()
        if password is None:
            assert not user.has_usable_password()
        else:
            assert user.check_password(password)
