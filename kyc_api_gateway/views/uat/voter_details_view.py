from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from kyc_api_gateway.models import VendorManagement, ClientManagement, UatVoterDetail
from kyc_api_gateway.models.uat_voter_request_log import UatVoterRequestLog
from kyc_api_gateway.models.kyc_client_services_management import KycClientServicesManagement
from kyc_api_gateway.serializers.uat_voter_details_serializer import UatVoterDetailSerializer
from kyc_api_gateway.services.uat.voter_handler import call_voter_vendor_api, normalize_voter_response, save_voter_data


class VoterUatAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        client = self._authenticate_client(request, env="uat")
        if isinstance(client, Response):
            return client

        services = self._get_client_services(client, env="uat")
        if isinstance(services, Response):
            return services

        service = next((s for s in services if s["name"].upper() == "VOTER"), None)
        if not service:
            return Response({"success": False, "status": 403, "error": "Voter service not assigned"}, status=403)

        return self._fetch_voter(request, env="uat", client=client, service=service)

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

    def _log_request(self, voter_id, vendor, endpoint, status_code, status,
                     request_payload=None, response_payload=None, error_message=None,
                     user=None, voter_obj=None):
        UatVoterRequestLog.objects.create(
            voter_detail=voter_obj,
            vendor=vendor,
            endpoint=endpoint,
            status_code=status_code,
            status=status,
            request_payload=request_payload,
            response_payload=response_payload,
            error_message=error_message,
            user=user
        )


    def _fetch_voter(self, request, env, client, service):
        voter_id = request.data.get("id_number")
        endpoint = request.path
        user = request.user if request.user.is_authenticated else None
        
        if not voter_id:
            self._log_request(None, service["name"], endpoint, 400, "fail", request.data, None, "Voter ID missing", user)
            return Response({"success": False, "status": 400, "error": "Voter ID required"}, status=400)

        seven_days_ago = timezone.now() - timedelta(days=7)
        cached = UatVoterDetail.objects.filter(voter_id=voter_id, created_at__gte=seven_days_ago).first()
        if cached:
            serializer = UatVoterDetailSerializer(cached)
            self._log_request(voter_id, "cached", endpoint, 200, "success", request.data, serializer.data, None, user, cached)
            return Response({"success": True, "status": 200, "message": "Cached data", "data": serializer.data})

        vendors = VendorManagement.objects.filter(status="Active", deleted_at__isnull=True).order_by("priority")

        for vendor in vendors:
            try:
                response_data = call_voter_vendor_api(vendor, request.data, env)

                if not response_data:
                    self._log_request(voter_id, vendor.vendor_name, endpoint, 502, "fail", request.data, None, "No valid response", user)
                    continue

                normalized = normalize_voter_response(vendor.vendor_name, response_data)

                if normalized:
                    voter_obj = save_voter_data(normalized, client.id)
                    serializer = UatVoterDetailSerializer(voter_obj)
                    self._log_request(voter_id, vendor.vendor_name, endpoint, 200, "success", request.data, serializer.data, None, user, voter_obj)
                    return Response({"success": True, "status": 200, "message": f"Data from {vendor.vendor_name}", "data": serializer.data})

            except Exception as e:
                self._log_request(voter_id, vendor.vendor_name, endpoint, 500, "fail", request.data, None, str(e), user)
                continue

        self._log_request(voter_id, None, endpoint, 404, "fail", request.data, None, "All vendors failed", user)
        return Response({"success": False, "status": 404, "error": "All vendors failed"}, status=404)
