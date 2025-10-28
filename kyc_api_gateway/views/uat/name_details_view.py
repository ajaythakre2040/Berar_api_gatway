from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from kyc_api_gateway.models import (
    UatNameMatch,
    ClientManagement,
    KycClientServicesManagement,
    KycVendorPriority
)
from kyc_api_gateway.models.uat_name_request_log import UatNameMatchRequestLog
from kyc_api_gateway.serializers.uat_name_match_serializer import UatNameMatchSerializer

from kyc_api_gateway.services.uat.name_handler import call_vendor_api_uat, normalize_vendor_response , save_name_match_uat 
from constant import KYC_MY_SERVICES

class NameMatchUatAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    

    def post(self, request):

        name1 = request.data.get("name_1")
        name2 = request.data.get("name_2")

        ip_address = self.get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")


        if not name1 or not name2 or name1.strip() == "":
            missing = []
            if not name1 or name1.strip() == "":
                missing.append("name1")
            if not name2 or name2.strip() == "":
                missing.append("name2")
            
            error_msg = f"Missing required fields: {', '.join(missing)}"
            self._log_request(
                name1=name1,
                name2=name2,
                vendor_name=None,
                endpoint=request.path,
                status_code=400,
                status="fail",
                request_payload=request.data,
                response_payload=None,
                error_message=error_msg,
                user=None,
                match_obj=None,
                ip_address=ip_address,
                user_agent=user_agent
            )
            return Response({
                "success": False,
                "status": 400,
                "error": error_msg
            }, status=400)
        
        client = self._authenticate_client(request)
        if isinstance(client, Response):
            return client
        
        service_name = "NAME"
        service_id = KYC_MY_SERVICES.get(service_name.upper())

        if not service_id:
            error_msg = "Name Match service not assigned"
            self._log_request(
                name1=name1,
                name2=name2,
                vendor_name=None,
                endpoint=request.path,
                status_code=403,
                status="fail",
                request_payload=request.data,
                response_payload=None,
                error_message=error_msg,
                user=None,
                match_obj=None,
                ip_address=ip_address,
                user_agent=user_agent
            )
            return Response({
                "success": False,
                "status": 403,
                "error": error_msg
            }, status=403)
        
        try:
            cache_days = self._get_cache_days(client, service_id)

        except PermissionError as e:

            self._log_request(
                name1=name1,
                name2=name2,
                vendor_name=None,
                endpoint=request.path,
                status_code=403,
                status="fail",
                request_payload=request.data,
                response_payload=None,
                error_message=str(e),
                user=None,
                match_obj=None,
                ip_address=ip_address,
                user_agent=user_agent
            )
            return Response({
                "success": False,
                "status": 403,
                "error": error_msg
            }, status=403)

        except ValueError as e:
            self._log_request(
                name1=name1,
                name2=name2,
                vendor_name=None,
                endpoint=request.path,
                status_code=500,
                status="fail",
                request_payload=request.data,
                response_payload=None,
                error_message=str(e),
                user=None,
                match_obj=None,
                ip_address=ip_address,
                user_agent=user_agent
            )
            return Response({
                "success": False,
                "status": 500,
                "error": str(e)
            }, status=500)
           
        days_ago = timezone.now() - timedelta(days=cache_days)
        name1 = request.data.get("name_1").strip()
        name2 = request.data.get("name_2").strip()

        cached = UatNameMatch.objects.filter(
            name_1__iexact=name1,
            name_2__iexact=name2,
            created_at__gte=days_ago
        ).first()

        if cached:
            serializer = UatNameMatchSerializer(cached)
            self._log_request(
                name1=name1,
                name2=name2,
                vendor_name="cached",
                endpoint=request.path,
                status_code=200,
                status="success",
                request_payload=request.data,
                response_payload=serializer.data,
                error_message=None,
                user=None,
                match_obj=cached,
                ip_address=ip_address,
                user_agent=user_agent
            )

            return Response({
                "success": True,
                "status": 200,
                "message": "Cached data",
                "data": serializer.data
            })
        
        vendors = self._get_priority_vendors(client, service_id)
        print(f"[DEBUG] Found {vendors.count()} priority vendors for client={client.id}, service_id={service_id}")

        if not vendors.exists():
            error_msg = "No vendors configured for Name Match service"
            self._log_request(
                name1=name1,
                name2=name2,
                vendor_name=None,
                endpoint=request.path,
                status_code=403,
                status="fail",
                request_payload=request.data,
                response_payload=None,
                error_message=error_msg,
                user=None,
                match_obj=None,
                ip_address=ip_address,
                user_agent=user_agent
            )
            return Response({
                "success": False,
                "status": 403,
                "error": error_msg
            }, status=403)
        
        endpoint = request.path

        for vp in vendors:
            vendor = vp.vendor

            try:
                response = call_vendor_api_uat(vendor, request.data)

                if response and response.get("http_error"):
                    self._log_request(
                        name1=name1,
                        name2=name2,
                        vendor_name=vendor.vendor_name,
                        endpoint=endpoint,
                        status_code=response.get("status_code") or 500,
                        status="fail",
                        request_payload=request.data,
                        response_payload=response.get("vendor_response"),
                        error_message=response.get("error_message"),
                        user=None,
                        match_obj=None,
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                    continue 
                try:
                    data = response
                except Exception:
                    data = None

                normalized = normalize_vendor_response(vendor.vendor_name, data or {})

                if not normalized:
                    error_msg = f"Normalization failed for vendor {vendor.vendor_name}"
                    self._log_request(
                        name1=name1,
                        name2=name2,
                        vendor_name=vendor.vendor_name,
                        endpoint=endpoint,
                        status_code=502,
                        status="fail",
                        request_payload=request.data,
                        response_payload=data,
                        error_message=error_msg,
                        user=None,
                        match_obj=None,
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                    continue
                
                name_obj = save_name_match_uat(normalized, client.id)
                serializer = UatNameMatchSerializer(name_obj)

                self._log_request(
                    name1=name1,
                    name2=name2,
                    vendor_name=vendor.vendor_name,
                    endpoint=endpoint,
                    status_code=200,
                    status="success",
                    request_payload=request.data,
                    response_payload=serializer.data,
                    error_message=None,
                    user=None,
                    match_obj=name_obj,
                    ip_address=ip_address,
                    user_agent=user_agent
                )

                return Response({
                    "success": True,
                    "status": 200,
                    "message": f"Data from {vendor.vendor_name}",
                    "data": serializer.data
                })

            except Exception as e:
                error_msg = f"Request to vendor {vendor.vendor_name} failed: {str(e)}"
                self._log_request(
                    name1=name1,
                    name2=name2,
                    vendor_name=vendor.vendor_name,
                    endpoint=endpoint,
                    status_code=500,
                    status="fail",
                    request_payload=request.data,
                    response_payload=None,
                    error_message=error_msg,
                    user=None,
                    match_obj=None,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                continue
            
        return Response({
            "success": False,
            "status": 404,
            "error": "No vendor returned valid data"
        }, status=404)

    def _authenticate_client(self, request):

        ip_address = self.get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        api_key = request.headers.get("X-API-KEY")
        if not api_key:

            error_msg = "Missing API key"

            self._log_request(
                name1=None,
                name2=None,
                vendor_name=None,
                endpoint=request.path,
                status_code=401,
                status="fail",
                request_payload=None,
                response_payload=None,
                error_message=error_msg,
                user=None,
                match_obj=None,
                ip_address=ip_address,
                user_agent=user_agent
            )
        
            return Response({
                "success": False,
                "status": 401,
                "error": error_msg
            }, status=401)

        client = ClientManagement.objects.filter(
            uat_key=api_key,
            deleted_at__isnull=True
        ).first()

        if not client:
            error_msg = "Invalid API key"
            self._log_request(
                name1=None,
                name2=None,
                vendor_name=None,
                endpoint=request.path,
                status_code=401,
                status="fail",
                request_payload=None,
                response_payload=None,
                error_message=error_msg,
                user=None,
                match_obj=None,
                ip_address=ip_address,
                user_agent=user_agent
            )

            return Response({
                "success": False,
                "status": 401,
                "error": error_msg}
                , status=401)
        
        return client

    def _get_cache_days(self, client, service_id):
       
        cs = KycClientServicesManagement.objects.filter(
            client=client,
            myservice__id=service_id,
            deleted_at__isnull=True
        ).first()

        if not cs:
            raise ValueError(f"Cache days not configured for client={client.id}, service_id={service_id}")

        if cs.status is False:
            raise PermissionError(f"Service is not permitted for client")

        return cs.day
    

    def _get_priority_vendors(self, client, service_id):
        return KycVendorPriority.objects.filter(
            client=client,
            my_service_id=service_id,
            deleted_at__isnull=True
        ).select_related("vendor").order_by("priority")
    

    def _log_request(self, name1, name2, vendor_name, endpoint, status_code, status, request_payload=None, response_payload=None, error_message=None, user=None, match_obj=None, ip_address=None, user_agent=None):

         if not isinstance(status_code, int):
            raise ValueError(f"status_code must be an integer, got {status_code!r}")
         
         UatNameMatchRequestLog.objects.create(
                name_1=name1,
                name_2=name2,
                vendor=vendor_name,
                endpoint=endpoint,
                status_code=status_code,
                status=status,
                request_payload=request_payload,
                response_payload=response_payload,
                error_message=error_message,
                user=user if user and user.is_authenticated else None,
                name_match=match_obj,
                ip_address=ip_address,
                user_agent=user_agent,
         )

