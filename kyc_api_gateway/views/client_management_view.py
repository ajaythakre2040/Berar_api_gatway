from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from kyc_api_gateway.models.client_management import ClientManagement
from kyc_api_gateway.serializers.client_management_serializer import ClientManagementSerializer
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from kyc_api_gateway.models.api_management import ApiManagement
from auth_system.utils.pagination import CustomPagination
from django.db.models import Q


class ClientManagementListCreate(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.GET.get("search", "").strip()
        clients = ClientManagement.objects.filter(deleted_at__isnull=True)

        # search filter
        if search_query:
            clients = clients.filter(
                Q(company_name__icontains=search_query) |
                Q(registration_number__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )

        clients = clients.order_by("id")

        paginator = CustomPagination()
        page = paginator.paginate_queryset(clients, request)
        serializer = ClientManagementSerializer(page, many=True)

        total_clients = clients.count()

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Client list retrieved successfully.",
                "total_clients": total_clients,
            },
        )

    def post(self, request):
        serializer = ClientManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id)
            return Response(
                {
                    "success": True,
                    "message": "Client created successfully.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to create client.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    

class ClientManagementDetail(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request, pk):
        client = get_object_or_404(ClientManagement, pk=pk, deleted_at__isnull=True)
        serializer = ClientManagementSerializer(client)
        return Response(
            {"success": True, "message": "Client retrieved successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        client = get_object_or_404(ClientManagement, pk=pk, deleted_at__isnull=True)
        serializer = ClientManagementSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id)
            return Response(
                {"success": True, "message": "Client updated successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "message": "Failed to update client.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        client = get_object_or_404(ClientManagement, pk=pk, deleted_at__isnull=True)
        client.deleted_at = timezone.now()
        client.deleted_by = request.user.id
        client.save()
        return Response(
            {"success": True, "message": "Client deleted successfully."},
            status=status.HTTP_200_OK,
        )


class ClientAllCount(APIView):
    permission_classes = [IsTokenValid, IsAuthenticated]

    def get(self, request):
        try:
            total_client = ClientManagement.objects.filter(deleted_at__isnull=True).count()

            total_active_client = ClientManagement.objects.filter(
                account_status="Active", deleted_at__isnull=True
            ).count()

            total_api = ApiManagement.objects.filter(deleted_at__isnull=True).count()

            return Response(
                {
                    "success": True,
                    "message": " All Counts retrieved successfully.",
                    "data": {
                        "total_client": total_client,
                        "total_active_client": total_active_client,
                        "total_api": total_api,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Failed to fetch counts.",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
