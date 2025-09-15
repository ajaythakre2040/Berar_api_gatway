from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from kyc_api_gateway.models.client_management import ClientManagement
from kyc_api_gateway.serializers.client_management_serializer import ClientManagementSerializer
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid


class ClientManagementListCreate(APIView):
    permission_classes = [IsAuthenticated,IsTokenValid]
    # Get all clients
    def get(self, request):
        clients = ClientManagement.objects.filter(deleted_at__isnull=True)
        serializer = ClientManagementSerializer(clients, many=True)
        return Response(
            {
                "success": True,
                "message": "Client list retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # Create new client
    def post(self, request):
        company_name = request.data.get("company_name")
        registration_number = request.data.get("registration_number")
        email = request.data.get("email")
        phone = request.data.get("phone")

        # Duplicate checks
        if ClientManagement.objects.filter(company_name=company_name, deleted_at__isnull=True).exists():
            return Response(
                {"success": False, "message": "Company name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if ClientManagement.objects.filter(registration_number=registration_number, deleted_at__isnull=True).exists():
            return Response(
                {"success": False, "message": "Registration number already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if ClientManagement.objects.filter(email=email, deleted_at__isnull=True).exists():
            return Response(
                {"success": False, "message": "Email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if ClientManagement.objects.filter(phone=phone, deleted_at__isnull=True).exists():
            return Response(
                {"success": False, "message": "Phone already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ClientManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id, created_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Client created successfully.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "message": "Failed to create client.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ClientManagementDetail(APIView):
    permission_classes = [IsAuthenticated,IsTokenValid]

    def get(self, request, pk):
        client = get_object_or_404(ClientManagement, pk=pk, deleted_at__isnull=True)
        serializer = ClientManagementSerializer(client)
        return Response(
            {"success": True, "message": "Client retrieved successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        client = get_object_or_404(ClientManagement, pk=pk, deleted_at__isnull=True)

        company_name = request.data.get("company_name")
        registration_number = request.data.get("registration_number")
        email = request.data.get("email")
        phone = request.data.get("phone")

        # Duplicate check (excluding self)
        if company_name and ClientManagement.objects.filter(company_name=company_name, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {"success": False, "message": "Company name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if registration_number and ClientManagement.objects.filter(registration_number=registration_number, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {"success": False, "message": "Registration number already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if email and ClientManagement.objects.filter(email=email, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {"success": False, "message": "Email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if phone and ClientManagement.objects.filter(phone=phone, deleted_at__isnull=True).exclude(id=pk).exists():
            return Response(
                {"success": False, "message": "Phone already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ClientManagementSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {"success": True, "message": "Client updated successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "message": "Failed to update client.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Soft delete client
    def delete(self, request, pk):
        client = get_object_or_404(ClientManagement, pk=pk, deleted_at__isnull=True)
        client.deleted_at = timezone.now()
        client.deleted_by = request.user.id
        client.save()
        return Response(
            {"success": True, "message": "Client deleted successfully."},
            status=status.HTTP_200_OK,
        )
