from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid  # assuming you use this

from kyc_api_gateway.models.api_management import ApiManagement
from kyc_api_gateway.models.vendor_management import VendorManagement
from kyc_api_gateway.serializers.api_management_serializer import ApiManagementSerializer


class ApiManagementListCreate(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        apis = ApiManagement.objects.filter(deleted_at__isnull=True)
        serializer = ApiManagementSerializer(apis, many=True)
        return Response(
            {
                "success": True,
                "message": "API list retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        api_name = request.data.get("api_name")

        # Duplicate check
        if ApiManagement.objects.filter(api_name=api_name, deleted_at__isnull=True).exists():
            return Response(
                {
                    "success": False,
                    "message": "API with this name already exists.",
                    "errors": {"api_name": ["Duplicate API name not allowed."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ApiManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id, created_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "API created successfully.",
                    # "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to create API.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ApiManagementDetail(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        return get_object_or_404(ApiManagement, pk=pk, deleted_at__isnull=True)

    def get(self, request, pk):
        api = self.get_object(pk)
        serializer = ApiManagementSerializer(api)
        return Response(
            {
                "success": True,
                "message": "API retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        api = self.get_object(pk)
        api_name = request.data.get("api_name")

        # Duplicate check (excluding current ID)
        if api_name and ApiManagement.objects.filter(api_name=api_name, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {
                    "success": False,
                    "message": "API with this name already exists.",
                    "errors": {"api_name": ["Duplicate API name not allowed."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ApiManagementSerializer(api, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "API updated successfully.",
                    # "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update API.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        api = self.get_object(pk)
        api.deleted_at = timezone.now()
        api.deleted_by = request.user.id
        api.save()
        return Response(
            {
                "success": True,
                "message": "API deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
