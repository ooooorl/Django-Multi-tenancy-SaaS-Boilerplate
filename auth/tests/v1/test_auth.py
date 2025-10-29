import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from user.tests.v1.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
@pytest.mark.django_db
def user():
    return UserFactory()


@pytest.fixture
def endpoints():
    return {
        "register": reverse("register-user"),
        "login": reverse("login-user"),
        "refresh": reverse("refresh-token"),
        "logout": reverse("logout-user"),
    }


@pytest.mark.django_db
def test_register_user_fail(api_client, endpoints):
    payload = {"username": "", "password": "", "first_name": "", "last_name": ""}

    response = api_client.post(endpoints["register"], payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "username": ["This field may not be blank."],
        "password": ["This field is required"],
    }


@pytest.mark.django_db
def test_register_user_success(api_client, endpoints):
    """Register user twice"""
    reg_payload = {"username": "test@test.com", "password": "Testing@123"}

    # Register user
    response = api_client.post(endpoints["register"], reg_payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    # Register again with the same credentials
    reg_payload = {"username": "test@test.com", "password": "test"}
    response = api_client.post(endpoints["register"], reg_payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "username": ["user with this username already exists."],
        "password": [
            "Password must contain at least one uppercase letter.",
            "Ensure this field has at least 8 characters.",
        ],
    }


@pytest.mark.django_db
def test_login_user_fail(api_client, endpoints):
    payload = {"username": "", "password": ""}

    response = api_client.post(endpoints["login"], payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "username": ["This field may not be blank."],
        "password": ["This field may not be blank."],
    }


@pytest.mark.django_db
def test_authentication_cookie_only_true(api_client, endpoints):
    reg_payload = {"username": "test@test.com", "password": "Testing@123"}

    # Register user
    response = api_client.post(endpoints["register"], reg_payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    # Login with cookies
    login_payload = {**reg_payload, "is_http_cookie_only": True}

    response = api_client.post(endpoints["login"], login_payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "access_expiration" in response.data
    assert "refresh_expiration" in response.data
    assert "user" in response.data

    # Refresh token with cookies
    refresh_payload = {"is_http_cookie_only": True}
    response = api_client.post(endpoints["refresh"], refresh_payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "access_expiration" in response.data
    assert "refresh_expiration" in response.data

    # Logout with cookies
    response = api_client.post(endpoints["logout"], refresh_payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"detail": "Successfully logged out"}


@pytest.mark.django_db
def test_authentication_cookie_only_false(api_client, endpoints, user):
    reg_payload = {"username": "test@test.com", "password": "Testing@123"}

    # Register
    response = api_client.post(endpoints["register"], reg_payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    # Login
    login_payload = {**reg_payload, "is_http_cookie_only": False}

    response = api_client.post(endpoints["login"], login_payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data
    assert "user" in response.data

    refresh_token = response.data["refresh"]

    # Refresh token
    response = api_client.post(
        endpoints["refresh"], {"refresh": refresh_token}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_logout_cookie_only_false(api_client, endpoints, user):
    reg_payload = {"username": "test@test.com", "password": "Testing@123"}

    # Register
    response = api_client.post(endpoints["register"], reg_payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    # Login
    login_payload = {**reg_payload, "is_http_cookie_only": False}

    response = api_client.post(endpoints["login"], login_payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data
    assert "user" in response.data

    refresh_token = response.data["refresh"]

    # Logout with Authorization header or force_authenticate
    api_client.force_authenticate(user=user)
    response = api_client.post(
        endpoints["logout"], {"refresh": refresh_token}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"detail": "Successfully logged out"}
