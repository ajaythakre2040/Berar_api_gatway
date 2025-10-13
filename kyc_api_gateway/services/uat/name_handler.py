import requests
from decimal import Decimal
from decouple import config
from kyc_api_gateway.models import UatNameMatch
from kyc_api_gateway.utils.constants import VENDOR_NAME_SERVICE_ENDPOINTS

SUREPASS_TOKEN = config("SUREPASS_TOKEN", default=None)
if not SUREPASS_TOKEN:
    raise ValueError("SUREPASS_TOKEN is not set in your environment variables.")


def build_name_request(vendor_name, request_data):
    if vendor_name.lower() == "karza":
        return {
            "name1": request_data.get("name_1") or request_data.get("name1"),
            "name2": request_data.get("name_2") or request_data.get("name2"),
            "type": request_data.get("type", "individual"),
            "preset": "s",
            "allowPartialMatch": True,
            "suppressReorderPenalty": True,
            "clientData": {"caseId": "123456"},
        }

    elif vendor_name.lower() == "surepass":
        return {
            "name_1": request_data.get("name_1"),
            "name_2": request_data.get("name_2"),
            "name_type": request_data.get("name_type", "person"),
        }

    return request_data


def call_name_vendor_api(vendor, request_data, env="uat"):
    vendor_key = vendor.vendor_name.lower()
    endpoint_path = VENDOR_NAME_SERVICE_ENDPOINTS.get(vendor_key)
    if not endpoint_path:
        print(f"[ERROR] No endpoint for vendor: {vendor.vendor_name}")
        return None

    base_url = vendor.end_point_uat if env == "uat" else vendor.end_point_production
    full_url = f"{base_url.rstrip('/')}/{endpoint_path.lstrip('/')}"
    headers = {"Content-Type": "application/json"}

    if vendor_key == "karza":
        headers["x-karza-key"] = vendor.uat_key if env == "uat" else vendor.production_key
    elif vendor_key == "surepass":
        headers["Authorization"] = f"Bearer {SUREPASS_TOKEN}"

    payload = build_name_request(vendor_key, request_data)

    try:
        response = requests.post(full_url, json=payload, headers=headers, timeout=vendor.timeout or 30)
        return response
    except Exception as e:
        print(f"[ERROR] {vendor.vendor_name} request failed: {str(e)}")
        return None


def normalize_name_response(vendor_name, raw_data, request_data=None):
    if vendor_name.lower() == "karza":
        return {
            "client_id": raw_data.get("requestId"),
            "request_id": raw_data.get("requestId"),
            "name_1": (request_data.get("name_1") or request_data.get("name1")) if request_data else None,
            "name_2": (request_data.get("name_2") or request_data.get("name2")) if request_data else None,
            "match_score": sanitize_decimal(raw_data.get("result", {}).get("score")),
            "match_status": raw_data.get("result", {}).get("result"),
        }

    elif vendor_name.lower() == "surepass":
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


def save_name_match(normalized, created_by):
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
