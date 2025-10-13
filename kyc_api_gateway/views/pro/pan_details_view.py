from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from kyc_api_gateway.models import PanDetails, VendorManagement
from kyc_api_gateway.serializers.uat_pan_details_serializer import PanDetailsSerializer
from kyc_api_gateway.services.uat.pan_handler import call_vendor_api, save_pan_data, normalize_vendor_response

class PanProductionDetailsAPIView(APIView):

    def post(self, request):
        return self._fetch_pan(request, env="production")

    def _fetch_pan(self, request, env):
        pan_number = request.data.get("pan")
        if not pan_number:
            return Response(
                    {
                        "success": False,
                        "status": 400,
                        "error": "PAN number is required", "data": None
                    },
                    status=400,
                )

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
                    {
                        "success": True,
                        "status": 200,
                        "error": None,
                        "data": serializer.data,
                        "message": "Data from cache"
                    },
                    status=200,
                )

        vendors = VendorManagement.objects.filter(
            status="Active", deleted_at__isnull=True
        ).order_by("priority")

        user_id = request.user.id if request.user.is_authenticated else 0

        for vendor in vendors:
            response = call_vendor_api(vendor, pan_number, env=env)

            if not response:
                continue

            if response.status_code != 200:
                return Response(
                    {
                        "success": False,
                        "status": response.status_code,
                        "error": f"Vendor {vendor.vendor_name} HTTP error: {response.status_code}",
                        "data": None,
                    },
                    status=response.status_code,
                )

            try:
                data = response.json()

                status_code = data.get("statusCode")
                status_message = data.get("statusMessage")
                if status_code and status_code != 101: 
                    return Response(
                        {
                            "success": False,
                            "status": 400,
                            "error": f"Vendor {vendor.vendor_name} error: {status_message}",
                            "data": None,
                        },
                        status=400,
                    )

                normalized = normalize_vendor_response(vendor.vendor_name, data)
                if normalized and normalized.get("pan_number"):
                    pan_obj = save_pan_data(normalized, user_id)
                    serializer = PanDetailsSerializer(pan_obj)
                    return Response(
                        {
                            "success": True,
                            "status": 200,
                            "error": None,
                            "data": serializer.data,
                        },
                        status=200,
                    )

            except ValueError as ve:
                return Response(
                    {
                        "success": False,
                        "status": 500,
                        "error": f"Invalid response from vendor {vendor.vendor_name}: {ve}",
                        "data": None,
                    },
                    status=500,
                )
            except Exception as e:
                return Response(
                    {
                        "success": False,
                        "status": 500,
                        "error": f"Failed processing vendor {vendor.vendor_name} response: {e}",
                        "data": None,
                    },
                    status=500,
                )

        return Response(
            {
                "success": False,
                "status": 404,
                "error": "Unable to fetch PAN details from any vendor",
                "data": None,
            },
            status=404,
        )
