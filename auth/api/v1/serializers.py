import logging
from typing import Any, Dict

from dj_rest_auth.jwt_auth import CookieTokenRefreshSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

from django.contrib.auth.models import update_last_login
from django.db import transaction

from rest_framework import serializers

from auth.utils.validator import password_validator
from user.api.v1.serializers import UserSerializer
from user.models import User

logger = logging.getLogger(__name__)


class RegisterUserSerializer(UserSerializer):
    """Registration Serializer for User model with email login."""

    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        max_length=255,
        style={"input_type": "password"},
        validators=[password_validator],
        error_messages={
            "blank": "This field is required",
        },
    )

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ["password"]
        read_only_fields = ["is_superuser", "is_staff", "id"]

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create a new user with email login."""
        password = validated_data.pop("password")
        validated_data["tenant"] = self.context.get("tenant")

        # Set username automatically (since it's still required by AbstractUser)
        email = validated_data["email"]
        if "username" not in validated_data or not validated_data["username"]:
            validated_data["username"] = email.split("@")[0]

        with transaction.atomic():
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom login serializer that uses email for authentication."""

    # Override fields for clarity
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict:
        """Validate and return token pair + user data."""
        # Map `email` → `username` because SimpleJWT expects USERNAME_FIELD
        tenant = self.context.get("tenant")
        attrs["username"] = attrs.get("email")

        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data

        # Enforce that the user belongs to this tenant
        if self.user.tenant != tenant:
            raise serializers.ValidationError(
                {"detail": "User does not belong to this tenant."}
            )

        # Optionally update last login timestamp
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class CustomCookieTokenRefreshSerializer(CookieTokenRefreshSerializer):
    """Custom refresh token serializer."""

    is_http_cookie_only = serializers.BooleanField(required=False)
