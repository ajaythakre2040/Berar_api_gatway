from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from kyc_api_gateway.models import PanDetails, VendorManagement
from kyc_api_gateway.serializers.pan_details_serializer import PanDetailsSerializer
from kyc_api_gateway.services.pan_handler import call_vendor_api, save_pan_data


class PanDetailsAPIView(APIView):
    def get(self, request):
        pan_number = request.GET.get("pan")
        if not pan_number:
            return Response({"error": "PAN number is required"}, status=400)

        pan_number = pan_number.upper().strip()
        seven_days_ago = timezone.now() - timedelta(days=7)

        cached = PanDetails.objects.filter(
            pan_number=pan_number,
            created_at__gte=seven_days_ago,
            deleted_at__isnull=True,
        ).first()

        if cached:
            serializer = PanDetailsSerializer(cached)
            return Response(
                {"message": "Data from cache", "data": serializer.data}, status=200
            )

        vendors = VendorManagement.objects.filter(
            status="Active", deleted_at__isnull=True
        ).order_by("priority")

        for vendor in vendors:
            response = call_vendor_api(vendor, pan_number)
            if response:
                try:
                    data = response.json()
                    result = data.get("result") or data.get("data")
                    if result and (result.get("pan") or result.get("pan_number")):
                        created_by = (
                            request.user.id if request.user.is_authenticated else 0
                        )
                        pan_obj = save_pan_data(data, pan_number, created_by, vendor)
                        serializer = PanDetailsSerializer(pan_obj)
                        return Response(
                            {
                                "message": f"Fetched from {vendor.vendor_name}",
                                "data": serializer.data,
                            },
                            status=200,
                        )
                except Exception as e:
                    print(f"Error processing response from {vendor.vendor_name}: {e}")

        return Response(
            {"error": "Unable to fetch PAN details from vendors"}, status=502
        )
