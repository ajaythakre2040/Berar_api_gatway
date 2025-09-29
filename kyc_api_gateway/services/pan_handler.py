import requests
from kyc_api_gateway.utils.constants import (
    VENDOR_KARZA,
    VENDOR_SUREPASS,
    VENDOR_DIGITALOCEANN,
    VENDOR_SERVICE_ENDPOINTS,
    DEFAULT_COUNTRY,
)
from kyc_api_gateway.models import PanDetails


def build_vendor_request(vendor_code, pan_number):
    if vendor_code == VENDOR_KARZA:
        return {
            "pan": pan_number,
            "aadhaarLastFour": "",
            "dob": "",
            "name": "",
            "address": "",
            "getContactDetails": "Y",
            "PANStatus": "Y",
            "isSalaried": "Y",
            "isDirector": "Y",
            "isSoleProp": "Y",
            "consent": "Y",
        }
    elif vendor_code == VENDOR_SUREPASS:
        return {"id_number": pan_number}
    return {"pan": pan_number, "consent": "Y"}


def call_vendor_api(vendor, pan_number):
    vendor_key = vendor.vendor_name.lower()
    endpoint_path = VENDOR_SERVICE_ENDPOINTS.get(vendor_key)

    if not endpoint_path:
        print(
            f"Vendor {vendor.vendor_name} does not have a service path configured, skipping."
        )
        return None

    if not vendor.end_point_production:
        print(
            f"Vendor {vendor.vendor_name} does not have an endpoint URL set, skipping."
        )
        return None

    base_url = vendor.end_point_production.rstrip("/")
    full_url =" https://testapi.karza.in/v3/pan-profile"

    payload = build_vendor_request(vendor_key, pan_number)
    headers = {}

    try:
        if vendor_key == VENDOR_KARZA:
            headers = {
                "x-karza-key": "XPUJ4jwzn3n5xxwjq9al",
                "Content-Type": "application/json",
            }
            response = requests.post(
                full_url, json=payload, headers=headers, timeout=vendor.timeout or 30
            )

        elif vendor_key == VENDOR_SUREPASS:
            headers = {
                "Authorization": f"Bearer {vendor.production_key}",
                "Content-Type": "application/json",
            }
            response = requests.post(
                full_url, json=payload, headers=headers, timeout=vendor.timeout or 30
            )

        else:
            response = requests.get(
                full_url, params={"pan": pan_number}, timeout=vendor.timeout
            )

        print(f"Vendor {vendor.vendor_name} returned status {response.status_code}")
        return response

    except Exception as e:
        print(f"Vendor {vendor.vendor_name} failed: {e}")
        return None


def save_pan_data(data, pan_number, created_by, vendor):
    result = data.get("result") or data.get("data") or {}
    address = result.get("address", {})

    first_name = result.get("firstName")
    middle_name = result.get("middleName")
    last_name = result.get("lastName")
    full_name = result.get("name") or result.get("full_name")

    if vendor.vendor_name.lower() == VENDOR_SUREPASS:
        split = result.get("full_name_split", [])
        first_name = split[0] if len(split) > 0 else None
        middle_name = split[1] if len(split) > 1 else None
        last_name = split[2] if len(split) > 2 else None
        gender = (
            "male" if result.get("gender", "").lower().startswith("m") else "female"
        )
    else:
        gender = result.get("gender")

    pan_obj = PanDetails.objects.create(
        pan_number=pan_number,
        full_name=full_name,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        gender=gender,
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
        category=result.get("category"),
        less_info=result.get("less_info"),
        request_id=data.get("requestId"),
        client_id=data.get("client_id"),
        address_line_1=address.get("buildingName") or address.get("line_1"),
        address_line_2=address.get("locality") or address.get("line_2"),
        street_name=address.get("streetName") or address.get("street_name"),
        city=address.get("city"),
        state=address.get("state"),
        pin_code=address.get("pinCode") or address.get("zip"),
        country=address.get("country", DEFAULT_COUNTRY),
        full_address=address.get("full"),
        created_by=created_by,
    )
    return pan_obj
