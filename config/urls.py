from django.contrib import admin
from django.urls import include, path


API_PREFIX = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(API_PREFIX, include("auth.api.v1.routers")),
]
