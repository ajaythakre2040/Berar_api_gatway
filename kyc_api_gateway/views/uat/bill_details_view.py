

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from datetime import timedelta
# from django.utils import timezone
# from kyc_api_gateway.models import UatElectricityBill, VendorManagement, ClientManagement
# from kyc_api_gateway.models.uat_bill_request_log import UatBillRequestLog
# from kyc_api_gateway.models.kyc_client_services_management import KycClientServicesManagement
# from kyc_api_gateway.models.kyc_my_services import KycMyServices
# from kyc_api_gateway.serializers.uat_bill_details_serializer import UatElectricityBillSerializer
# from kyc_api_gateway.services.uat.bill_handler import call_vendor_api, save_bill_data, normalize_vendor_response

# class BillUatDetailsAPIView(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def post(self, request):
#         client = self._authenticate_client(request, env="uat")
#         if isinstance(client, Response):
#             return client

#         services = self._get_client_services(client, env="uat")
#         if isinstance(services, Response):
#             return services

#         service = next((s for s in services if s["name"].upper() == "BILL"), None)
#         if not service:
#             return Response({"success": False, "status": 403, "error": "Bill service not assigned"}, status=403)

#         return self._fetch_bill(request, env="uat", client=client, service=service)

#     def _authenticate_client(self, request, env):
#         key_header = request.headers.get("X-API-KEY")
#         if not key_header:
#             return Response({"success": False, "status": 401, "error": "Missing API key"}, status=401)

#         client = ClientManagement.objects.filter(
#             uat_key=key_header if env == "uat" else key_header,
#             deleted_at__isnull=True
#         ).first()

#         if not client:
#             return Response({"success": False, "status": 401, "error": "Invalid API key"}, status=401)

#         return client

#     def _get_client_services(self, client, env):
#         client_services = KycClientServicesManagement.objects.filter(
#             client=client, status=True, deleted_at__isnull=True
#         ).select_related("myservice")

#         if not client_services.exists():
#             return Response({"success": False, "status": 403, "error": "No active services assigned"}, status=403)

#         allowed = []
#         for cs in client_services:
#             s = cs.myservice
#             url = s.uat_url if env == "uat" else s.prod_url
#             allowed.append({"id": s.id, "name": s.name, "url": url})
#         return allowed

#     def _log_request(self, customer_id, vendor, endpoint, status_code, status,
#                      request_payload=None, response_payload=None, error_message=None,
#                      user=None, bill_details=None):
#         UatBillRequestLog.objects.create(
#             customer_id=customer_id,
#             bill_details=bill_details,
#             vendor=vendor,
#             endpoint=endpoint,
#             status_code=status_code,
#             status=status,
#             request_payload=request_payload,
#             response_payload=response_payload,
#             error_message=error_message,
#             user=user
#         )

#     def _fetch_bill(self, request, env, client, service):
#         customer_id = request.data.get("consumer_id") or request.data.get("id_number")
#         endpoint = request.path
#         user = request.user if request.user.is_authenticated else None

#         if not customer_id:
#             self._log_request(None, service["name"], endpoint, 400, "fail", request.data, None, "Customer ID missing", user)
#             return Response({"success": False, "status": 400, "error": "Customer/Consumer ID required"}, status=400)

#         seven_days_ago = timezone.now() - timedelta(days=7)
#         cached = UatElectricityBill.objects.filter(
#             customer_id=customer_id,
#             created_at__gte=seven_days_ago
#         ).first()

#         if cached:
#             serializer = UatElectricityBillSerializer(cached)
#             self._log_request(customer_id, "cached", endpoint, 200, "success", request.data, serializer.data, None, user, cached)
#             return Response({"success": True, "status": 200, "message": "Cached data", "data": serializer.data})

#         vendors = VendorManagement.objects.filter(status="Active", deleted_at__isnull=True).order_by("priority")

#         for vendor in vendors:
#             try:
#                 response = call_vendor_api(vendor, request.data, env)
#                 if not response:
#                     self._log_request(customer_id, vendor.vendor_name, endpoint, 502, "fail", request.data, None, "No response", user)
#                     continue

#                 data = response.json()
#                 normalized = normalize_vendor_response(vendor.vendor_name, data)
#                 if normalized:
#                     bill_obj = save_bill_data(normalized, client.id)
#                     serializer = UatElectricityBillSerializer(bill_obj)
#                     self._log_request(customer_id, vendor.vendor_name, endpoint, 200, "success", request.data, serializer.data, None, user, bill_obj)
#                     return Response({"success": True, "status": 200, "message": f"Data from {vendor.vendor_name}", "data": serializer.data})

#             except Exception as e:
#                 self._log_request(customer_id, vendor.vendor_name, endpoint, 500, "fail", request.data, None, str(e), user)
#                 return Response({"success": False, "status": 500, "error": str(e)}, status=500)

#         self._log_request(customer_id, None, endpoint, 404, "fail", request.data, None, "All vendors failed", user)
#         return Response({"success": False, "status": 404, "error": "All vendors failed"}, status=404)

from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from kyc_api_gateway.models import (
    UatElectricityBill,
    VendorManagement,
    ClientManagement
)
from kyc_api_gateway.models.uat_bill_request_log import UatBillRequestLog
from kyc_api_gateway.models.kyc_client_services_management import KycClientServicesManagement
from kyc_api_gateway.serializers.uat_bill_details_serializer import UatElectricityBillSerializer
from kyc_api_gateway.services.uat.bill_handler import (
    call_vendor_api,
    save_bill_data,
    normalize_vendor_response,
)


class BillUatDetailsAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Main entrypoint for fetching Electricity Bill details (UAT)."""
        # Authenticate client
        client = self._authenticate_client(request, env="uat")
        if isinstance(client, Response):
            return client

        # Validate service
        services = self._get_client_services(client, env="uat")
        if isinstance(services, Response):
            return services

        service = next((s for s in services if s["name"].upper() == "BILL"), None)
        if not service:
            return Response(
                {"success": False, "status": 403, "error": "Bill service not assigned"},
                status=403,
            )

        # Fetch and return bill details
        return self._fetch_bill(request, env="uat", client=client, service=service)

    # ---------------- Helper Methods ----------------

    def _authenticate_client(self, request, env):
        """Authenticate client using X-API-KEY header."""
        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            return Response(
                {"success": False, "status": 401, "error": "Missing API key"},
                status=401,
            )

        client = ClientManagement.objects.filter(
            uat_key=api_key if env == "uat" else api_key,
            deleted_at__isnull=True,
        ).first()

        if not client:
            return Response(
                {"success": False, "status": 401, "error": "Invalid API key"},
                status=401,
            )

        return client

    def _get_client_services(self, client, env):
        """Fetch all active services assigned to the client."""
        client_services = (
            KycClientServicesManagement.objects.filter(
                client=client, status=True, deleted_at__isnull=True
            ).select_related("myservice")
        )

        if not client_services.exists():
            return Response(
                {"success": False, "status": 403, "error": "No active services assigned"},
                status=403,
            )

        services = []
        for cs in client_services:
            my_service = cs.myservice
            url = my_service.uat_url if env == "uat" else my_service.prod_url
            services.append({"id": my_service.id, "name": my_service.name, "url": url})
        return services

    def _log_request(
        self,
        customer_id,
        vendor,
        endpoint,
        status_code,
        status,
        request_payload=None,
        response_payload=None,
        error_message=None,
        user=None,
        bill_details=None,
    ):
        """Create log entry for each request or response."""
        UatBillRequestLog.objects.create(
            customer_id=customer_id,
            bill_details=bill_details,
            vendor=vendor,
            endpoint=endpoint,
            status_code=status_code,
            status=status,
            request_payload=request_payload,
            response_payload=response_payload,
            error_message=error_message,
            user=user,
        )

    def _fetch_bill(self, request, env, client, service):
        """Main handler for fetching bill details from cache or vendors."""
        customer_id = request.data.get("consumer_id") or request.data.get("id_number")
        endpoint = request.path
        user = request.user if getattr(request.user, "is_authenticated", False) else None

        # Validate required field
        if not customer_id:
            self._log_request(
                None,
                service["name"],
                endpoint,
                400,
                "fail",
                request.data,
                None,
                "Customer ID missing",
                user,
            )
            return Response(
                {"success": False, "status": 400, "error": "Customer/Consumer ID required"},
                status=400,
            )

        # Check cache (7 days validity)
        seven_days_ago = timezone.now() - timedelta(days=7)
        cached = UatElectricityBill.objects.filter(
            customer_id=customer_id, created_at__gte=seven_days_ago
        ).first()

        if cached:
            serializer = UatElectricityBillSerializer(cached)
            self._log_request(
                customer_id,
                "cached",
                endpoint,
                200,
                "success",
                request.data,
                serializer.data,
                None,
                user,
                cached,
            )
            return Response(
                {"success": True, "status": 200, "message": "Cached data", "data": serializer.data}
            )

        # Try vendors sequentially (based on priority)
        vendors = VendorManagement.objects.filter(
            status="Active", deleted_at__isnull=True
        ).order_by("priority")

        for vendor in vendors:
            try:
                response = call_vendor_api(vendor, request.data, env)
                if not response:
                    self._log_request(
                        customer_id,
                        vendor.vendor_name,
                        endpoint,
                        502,
                        "fail",
                        request.data,
                        None,
                        "No response",
                        user,
                    )
                    continue

                data = response.json()
                normalized = normalize_vendor_response(vendor.vendor_name, data)
                if normalized:
                    bill_obj = save_bill_data(normalized, client.id)
                    serializer = UatElectricityBillSerializer(bill_obj)
                    self._log_request(
                        customer_id,
                        vendor.vendor_name,
                        endpoint,
                        200,
                        "success",
                        request.data,
                        serializer.data,
                        None,
                        user,
                        bill_obj,
                    )
                    return Response(
                        {
                            "success": True,
                            "status": 200,
                            "message": f"Data from {vendor.vendor_name}",
                            "data": serializer.data,
                        }
                    )

            except Exception as e:
                self._log_request(
                    customer_id,
                    vendor.vendor_name,
                    endpoint,
                    500,
                    "fail",
                    request.data,
                    None,
                    str(e),
                    user,
                )
                return Response(
                    {"success": False, "status": 500, "error": str(e)}, status=500
                )

        # If all vendors failed
        self._log_request(
            customer_id,
            None,
            endpoint,
            404,
            "fail",
            request.data,
            None,
            "All vendors failed",
            user,
        )
        return Response(
            {"success": False, "status": 404, "error": "All vendors failed"}, status=404
        )
