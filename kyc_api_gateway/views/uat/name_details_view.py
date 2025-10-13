from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from kyc_api_gateway.models import (
    VendorManagement,
    ClientManagement,
    KycClientServicesManagement,
    UatNameMatch,
    UatNameMatchRequestLog
)
from kyc_api_gateway.serializers.uat_name_match_serializer import UatNameMatchSerializer
from kyc_api_gateway.services.uat.name_handler import (
    call_name_vendor_api,
    normalize_name_response,
    save_name_match
)

class NameMatchUatAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        client = self._authenticate_client(request, env="uat")
        if isinstance(client, Response):
            return client

        services = self._get_client_services(client, env="uat")
        if isinstance(services, Response):
            return services

        service = next((s for s in services if s["name"].upper() == "NAME"), None)
        if not service:
            return Response({"success": False, "status": 403, "error": "Name Match service not assigned"}, status=403)

        return self._fetch_name_match(request, env="uat", client=client, service=service)


    def _authenticate_client(self, request, env):
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

    def _get_client_services(self, client, env):
        client_services = KycClientServicesManagement.objects.filter(
            client=client, status=True, deleted_at__isnull=True
        ).select_related("myservice")

        if not client_services.exists():
            return Response({"success": False, "status": 403, "error": "No active services assigned"}, status=403)

        allowed = []
        for cs in client_services:
            s = cs.myservice
            url = s.uat_url if env == "uat" else s.prod_url
            allowed.append({"id": s.id, "name": s.name, "url": url})
        return allowed

    def _log_name_request(self, name1, name2, vendor, endpoint, status_code, status,
                          request_payload=None, response_payload=None, error_message=None,
                          user=None, match_obj=None):
        UatNameMatchRequestLog.objects.create(
            name_1=name1,
            name_2=name2,
            vendor=vendor,
            endpoint=endpoint,
            status_code=status_code,
            status=status,
            request_payload=request_payload,
            response_payload=response_payload,
            error_message=error_message,
            user=user if user and user.is_authenticated else None,
            name_match=match_obj
        )

    def _fetch_name_match(self, request, env, client, service):
        name1 = request.data.get("name_1")
        name2 = request.data.get("name_2")

        if not name1 or not name2:
            return Response(
                {"success": False, "status": 400, "error": "Both name_1 and name_2 are required"},
                status=400
            )

        user = request.user if request.user.is_authenticated else None
        endpoint = request.path

        seven_days_ago = timezone.now() - timedelta(days=7)
        cached = UatNameMatch.objects.filter(
            name_1=name1, name_2=name2, created_at__gte=seven_days_ago
        ).first()

        if cached:
            serializer = UatNameMatchSerializer(cached)
            self._log_name_request(name1, name2, "cached", endpoint, 200, "success",
                                   request_payload=request.data, response_payload=serializer.data,
                                   user=user, match_obj=cached)
            return Response({
                "success": True,
                "status": 200,
                "message": "Cached data",
                "data": serializer.data
            })

        vendors = VendorManagement.objects.filter(status="Active", deleted_at__isnull=True).order_by("priority")

        for vendor in vendors:
            try:
                response = call_name_vendor_api(vendor, request.data, env)
                if not response:
                    self._log_name_request(name1, name2, vendor.vendor_name, endpoint,
                                           502, "fail", request_payload=request.data,
                                           error_message="No response", user=user)
                    continue

                data = response.json()
                normalized = normalize_name_response(vendor.vendor_name, data, request_data=request.data)

                if normalized:
                    obj = save_name_match(normalized, client.id)
                    serializer = UatNameMatchSerializer(obj)
                    self._log_name_request(name1, name2, vendor.vendor_name, endpoint,
                                           response.status_code, "success",
                                           request_payload=request.data,
                                           response_payload=serializer.data,
                                           user=user, match_obj=obj)
                    return Response({
                        "success": True,
                        "status": 200,
                        "message": f"Data from {vendor.vendor_name}",
                        "data": serializer.data
                    })

            except Exception as e:
                self._log_name_request(name1, name2, vendor.vendor_name, endpoint,
                                       500, "fail", request_payload=request.data,
                                       error_message=str(e), user=user)
                continue 

        self._log_name_request(name1, name2, None, endpoint, 404, "fail",
                               request_payload=request.data, error_message="All vendors failed", user=user)
        return Response({"success": False, "status": 404, "error": "All vendors failed"}, status=404)
