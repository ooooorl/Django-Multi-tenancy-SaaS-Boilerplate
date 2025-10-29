from dj_rest_auth.jwt_auth import CookieTokenRefreshSerializer
from rest_framework_simplejwt.tokens import TokenError
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from auth.api.v1.serializers import (
    CustomCookieTokenRefreshSerializer,
    CustomTokenObtainPairSerializer,
    RegisterUserSerializer,
)
from auth.utils.jwt import (
    logout_and_revoke_tokens,
    refresh_and_set_jwt_cookies,
    set_cookies,
)


class RegisterView(GenericAPIView):
    """Registration endpoint"""

    permission_classes = [AllowAny]
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        """Handle registration request."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"user": serializer.data, "message": "User registered successfully."},
            status=status.HTTP_201_CREATED,
        )


class LoginView(GenericAPIView):
    """Login endpoint"""

    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """Handle login request."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_http_cookie_only = request.data.get("is_http_cookie_only", False)

        # Set both access and refresh tokens in cookies
        return set_cookies(
            response=Response(serializer.validated_data),
            access_token=serializer.validated_data["access"],
            refresh_token=serializer.validated_data["refresh"],
            is_http_cookie_only=is_http_cookie_only,
        )


class TokenRefreshView(BaseTokenRefreshView):
    """Custom Token Refresh View to handle JWT token refresh."""

    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        """Set the access token in the cookie."""
        is_http_cookie_only = request.data.get("is_http_cookie_only", False)

        if response.status_code == status.HTTP_200_OK:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            # Set the access and refresh token in the cookie
            try:
                response = refresh_and_set_jwt_cookies(
                    response=response,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    is_http_cookie_only=is_http_cookie_only,
                )

            except Exception as error:
                response = Response(
                    {"detail": f"{error}"}, status=status.HTTP_400_BAD_REQUEST
                )

        return super().finalize_response(request, response, *args, **kwargs)


class LogoutView(GenericAPIView):
    """An endpoint for user to logout."""

    permission_classes = [IsAuthenticated]
    serializer_class = CustomCookieTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        """Handle logout request."""

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            refresh_token = serializer.validated_data.get("refresh")
            is_http_cookie_only = request.data.get("is_http_cookie_only", False)

            # Blacklist the refresh token
            response = logout_and_revoke_tokens(
                response=Response(
                    {"detail": "Successfully logged out"}, status=status.HTTP_200_OK
                ),
                refresh_token=refresh_token,
                is_http_cookie_only=is_http_cookie_only,
            )

            return response

        except TokenError as error:
            return Response({"detail": f"{error}"}, status=status.HTTP_400_BAD_REQUEST)
