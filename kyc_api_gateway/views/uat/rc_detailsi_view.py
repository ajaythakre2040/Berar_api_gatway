from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from kyc_api_gateway.models import VendorManagement, ClientManagement, UatRcDetails
from kyc_api_gateway.models.uat_rc_request_log import UatRcRequestLog
from kyc_api_gateway.models.kyc_client_services_management import KycClientServicesManagement
from kyc_api_gateway.serializers.uat_rc_detail_serializer import UatRcDetailsSerializer
from kyc_api_gateway.services.uat.rc_handler import call_rc_vendor_api, normalize_rc_response, save_rc_data

class RcUatAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        client = self._authenticate_client(request, env="uat")
        if isinstance(client, Response):
            return client

        services = self._get_client_services(client, env="uat")
        if isinstance(services, Response):
            return services

        service = next((s for s in services if s["name"].upper() == "RC"), None)
        if not service:
            return Response({
                "success": False,
                "status": 403,
                "error": "RC service not assigned"
            }, status=403)

        return self._fetch_rc(request, client, service)

    def _authenticate_client(self, request, env="uat"):
        key_header = request.headers.get("X-API-KEY")
        if not key_header:
            return Response({"success": False, "status": 401, "error": "Missing API key"}, status=401)

        client = ClientManagement.objects.filter(
            uat_key=key_header if env == "uat" else key_header,
            deleted_at__isnull=True
        ).first()

        if not client:
            return Response({"success": False, "status": 401, "error": "Invalid API key"}, status=401)
        return client

    def _get_client_services(self, client, env="uat"):
        client_services = KycClientServicesManagement.objects.filter(
            client=client, status=True, deleted_at__isnull=True
        ).select_related("myservice")

        if not client_services.exists():
            return Response({"success": False, "status": 403, "error": "No active services assigned"}, status=403)

        allowed_services = []
        for cs in client_services:
            s = cs.myservice
            url = s.uat_url if env == "uat" else s.prod_url
            allowed_services.append({"id": s.id, "name": s.name, "url": url})
        return allowed_services

    def _log_request(self, rc_number, vendor, endpoint, status_code, status,
                     request_payload=None, response_payload=None, error_message=None,
                     user=None, rc_details=None):
        UatRcRequestLog.objects.create(
            rc_number=rc_number,
            rc_details=rc_details,
            vendor=vendor,
            endpoint=endpoint,
            status_code=status_code,
            status=status,
            request_payload=request_payload,
            response_payload=response_payload,
            error_message=error_message,
            user=user
        )

    def _fetch_rc(self, request, client, service):
        rc_number = request.data.get("rc_number")
        endpoint = request.path
        user = request.user if request.user.is_authenticated else None

        if not rc_number:
            self._log_request(rc_number, service["name"], endpoint, 400, "fail",
                              request_payload=request.data,
                              error_message="RC number required", user=user)
            return Response({"success": False, "status": 400, "error": "RC number required"}, status=400)

        seven_days_ago = timezone.now() - timedelta(days=7)

        cached = UatRcDetails.objects.filter(rc_number=rc_number, created_at__gte=seven_days_ago).first()
        if cached:
            serializer = UatRcDetailsSerializer(cached)
            self._log_request(rc_number, "cached", endpoint, 200, "success",
                              request_payload=request.data, response_payload=serializer.data,
                              user=user, rc_details=cached)
            return Response({"success": True, "status": 200, "message": "Cached data", "data": serializer.data})

        vendors = VendorManagement.objects.filter(status="Active", deleted_at__isnull=True).order_by("priority")

        for vendor in vendors:
                try:

                    response = call_rc_vendor_api(vendor, request.data)


                    if not response:
                        self._log_request(rc_number, vendor.vendor_name, endpoint, 502, "fail",
                                        request_payload=request.data, error_message="No response", user=user)
                        continue

                    try:
                        data = response 

                    except ValueError:
                        self._log_request(rc_number, vendor.vendor_name, endpoint, 502, "fail",
                                        request_payload=request.data,
                                        error_message=f"Invalid JSON response: {response.text}", user=user)
                        continue

                    normalized = normalize_rc_response(vendor.vendor_name, data)

                    if normalized:
                        rc_obj = save_rc_data(normalized, client.id)
                        serializer = UatRcDetailsSerializer(rc_obj)

                    
                        self._log_request(rc_number, vendor.vendor_name, endpoint, 200, "success",
                                        request_payload=request.data, response_payload=serializer.data,
                                        user=user, rc_details=rc_obj)
                        return Response({"success": True, "status": 200,
                                        "message": f"Data retrieved from {vendor.vendor_name}",
                                        "data": serializer.data})

                except Exception as e:
                    self._log_request(rc_number, vendor.vendor_name, endpoint, 500, "fail",
                                    request_payload=request.data, error_message=str(e), user=user)
                    return Response({"success": False, "status": 500,
                                    "error": f"Failed processing vendor {vendor.vendor_name} response: {e}"}, status=500)

        self._log_request(rc_number, vendor=None, endpoint=endpoint, status_code=404, status="fail",
                            request_payload=request.data, error_message="All vendors failed", user=user)
        return Response({"success": False, "status": 404, "error": "All vendors failed"}, status=404)
