from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    """
    Abstract serializer for all serializers that needs an action for Model.
    """

    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)
