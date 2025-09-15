from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.utils import timezone
from kyc_api_gateway.models.role_management import RoleManagement
from kyc_api_gateway.serializers.role_menagement_serializer import RoleManagementSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid




class RoleManagementListCreate(APIView):
    permission_classes = [IsAuthenticated,IsTokenValid]

    def get(self, request):
        roles = RoleManagement.objects.filter(deleted_at__isnull=True)
        serializer = RoleManagementSerializer(roles, many=True)
        return Response(
            {
                "success": True,
                "message": "Role list retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # create new role
    def post(self, request):
        role_name = request.data.get("role_name")
        # Duplicate check
        if RoleManagement.objects.filter(role_name=role_name, deleted_at__isnull=True).exists():
            return Response(
                {
                    "success": False,
                    "message": "Role with this name already exists.",
                    "errors": {"role_name": ["Duplicate role not allowed."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RoleManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id, created_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Role created successfully.",
                    # "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to create role.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class RoleManagementDetail(APIView):
    permission_classes = [IsAuthenticated,IsTokenValid]

    # get role by id
    def get(self, request, pk):
        role = get_object_or_404(RoleManagement, pk=pk, deleted_at__isnull=True)
        serializer = RoleManagementSerializer(role)
        return Response(
            {
                "success": True,
                "message": "Role retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # update role by id
    def patch(self, request, pk):
        role = get_object_or_404(RoleManagement, pk=pk, deleted_at__isnull=True)

        role_name = request.data.get("role_name")
        # Duplicate check (excluding current ID)
        if RoleManagement.objects.filter(role_name=role_name, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {
                    "success": False,
                    "message": "Role with this name already exists.",
                    "errors": {"role_name": ["Duplicate role not allowed."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RoleManagementSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Role updated successfully.",
                    # "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update role.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # soft delete role by id
    def delete(self, request, pk):
        role = get_object_or_404(RoleManagement, pk=pk, deleted_at__isnull=True)
        role.deleted_at = timezone.now()
        role.deleted_by = request.user.id
        role.save()
        return Response(
            {
                "success": True,
                "message": "Role deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
