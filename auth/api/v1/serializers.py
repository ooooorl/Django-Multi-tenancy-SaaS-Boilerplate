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


class RegisterUserSerializer(UserSerializer):
    """Registration Serializer."""

    password = serializers.CharField(
        min_length=8,
        required=True,
        write_only=True,
        max_length=255,
        style={"input_type": "password"},
        validators=[password_validator],
        error_messages={
            "blank": "This field is required",
        },
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            "password",
        ]

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Override the create method to make use of the custom create_user method.
        """
        username = validated_data.pop("username").strip()

        with transaction.atomic():
            user = User.objects.create_user(username=username, **validated_data)
            return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom Login Serializer."""

    def validate(self, attrs: Dict[str, Any]) -> Dict:
        """validate the given credentials."""

        if "username" in attrs:
            attrs["username"] = attrs["username"].lower()

        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data

        # Update the last timestamp of the user
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user=self.user)

        return data


class CustomCookieTokenRefreshSerializer(CookieTokenRefreshSerializer):
    """Custom refresh token serializer."""

    is_http_cookie_only = serializers.BooleanField(required=False)
