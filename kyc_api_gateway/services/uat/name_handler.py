import requests
from decimal import Decimal
from decouple import config
from kyc_api_gateway.models import UatNameMatch
from kyc_api_gateway.utils.constants import VENDOR_NAME_SERVICE_ENDPOINTS

SUREPASS_TOKEN = config("SUREPASS_TOKEN", default=None)
if not SUREPASS_TOKEN:
    raise ValueError("SUREPASS_TOKEN is not set in your environment variables.")


def build_name_request_uat(vendor_name, request_data):
  
    vendor_key = vendor_name.lower()

    if vendor_key == "karza":
        return {
            "name1": request_data.get("name_1") or request_data.get("name1"),
            "name2": request_data.get("name_2") or request_data.get("name2"),
            "type": request_data.get("type", "individual"),
            "preset": "s",
            "allowPartialMatch": True,
            "suppressReorderPenalty": True,
            "clientData": {"caseId": request_data.get("case_id", "123456")},
        }

    elif vendor_key == "surepass":
        return {
            "name_1": request_data.get("name_1"),
            "name_2": request_data.get("name_2"),
            "name_type": request_data.get("name_type", "person"),
        }

    return request_data


def call_vendor_api_uat(vendor, request_data):
    vendor_key = vendor.vendor_name.lower()
    endpoint_path = VENDOR_NAME_SERVICE_ENDPOINTS.get(vendor_key)
    base_url = vendor.uat_base_url

    print(f"vendor_key: {vendor_key}")
    print(f"endpoint_path: {endpoint_path}")
    print(f"base_url: {base_url}")

    if not endpoint_path or not base_url:
        print(f"[ERROR] Vendor '{vendor.vendor_name}' not configured properly.")
        return None

    full_url = f"{base_url.rstrip('/')}/{endpoint_path.lstrip('/')}"
    payload = build_name_request_uat(vendor_key, request_data)

    headers = {"Content-Type": "application/json"}
    if vendor_key == "karza":
        headers["x-karza-key"] = vendor.uat_api_key
    elif vendor_key == "surepass":
        headers["Authorization"] = f"Bearer {SUREPASS_TOKEN}"

    print("\n--- Calling Vendor UAT Name API ---")
    print("URL:", full_url)
    print("Headers:", headers)
    print("Payload:", payload)

    try:
        response = requests.post(full_url, json=payload, headers=headers)
        response.raise_for_status()

        print("\n--- Vendor UAT Name API Response ---")
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())

        return response.json()

    except requests.HTTPError as e:
        try:
            error_content = response.json()
        except Exception:
            error_content = response.text

        print("\n--- Vendor UAT Name API HTTPError ---")
        print("Status Code:", response.status_code)
        print("Error Message:", str(e))
        print("Error Content:", error_content)

        return {
            "http_error": True,
            "status_code": response.status_code,
            "vendor_response": error_content,
            "error_message": str(e),
        }

    except Exception as e:
        print("\n--- Vendor UAT Name API General Exception ---")
        print("Error Message:", str(e))

        return {
            "http_error": True,
            "status_code": None,
            "vendor_response": None,
            "error_message": str(e),
        }


def normalize_vendor_response(vendor_name, raw_data, request_data=None):
    vendor_name = vendor_name.lower()
    if vendor_name == "karza":
        return {
            "client_id": raw_data.get("requestId"),
            "request_id": raw_data.get("requestId"),
            "name_1": request_data.get("name_1") or request_data.get("name1") if request_data else None,
            "name_2": request_data.get("name_2") or request_data.get("name2") if request_data else None,
            "match_score": sanitize_decimal(raw_data.get("result", {}).get("score")),
            "match_status": raw_data.get("result", {}).get("result"),
        }
    elif vendor_name == "surepass":
        result = raw_data.get("data", {})
        return {
            "client_id": result.get("client_id"),
            "request_id": None,
            "name_1": result.get("name_1"),
            "name_2": result.get("name_2"),
            "match_score": sanitize_decimal(result.get("match_score")),
            "match_status": result.get("match_status"),
        }
    return None

def sanitize_decimal(value):
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def save_name_match_uat(normalized, created_by):
    match_obj = UatNameMatch.objects.create(
        client_id=normalized.get("client_id"),
        request_id=normalized.get("request_id"),
        name_1=normalized.get("name_1"),
        name_2=normalized.get("name_2"),
        match_score=normalized.get("match_score"),
        match_status=normalized.get("match_status"),
        created_by=created_by,
    )
    return match_obj
