from rest_framework import serializers
from kyc_api_gateway.models.role_management import RoleManagement

class RoleManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleManagement
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
