from rest_framework import serializers
from kyc_api_gateway.models.pan_details import PanDetails


class PanDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanDetails
        fields = [
            "id",
            # Vendor metadata
            "request_id",
            "client_id",
            # PAN and name
            "pan_number",
            "full_name",
            "first_name",
            "middle_name",
            "last_name",
            # Aadhaar
            "aadhaar_linked",
            "masked_aadhaar",
            "aadhaar_match",
            # DOB
            "dob",
            
            "dob_verified",
            "dob_check",
            # Gender
            "gender",
            # Contact
            "phone_number",
            "email",
            # PAN status & professional info
            "pan_status",
            "is_salaried",
            "is_director",
            "is_sole_prop",
            "issue_date",
            "category",
            "less_info",
            # Profile match
            "profile_match",
            # Address
            "address_line_1",
            "address_line_2",
            "street_name",
            "city",
            "state",
            "pin_code",
            "country",
            "full_address",
            # Timestamps
            "created_at",
            "updated_at",
            "deleted_at",
            "created_by",
            "updated_by",
            "deleted_by",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "deleted_at",
            "created_by",
            "updated_by",
            "deleted_by",
        ]
