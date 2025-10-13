from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from kyc_api_gateway.models import VendorManagement, ClientManagement
from kyc_api_gateway.models import UatPanDetails

from kyc_api_gateway.models.uat_pan_request_log import UatPanRequestLog
from kyc_api_gateway.models.kyc_client_services_management import KycClientServicesManagement
from kyc_api_gateway.serializers.uat_pan_details_serializer import UatPanDetailsSerializer
from kyc_api_gateway.services.uat.pan_handler import call_vendor_api, save_pan_data, normalize_vendor_response


class PanUatDetailsAPIView(APIView):
    authentication_classes = []  
    permission_classes = []   

    def post(self, request):
        client = self._authenticate_client(request, env="uat")
        if isinstance(client, Response):
            return client

        services = self._get_client_services(client, env="uat")
        if isinstance(services, Response):
            return services

        service = next((s for s in services if s["name"].upper() == "PAN"), None)
        if not service:
            return Response({
                "success": False,
                "status": 403,
                "error": "PAN service not assigned to this client"
            }, status=403)

        return self._fetch_pan(request, env="uat", client=client, service=service)

    def _authenticate_client(self, request, env):
        key_header = request.headers.get("X-API-KEY")
        if not key_header:
            return Response({
                "success": False,
                "status": 401,
                "error": "Missing API key"
            }, status=401)

        if env == "uat":
            client = ClientManagement.objects.filter(
                uat_key=key_header, deleted_at__isnull=True
            ).first()
        else:
            client = ClientManagement.objects.filter(
                prod_key=key_header, deleted_at__isnull=True
            ).first()

        if not client:
            return Response({
                "success": False,
                "status": 401,
                "error": "Invalid API key"
            }, status=401)

        return client

    def _get_client_services(self, client, env):
        client_services = KycClientServicesManagement.objects.filter(
            client=client, status=True, deleted_at__isnull=True
        ).select_related("myservice")

        if not client_services.exists():
            return Response({
                "success": False,
                "status": 403,
                "error": "No active services assigned to this client"
            }, status=403)

        allowed_services = []

        for cs in client_services:
            service = cs.myservice
            url = service.uat_url if env == "uat" else service.prod_url
            if not url:
                return Response({
                    "success": False,
                    "status": 403,
                    "error": f"{env.upper()} URL not configured for {service.name}"
                }, status=403)

            allowed_services.append({
                "id": service.id,
                "name": service.name,
                "url": url
            })

        return allowed_services

    def _log_request(self, pan_number, vendor, endpoint, status_code, status,
                     request_payload=None, response_payload=None, error_message=None,
                     user=None, pan_details=None):
        UatPanRequestLog.objects.create(
            pan_number=pan_number,
            pan_details=pan_details,
            vendor=vendor,
            endpoint=endpoint,
            status_code=status_code,
            status=status,
            request_payload=request_payload,
            response_payload=response_payload,
            error_message=error_message,
            user=user
        )

    def _fetch_pan(self, request, env, client, service):
        pan_number = request.data.get("pan")
        endpoint = request.path
        user = request.user if request.user.is_authenticated else None

        if not pan_number:
            self._log_request(
                pan_number, vendor=service["name"], endpoint=endpoint,
                status_code=400, status="fail",
                request_payload=request.data,
                error_message="PAN number is required", user=user
            )
            return Response({
                "success": False,
                "status": 400,
                "error": "PAN number is required",
                "data": None
            }, status=400)

        pan_number = pan_number.upper().strip()
        seven_days_ago = timezone.now() - timedelta(days=7)

        cached = UatPanDetails.objects.filter(
            pan_number=pan_number,
            created_at__gte=seven_days_ago,
            deleted_at__isnull=True
        ).order_by('-created_at').first()

        if cached:
            serializer = UatPanDetailsSerializer(cached)
            self._log_request(
                pan_number, vendor="cached", endpoint=endpoint,
                status_code=200, status="success",
                request_payload=request.data,
                response_payload=serializer.data,
                user=user,
                pan_details=cached
            )
            return Response({
                "success": True,
                "status": 200,
                "message": "Data retrieved successfully (cached)",
                "error": None,
                "data": serializer.data
            }, status=200)

        vendors = VendorManagement.objects.filter(status="Active", deleted_at__isnull=True).order_by("priority")

        for vendor in vendors:
            try:
                response = call_vendor_api(vendor, pan_number, service=service, env=env)
                if not response:
                    self._log_request(
                        pan_number, vendor.vendor_name, endpoint,
                        status_code=502, status="fail",
                        request_payload=request.data,
                        error_message="No response from vendor",
                        user=user
                    )
                    continue

                data = response.json()
                status_code = data.get("statusCode")
                status_message = data.get("statusMessage")

                if status_code and status_code != 101:
                    self._log_request(
                        pan_number, vendor.vendor_name, endpoint,
                        status_code=400, status="fail",
                        request_payload=request.data,
                        response_payload=data,
                        error_message=status_message,
                        user=user
                    )
                    return Response({
                        "success": False,
                        "status": 400,
                        "error": f"Vendor {vendor.vendor_name} error: {status_message}",
                        "data": None
                    }, status=400)

                normalized = normalize_vendor_response(vendor.vendor_name, data)
                if normalized and normalized.get("pan_number"):
                    pan_obj = save_pan_data(normalized, client.id)
                    serializer = UatPanDetailsSerializer(pan_obj)
                    self._log_request(
                        pan_number, vendor.vendor_name, endpoint,
                        status_code=200, status="success",
                        request_payload=request.data,
                        response_payload=serializer.data,
                        user=user,
                        pan_details=pan_obj
                    )
                    return Response({
                        "success": True,
                        "status": 200,
                        "message": f"Data retrieved from {vendor.vendor_name}",
                        "error": None,
                        "data": serializer.data
                    }, status=200)

            except Exception as e:
                self._log_request(
                    pan_number, vendor.vendor_name, endpoint,
                    status_code=500, status="fail",
                    request_payload=request.data,
                    error_message=str(e),
                    user=user
                )
                return Response({
                    "success": False,
                    "status": 500,
                    "error": f"Failed processing vendor {vendor.vendor_name} response: {e}",
                    "data": None
                }, status=500)

        self._log_request(
            pan_number, vendor=None, endpoint=endpoint,
            status_code=404, status="fail",
            request_payload=request.data,
            error_message="Unable to fetch PAN details from any vendor",
            user=user
        )
        return Response({
            "success": False,
            "status": 404,
            "error": "Unable to fetch PAN details from any vendor",
            "data": None
        }, status=404)
