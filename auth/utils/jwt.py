from typing import Dict

from dj_rest_auth.app_settings import api_settings as rest_auth_settings
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from django.utils import timezone

from rest_framework.response import Response


def set_all_jwt_cookies(
    response: Response,
    access_token: AccessToken,
    refresh_token: RefreshToken,
) -> Response:
    """
    Set all JWT token into HttpOnly cookies.
    """

    cookie_secure: bool = rest_auth_settings.JWT_AUTH_SECURE
    cookie_samesite: str = rest_auth_settings.JWT_AUTH_SAMESITE
    access_token_expiration = timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME
    refresh_token_expiration = timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME
    refresh_token_path = rest_auth_settings.JWT_AUTH_REFRESH_COOKIE_PATH

    # Set the access token in the cookie
    cookie_name = rest_auth_settings.JWT_AUTH_COOKIE
    refresh_cookie_name = rest_auth_settings.JWT_AUTH_REFRESH_COOKIE
    cookie_httponly = rest_auth_settings.JWT_AUTH_HTTPONLY

    response.set_cookie(
        cookie_name,
        access_token,
        expires=access_token_expiration,
        httponly=cookie_httponly,
        secure=cookie_secure,
        samesite=cookie_samesite,
    )

    response.set_cookie(
        refresh_cookie_name,
        refresh_token,
        expires=refresh_token_expiration,
        secure=cookie_secure,
        httponly=cookie_httponly,
        samesite=cookie_samesite,
        path=refresh_token_path,
    )

    return response


def set_cookies(
    response: Response,
    access_token: AccessToken,
    refresh_token: RefreshToken,
    is_http_cookie_only: bool,
) -> Response:
    """
    Set JWT tokens into HttpOnly cookies
    and we'll add and remove some attributes from the response.
    """

    if is_http_cookie_only:
        set_all_jwt_cookies(
            response=response,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        # Update and remove some attributes from the response
        _remove_sensitive_data(response)
        _update_expiration_info(response)

    return response


def _update_expiration_info(response: Response) -> Dict:
    """
    Update the expiration info in the response.
    """
    response.data.update(
        {
            "access_expiration": timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME,
            "refresh_expiration": timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME,
        }
    )


def _remove_sensitive_data(response: Response) -> None:
    """
    Remove the sensitive data from the response.
    """
    for token_key in ["access", "refresh"]:
        response.data.pop(token_key, None)


def logout_and_revoke_tokens(
    response: Response,
    refresh_token: RefreshToken,
    is_http_cookie_only: bool,
) -> Response:
    """
    Manually revoke JWT refresh tokens by blacklisting them.
    """
    token = RefreshToken(refresh_token)
    token.blacklist()

    force_token_expiration = timezone.now() - jwt_settings.REFRESH_TOKEN_LIFETIME
    refresh_cookie_path = rest_auth_settings.JWT_AUTH_REFRESH_COOKIE_PATH
    cookie_secure: bool = rest_auth_settings.JWT_AUTH_SECURE
    cookie_httponly = rest_auth_settings.JWT_AUTH_HTTPONLY
    cookie_samesite = rest_auth_settings.JWT_AUTH_SAMESITE

    if is_http_cookie_only:
        cookie_name = rest_auth_settings.JWT_AUTH_COOKIE
        refresh_cookie_name = rest_auth_settings.JWT_AUTH_REFRESH_COOKIE

        response.set_cookie(
            key=cookie_name,
            value="",  # Clear cookie value
            expires=force_token_expiration,
            httponly=cookie_httponly,
            secure=cookie_secure,
            samesite=cookie_samesite,
        )

        response.set_cookie(
            key=refresh_cookie_name,
            value="",  # Clear cookie value
            expires=force_token_expiration,
            httponly=cookie_httponly,
            secure=cookie_secure,
            samesite=cookie_samesite,
            path=refresh_cookie_path,
        )

    return response


def refresh_and_set_jwt_cookies(
    response: Response,
    access_token: AccessToken,
    refresh_token: RefreshToken,
    is_http_cookie_only: bool,
) -> Response:
    """
    Refresh the JWT token and set the new token into Http.
    """

    response = set_cookies(
        response=response,
        access_token=access_token,
        refresh_token=refresh_token,
        is_http_cookie_only=is_http_cookie_only,
    )

    return response
