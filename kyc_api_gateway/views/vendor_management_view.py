from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from kyc_api_gateway.models.vendor_management import VendorManagement
from kyc_api_gateway.serializers.vendor_management_serializer import VendorManagementSerializer
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from auth_system.utils.pagination import CustomPagination
from django.db.models import Q


class VendorManagementListCreate(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.GET.get("search", "").strip()
        vendors = VendorManagement.objects.filter(deleted_at__isnull=True)

        if search_query:
            vendors = vendors.filter(
                Q(display_name__icontains=search_query) |
                Q(internal_name__icontains=search_query) |
                Q(base_url__icontains=search_query) |
                Q(contact_email__icontains=search_query) |
                Q(api_key__icontains=search_query)
            )

        vendors = vendors.order_by("id")

        paginator = CustomPagination()
        page = paginator.paginate_queryset(vendors, request)
        serializer = VendorManagementSerializer(page, many=True)

        total_vendors = vendors.count()

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Vendor list retrieved successfully.",
                "total_vendors": total_vendors,
            },
        )

    def post(self, request):
        serializer = VendorManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id)
            return Response(
                {"success": True, "message": "Vendor created successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "message": "Failed to create vendor.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )    


class VendorManagementDetail(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request, pk):
        vendor = get_object_or_404(VendorManagement, pk=pk, deleted_at__isnull=True)
        serializer = VendorManagementSerializer(vendor)
        return Response(
            {"success": True, "message": "Vendor retrieved successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        vendor = get_object_or_404(VendorManagement, pk=pk, deleted_at__isnull=True)
        serializer = VendorManagementSerializer(vendor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id)
            return Response(
                {"success": True, "message": "Vendor updated successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "message": "Failed to update vendor.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        vendor = get_object_or_404(VendorManagement, pk=pk, deleted_at__isnull=True)
        vendor.deleted_at = timezone.now()
        vendor.deleted_by = request.user.id
        vendor.save()
        return Response(
            {"success": True, "message": "Vendor deleted successfully."},
            status=status.HTTP_200_OK,
        )



class VendorAllCount(APIView):
    permission_classes = [IsTokenValid, IsAuthenticated]

    def get(self, request):
        try:
            total_vendor = VendorManagement.objects.filter(deleted_at__isnull=True).count()

            total_active_vendor = VendorManagement.objects.filter(
                status="Active", deleted_at__isnull=True
            ).count()

            return Response(
                {
                    "success": True,
                    "message": " All Counts retrieved successfully.",
                    "data": {
                        "total_vendor": total_vendor,
                        "total_active_vendor": total_active_vendor,
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
        

        
# class VendorApiList(APIView):
#       permission_classes = [IsAuthenticated, IsTokenValid]

#       def get(self, request):
#         apis = VendorManagement.objects.filter(deleted_at__isnull=True).order_by("id")
#         serializer = VendorManagementSerializer(apis, many=True)
#         return Response(
#             {
#                 "success": True,
#                 "message": "Vendor list retrieved successfully.",
#                 "data": serializer.data,
#             },
#             status=status.HTTP_200_OK,
#         )

class VendorApiList(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        apis = VendorManagement.objects.filter(deleted_at__isnull=True).order_by("id").values("id", "vendor_name")
        return Response(
            {
                "success": True,
                "message": "API list retrieved successfully.",
                "data": list(apis),
            },
            status=status.HTTP_200_OK,
        )
