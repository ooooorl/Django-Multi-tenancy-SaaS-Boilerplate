import json

import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from tenant.tests.v1.factories import TenantFactory
from user.tests.v1.factories import UserFactory


@pytest.fixture
@pytest.mark.django_db
def tenant():
    return TenantFactory()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
@pytest.mark.django_db
def user(tenant):
    return UserFactory(tenant=tenant)


@pytest.fixture
def endpoints():
    return {
        "register": reverse("register-user"),
        "login": reverse("login-user"),
        "refresh": reverse("refresh-token"),
        "logout": reverse("logout-user"),
    }


@pytest.mark.django_db
def test_register_user_fail(api_client, endpoints, tenant):
    """Register user fail with blank payloads."""
    payload = {"email": "", "password": "", "first_name": "", "last_name": ""}
    tenant_subdomain = tenant.subdomain

    response = api_client.post(
        endpoints["register"],
        payload,
        format="json",
        HTTP_HOST=f"{tenant_subdomain}.localhost",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "email": ["This field may not be blank."],
        "password": ["This field is required"],
    }


@pytest.mark.django_db
def test_register_user_fail_without_subdomain(api_client, endpoints):
    """Register user fail with empty subdomain."""
    payload = {"email": "", "password": "", "first_name": "", "last_name": ""}

    response = api_client.post(
        endpoints["register"],
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"detail": "Tenant information is missing."}


@pytest.mark.django_db
def test_register_user_success(api_client, endpoints, tenant):
    """Register user twice"""
    tenant_subdomain = tenant.subdomain
    reg_payload = {"email": "test@test.com", "password": "Testing@123"}

    # Register user
    response = api_client.post(
        endpoints["register"],
        reg_payload,
        format="json",
        HTTP_HOST=f"{tenant_subdomain}.localhost",
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Register again with the same credentials
    reg_payload = {"email": "test@test.com", "password": "test"}
    response = api_client.post(
        endpoints["register"],
        reg_payload,
        format="json",
        HTTP_HOST=f"{tenant_subdomain}.localhost",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "email": ["user with this email already exists."],
        "password": [
            "Password must contain at least one uppercase letter.",
            "Ensure this field has at least 8 characters.",
        ],
    }


@pytest.mark.django_db
def test_login_user_fail_without_subdomain(api_client, endpoints):
    """
    User login fail with empty subdomain.
    """
    payload = {"email": "", "password": ""}

    response = api_client.post(endpoints["login"], payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"detail": "Tenant information is missing."}


@pytest.mark.django_db
def test_login_user_fail(api_client, endpoints, tenant):
    """User login fail with invalid credentials."""
    tenant_subdomain = tenant.subdomain
    payload = {"email": "invalid@test.com", "password": "wrongpassword"}

    response = api_client.post(
        endpoints["login"],
        payload,
        format="json",
        HTTP_HOST=f"{tenant_subdomain}.localhost",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {
        "detail": "No active account found with the given credentials"
    }


@pytest.mark.django_db
def test_login_user_does_not_belong_to_tenant(api_client, endpoints):
    # Create two tenants
    tenant_1 = TenantFactory(subdomain="tenant1")
    tenant_2 = TenantFactory(subdomain="tenant2")

    # Create a user in tenant_1 with hashed password
    UserFactory(email="user@tenant1.com", password="Password123!", tenant=tenant_1)

    # Attempt to login using tenant_2 subdomain
    payload = {"email": "user@tenant1.com", "password": "Password123!"}
    response = api_client.post(
        endpoints["login"],
        payload,
        format="json",
        HTTP_HOST=f"{tenant_2.subdomain}.localhost",
    )

    try:
        response_data = response.data
    except AttributeError:
        response_data = json.loads(response.content)

    # The login should fail because the user does not belong to tenant_2
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_data == {"detail": ["User does not belong to this tenant."]}


@pytest.mark.django_db
def test_authentication_cookie_only_true(api_client, endpoints, tenant):
    tenant_subdomain = tenant.subdomain
    reg_payload = {"email": "test@test.com", "password": "Testing@123"}

    # Register user
    response = api_client.post(
        endpoints["register"],
        reg_payload,
        format="json",
        HTTP_HOST=f"{tenant_subdomain}.localhost",
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Login with cookies
    login_payload = {**reg_payload, "is_http_cookie_only": True}
    response = api_client.post(
        endpoints["login"],
        login_payload,
        format="json",
        HTTP_HOST=f"{tenant_subdomain}.localhost",
    )
    assert response.status_code == status.HTTP_200_OK
    # Cookies are automatically set in api_client.cookies
    assert "access_expiration" in response.data
    assert "refresh_expiration" in response.data
    assert "user" in response.data

    # Refresh token using cookies
    refresh_payload = {"is_http_cookie_only": True}
    response = api_client.post(
        endpoints["refresh"],
        refresh_payload,
        format="json",
        HTTP_HOST=f"{tenant_subdomain}.localhost",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_expiration" in response.data
    assert "refresh_expiration" in response.data

    # Logout using cookies
    logout_payload = {"is_http_cookie_only": True}
    response = api_client.post(
        endpoints["logout"],
        logout_payload,
        format="json",
        HTTP_HOST=f"{tenant_subdomain}.localhost",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"detail": "Successfully logged out"}


@pytest.mark.django_db
def test_authentication_cookie_only_false(api_client, endpoints, tenant):
    reg_payload = {"email": "test@test.com", "password": "Testing@123"}
    tenant_subdomain = tenant.subdomain

    # Register
    response = api_client.post(
        endpoints["register"],
        reg_payload,
        format="json",
        HTTP_HOST=f"{tenant_subdomain}.localhost",
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Login
    login_payload = {**reg_payload, "is_http_cookie_only": False}

    response = api_client.post(
        endpoints["login"],
        login_payload,
        format="json",
        HTTP_HOST=f"{tenant_subdomain}.localhost",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data
    assert "user" in response.data

    refresh_token = response.data["refresh"]

    # Refresh token
    response = api_client.post(
        endpoints["refresh"],
        {"refresh": refresh_token},
        format="json",
        HTTP_HOST=f"{tenant_subdomain}.localhost",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data
