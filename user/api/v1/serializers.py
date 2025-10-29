from base.api.v1.serializers import BaseSerializer
from user.models import User


class UserSerializer(BaseSerializer):
    """
    Serializer for User model.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
        }
