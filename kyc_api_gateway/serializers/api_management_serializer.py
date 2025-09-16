from rest_framework import serializers
from kyc_api_gateway.models.api_management import ApiManagement
from kyc_api_gateway.models.vendor_management import VendorManagement

class VendorManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorManagement
        exclude = (
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )

class ApiManagementSerializer(serializers.ModelSerializer):
    supported_vendors = VendorManagementSerializer(many=True, read_only=True)
    default_vendor = VendorManagementSerializer(read_only=True)

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
