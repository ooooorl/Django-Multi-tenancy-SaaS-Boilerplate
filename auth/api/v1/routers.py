from django.urls import path

from auth.api.v1.viewsets import LoginView, LogoutView, RegisterView, TokenRefreshView

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="login-user"),
    path("auth/logout", LogoutView.as_view(), name="logout-user"),
    path("auth/register", RegisterView.as_view(), name="register-user"),
    path("auth/refresh/token", TokenRefreshView.as_view(), name="refresh-token"),
]
