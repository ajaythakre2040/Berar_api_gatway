from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from kyc_api_gateway.models.vendor_management import VendorManagement
from kyc_api_gateway.serializers.vendor_management_serializer import VendorManagementSerializer
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid


class VendorManagementListCreate(APIView):
    permission_classes = [IsAuthenticated,IsTokenValid]

    # Get all vendors
    def get(self, request):
        vendors = VendorManagement.objects.filter(deleted_at__isnull=True)
        serializer = VendorManagementSerializer(vendors, many=True)
        return Response(
            {
                "success": True,
                "message": "Vendor list retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # Create new vendor
    def post(self, request):
        display_name = request.data.get("display_name")
        internal_name = request.data.get("internal_name")
        base_url = request.data.get("base_url")
        contact_email = request.data.get("contact_email")
        api_key = request.data.get("api_key")

        # Duplicate checks
        if VendorManagement.objects.filter(display_name=display_name, deleted_at__isnull=True).exists():
            return Response(
                {"success": False, "message": "Display name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if VendorManagement.objects.filter(internal_name=internal_name, deleted_at__isnull=True).exists():
            return Response(
                {"success": False, "message": "Internal name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if VendorManagement.objects.filter(base_url=base_url, deleted_at__isnull=True).exists():
            return Response(
                {"success": False, "message": "Base URL already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if VendorManagement.objects.filter(contact_email=contact_email, deleted_at__isnull=True).exists():
            return Response(
                {"success": False, "message": "Contact email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if VendorManagement.objects.filter(api_key=api_key, deleted_at__isnull=True).exists():
            return Response(
                {"success": False, "message": "API key already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = VendorManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id, created_at=timezone.now())
            return Response(
                {"success": True, "message": "Vendor created successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "message": "Failed to create vendor.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VendorManagementDetail(APIView):
    permission_classes = [IsAuthenticated,IsTokenValid]

    def get(self, request, pk):
        vendor = get_object_or_404(VendorManagement, pk=pk, deleted_at__isnull=True)
        serializer = VendorManagementSerializer(vendor)
        return Response(
            {"success": True, "message": "Vendor retrieved successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    # Update vendor
    def patch(self, request, pk):
        vendor = get_object_or_404(VendorManagement, pk=pk, deleted_at__isnull=True)

        display_name = request.data.get("display_name")
        internal_name = request.data.get("internal_name")
        base_url = request.data.get("base_url")
        contact_email = request.data.get("contact_email")
        api_key = request.data.get("api_key")

        # Duplicate check (excluding self)
        if display_name and VendorManagement.objects.filter(display_name=display_name, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {"success": False, "message": "Display name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if internal_name and VendorManagement.objects.filter(internal_name=internal_name, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {"success": False, "message": "Internal name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if base_url and VendorManagement.objects.filter(base_url=base_url, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {"success": False, "message": "Base URL already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if contact_email and VendorManagement.objects.filter(contact_email=contact_email, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {"success": False, "message": "Contact email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if api_key and VendorManagement.objects.filter(api_key=api_key, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {"success": False, "message": "API key already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = VendorManagementSerializer(vendor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {"success": True, "message": "Vendor updated successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "message": "Failed to update vendor.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Soft delete vendor
    def delete(self, request, pk):
        vendor = get_object_or_404(VendorManagement, pk=pk, deleted_at__isnull=True)
        vendor.deleted_at = timezone.now()
        vendor.deleted_by = request.user.id
        vendor.save()
        return Response(
            {"success": True, "message": "Vendor deleted successfully."},
            status=status.HTTP_200_OK,
        )
