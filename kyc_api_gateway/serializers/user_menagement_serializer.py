from rest_framework import serializers
from kyc_api_gateway.models.user_menagement import UserManagement


class UserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserManagement
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
