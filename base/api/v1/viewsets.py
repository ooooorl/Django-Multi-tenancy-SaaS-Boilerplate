from rest_framework import filters
from rest_framework.viewsets import GenericViewSet


class BaseViewset(GenericViewSet):
    """
    Abstract viewsets for all views.
    """

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
