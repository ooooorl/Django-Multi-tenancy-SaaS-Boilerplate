import os
from datetime import timedelta

from .base import *  # noqa

ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Uncomment this one when not using with nginx
# DEVELOPMENT = ["whitenoise.middleware.WhiteNoiseMiddleware"]
# MIDDLEWARE += DEVELOPMENT

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=100),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1000),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "TOKEN_OBTAIN_SERIALIZER": "auth.api.v1.serializers.CustomTokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "auth.api.v1.serializers.CustomCookieTokenRefreshSerializer",
}
