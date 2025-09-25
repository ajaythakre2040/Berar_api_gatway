from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from kyc_api_gateway.models.pan_details import PanDetails
from kyc_api_gateway.models.vendor_management import VendorManagement
from kyc_api_gateway.serializers.pan_details_serializer import PanDetailsSerializer
import requests
import logging

logger = logging.getLogger(__name__)


class PanDetailsAPIView(APIView):
    def get(self, request):
        pan_number = request.GET.get("pan")
        # consent = request.GET.get("consent")
        # consent = "y"



        if not pan_number:
            return Response(
                {"error": "PAN number is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        print(pan_number)
        pan_number = pan_number.upper().strip()

        # Step 1: DB Cache - 7 Days
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_pan = PanDetails.objects.filter(
            pan_number=pan_number,
            created_at__gte=seven_days_ago,
            deleted_at__isnull=True,
        ).first()
        print(seven_days_ago)
        print(recent_pan)
        # print(recent_pan.__dict__)

        if recent_pan:
            serializer = PanDetailsSerializer(recent_pan)
            return Response(
                {"message": "Data from cache (DB)", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        # Step 2: Vendor API by priority
        vendors = VendorManagement.objects.filter(status="Active").order_by("priority")
        # print(vendors)

        for vendor in vendors:
            print(f"Checking Vendor: {vendor.vendor_name}, URL: {vendor.base_url}, Priority: {vendor.priority}")

            try:
                response = requests.get(
                    vendor.base_url,
                    params={"pan": pan_number},
                    timeout=vendor.timeout or 10,
                )

                if response.status_code == 200:
                    data = response.json()

                    if self.is_valid_response(data):
                        created_by = (
                            request.user.id if request.user.is_authenticated else 0
                        )

                        pan_obj = self.save_pan_data(
                            data=data,
                            pan_number=pan_number,
                            created_by=created_by,
                        )

                        serializer = PanDetailsSerializer(pan_obj)
                        return Response(
                            {
                                "message": f"Data fetched from vendor: {vendor.vendor_name}",
                                "data": serializer.data,
                            },
                            status=status.HTTP_200_OK,
                        )

            except Exception as e:
                print(f"Vendor API failed: {vendor.vendor_name}, Error: {str(e)}")

                logger.warning(
                    f"Vendor API failed: {vendor.vendor_name}, Error: {str(e)}"
                )
                continue

        return Response(
            {"error": "Unable to fetch PAN details from all vendors"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    def is_valid_response(self, data):
        result = data.get("result") or data.get("data")
        return result and result.get("pan")

    def save_pan_data(self, data, pan_number,  created_by):
        result = data.get("result") or data.get("data")

        obj = PanDetails.objects.create(
            pan_number=pan_number,
            full_name=result.get("full_name") or result.get("name"),
            first_name=result.get("firstName"),
            middle_name=result.get("middleName"),
            last_name=result.get("lastName"),
            gender=result.get("gender"),
            dob=result.get("dob") or result.get("input_dob"),
            dob_verified=result.get("dob_verified"),
            dob_check=result.get("dob_check"),
            phone_number=result.get("mobileNo") or result.get("phone_number"),
            email=result.get("emailId") or result.get("email"),
            aadhaar_linked=result.get("aadhaarLinked") or result.get("aadhaar_linked"),
            masked_aadhaar=result.get("masked_aadhaar"),
            aadhaar_match=result.get("aadhaarMatch"),
            pan_status=result.get("status"),
            is_salaried=result.get("isSalaried"),
            is_director=result.get("isDirector"),
            is_sole_prop=result.get("isSoleProp"),
            issue_date=result.get("issueDate"),
            profile_match=result.get("profileMatch"),
            category=result.get("category"),
            less_info=result.get("less_info"),
            request_id=data.get("requestId"),
            client_id=data.get("client_id"),
            address_line_1=result.get("address", {}).get("buildingName")
            or result.get("address", {}).get("line_1"),
            address_line_2=result.get("address", {}).get("locality")
            or result.get("address", {}).get("line_2"),
            street_name=result.get("address", {}).get("streetName")
            or result.get("address", {}).get("street_name"),
            city=result.get("address", {}).get("city"),
            state=result.get("address", {}).get("state"),
            pin_code=result.get("address", {}).get("pinCode")
            or result.get("address", {}).get("zip"),
            country=result.get("address", {}).get("country", "INDIA"),
            full_address=result.get("address", {}).get("full"),
            created_by=created_by,
        )
        return obj
