from rest_framework import serializers
from kyc_api_gateway.models.api_management import ApiManagement
from kyc_api_gateway.models.vendor_management import VendorManagement


class ApiManagementSerializer(serializers.ModelSerializer):
    supported_vendors = serializers.PrimaryKeyRelatedField(
        queryset=VendorManagement.objects.all(), many=True, required=False
    )

    class Meta:
        model = ApiManagement
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
