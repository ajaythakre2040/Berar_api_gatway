from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.exceptions import NotFound

from auth_system.models.user import TblUser
from auth_system.permissions.token_valid import IsTokenValid
from auth_system.serializers.user import TblUserSerializer
from django.db.models import Q

from auth_system.utils.pagination import CustomPagination

from auth_system.models.department import Department
from auth_system.models.role_permission import RolePermission
from rest_framework.views import APIView


class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTokenValid]
    serializer_class = TblUserSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        try:
            search_query = request.GET.get("search", "").strip()
            queryset = TblUser.objects.filter(deleted_at__isnull=True)

            if search_query:
                queryset = queryset.filter(
                    Q(full_name__icontains=search_query)
                    | Q(email__icontains=search_query)
                    | Q(mobile_number__icontains=search_query)
                )

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "success": True,
                    "message": "User list fetched successfully.",
                    "status_code": status.HTTP_200_OK,
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Error fetching user list: {str(e)}",
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(created_by=request.user.id)
            return Response(
                {
                    "success": True,
                    "message": "User created successfully.",
                    "status_code": status.HTTP_201_CREATED,
                    "data": TblUserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "User creation failed.",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TblUser.objects.filter(deleted_at__isnull=True)
    serializer_class = TblUserSerializer
    lookup_field = "id"

    def get_object(self):
        try:
            return TblUser.objects.get(id=self.kwargs["id"], deleted_at__isnull=True)
        except TblUser.DoesNotExist:
            raise NotFound(detail="User not found.", code=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "success": True,
                "message": "User details fetched successfully.",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance.updated_by = request.user.id
            instance.updated_at = timezone.now()
            self.perform_update(serializer)
            return Response(
                {
                    "success": True,
                    "message": "User updated successfully.",
                    "status_code": status.HTTP_200_OK,
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.deleted_by = request.user.id
        instance.save()
        return Response(
            {
                "success": True,
                "message": "User deleted successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )

