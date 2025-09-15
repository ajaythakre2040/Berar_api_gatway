from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from kyc_api_gateway.models.user_menagement import UserManagement
from kyc_api_gateway.serializers.user_menagement_serializer import UserManagementSerializer
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid


class UserManagementListCreate(APIView):
    permission_classes = [IsAuthenticated,IsTokenValid]

    def get(self, request):
        users = UserManagement.objects.filter(deleted_at__isnull=True)
        serializer = UserManagementSerializer(users, many=True)
        return Response(
            {
                "success": True,
                "message": "User list retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # create new user
    def post(self, request):
        email = request.data.get("email")
        phone = request.data.get("phone")
        username = request.data.get("username")

        # Duplicate check
        if UserManagement.objects.filter(email=email, deleted_at__isnull=True).exists():
            return Response(
                {
                    "success": False,
                    "message": "User with this email already exists.",
                    "errors": {"email": ["Duplicate email not allowed."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if UserManagement.objects.filter(phone=phone, deleted_at__isnull=True).exists():
            return Response(
                {
                    "success": False,
                    "message": "User with this phone already exists.",
                    "errors": {"phone": ["Duplicate phone not allowed."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if UserManagement.objects.filter(username=username, deleted_at__isnull=True).exists():
            return Response(
                {
                    "success": False,
                    "message": "User with this username already exists.",
                    "errors": {"username": ["Duplicate username not allowed."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id, created_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "User created successfully.",
                    # "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to create user.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserManagementDetail(APIView):
    permission_classes = [IsAuthenticated,IsTokenValid]

    # get user by id
    def get(self, request, pk):
        user = get_object_or_404(UserManagement, pk=pk, deleted_at__isnull=True)
        serializer = UserManagementSerializer(user)
        return Response(
            {
                "success": True,
                "message": "User retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # update user by id
    def patch(self, request, pk):
        user = get_object_or_404(UserManagement, pk=pk, deleted_at__isnull=True)

        email = request.data.get("email")
        phone = request.data.get("phone")
        username = request.data.get("username")

        # Duplicate check (excluding current ID)
        if email and UserManagement.objects.filter(email=email, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {
                    "success": False,
                    "message": "User with this email already exists.",
                    "errors": {"email": ["Duplicate email not allowed."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if phone and UserManagement.objects.filter(phone=phone, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {
                    "success": False,
                    "message": "User with this phone already exists.",
                    "errors": {"phone": ["Duplicate phone not allowed."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if username and UserManagement.objects.filter(username=username, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {
                    "success": False,
                    "message": "User with this username already exists.",
                    "errors": {"username": ["Duplicate username not allowed."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserManagementSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "User updated successfully.",
                    # "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update user.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # soft delete user by id
    def delete(self, request, pk):
        user = get_object_or_404(UserManagement, pk=pk, deleted_at__isnull=True)
        user.deleted_at = timezone.now()
        user.deleted_by = request.user.id
        user.save()
        return Response(
            {
                "success": True,
                "message": "User deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
