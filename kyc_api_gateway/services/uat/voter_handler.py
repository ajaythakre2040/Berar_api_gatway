import requests
from decouple import config
from kyc_api_gateway.models import UatVoterDetail
from kyc_api_gateway.utils.constants import VENDOR_VOTER_SERVICE_ENDPOINTS

SUREPASS_TOKEN = config("SUREPASS_TOKEN", default=None)
if not SUREPASS_TOKEN:
    raise ValueError("SUREPASS_TOKEN is not set in your environment variables.")


def build_voter_request(vendor_name, request_data):
    vendor_key = vendor_name.strip().lower()

    if vendor_key == "karza":
        return {
            "consent": request_data.get("consent", "Y"),
            "epicNo": request_data.get("id_number"),
            "clientData": {"caseId": "123456"},
        }

    elif vendor_key == "surepass":
        return {
            "id_number": request_data.get("id_number"),
        }

    return request_data


def call_voter_vendor_api(vendor, request_data, env="uat"):
    vendor_key = vendor.vendor_name.lower()
    endpoint_path = VENDOR_VOTER_SERVICE_ENDPOINTS.get(vendor_key, {}).get(env)
    if not endpoint_path:
        print(f"[ERROR] Vendor '{vendor.vendor_name}' has no endpoint path for {env}.")
        return None

    base_url = vendor.end_point_uat if env == "uat" else vendor.end_point_production
    if not base_url:
        print(f"[ERROR] Vendor '{vendor.vendor_name}' has no base URL for {env}.")
        return None

    full_url = f"{base_url.rstrip('/')}/{endpoint_path.lstrip('/')}"
    payload = build_voter_request(vendor_key, request_data)
    headers = {"Content-Type": "application/json"}

    if vendor_key == "karza":
        headers["x-karza-key"] = vendor.uat_key if env == "uat" else vendor.production_key
    elif vendor_key == "surepass":
        headers["Authorization"] = f"Bearer {SUREPASS_TOKEN}"


    try:
        response = requests.post(full_url, json=payload, headers=headers, timeout=vendor.timeout or 30)
        if response.status_code != 200:
            print(f"[WARN] {vendor.vendor_name} returned non-200: {response.status_code}")
            return None

        try:
            data = response.json()
            return data
        except ValueError:
            print(f"[ERROR] Vendor '{vendor.vendor_name}' returned invalid JSON: {response.text}")
            return None

    except Exception as e:
        print(f"[ERROR] Vendor API call failed ({vendor.vendor_name}): {str(e)}")
        return None


def normalize_voter_response(vendor_name, raw_data):
    if not isinstance(raw_data, dict):
        print(f"[ERROR] normalize_voter_response got invalid raw_data: {raw_data}")
        return None

    vendor_key = vendor_name.lower()

    if vendor_key == "karza":
        result = raw_data.get("result", {})
        if not result:
            print("[WARN] Karza returned empty result, skipping...")
            return None
        return {
            "vendor": "karza",
            "client_id": raw_data.get("clientData", {}).get("caseId"),
            "voter_id": result.get("epicNo"),
            "name": result.get("name"),
            "relation_name": result.get("rlnName"),
            "relation_type": result.get("rlnType"),
            "gender": result.get("gender"),
            "district": result.get("district"),
            "state": result.get("state"),
            "assembly_constituency": result.get("acName"),
            "assembly_constituency_number": result.get("acNo"),
            "polling_station": result.get("psName"),
            "part_no": result.get("partNo"),
            "slno_in_part": result.get("slNoInPart"),
            "ps_lat_long": result.get("psLatLong"),
            "house_no": result.get("houseNo"),
            "last_update": result.get("lastUpdate"),
            "st_code": result.get("stCode"),
        }

    elif vendor_key == "surepass":
        result = raw_data.get("data", {})
        if not result:
            print("[WARN] Surepass returned empty data")
            return None
        return {
            "vendor": "surepass",
            "client_id": result.get("client_id"),
            "voter_id": result.get("epic_no"),
            "name": result.get("name"),
            "relation_name": result.get("relation_name"),
            "relation_type": result.get("relation_type"),
            "gender": result.get("gender"),
            "district": result.get("district"),
            "state": result.get("state"),
            "assembly_constituency": result.get("assembly_constituency"),
            "assembly_constituency_number": result.get("assembly_constituency_number"),
            "polling_station": result.get("polling_station"),
            "part_no": result.get("part_number"),
            "part_name": result.get("part_name"),
            "slno_in_part": result.get("slno_inpart"),
            "ps_lat_long": result.get("ps_lat_long"),
            "house_no": result.get("house_no"),
            "last_update": result.get("last_update"),
            "st_code": result.get("st_code"),
            "parliamentary_name": result.get("parliamentary_name"),
            "parliamentary_number": result.get("parliamentary_number"),
        }

    print(f"[WARN] Unknown vendor '{vendor_name}', returning None")
    return None


def save_voter_data(normalized, created_by):
    if not normalized:
        print("[ERROR] Cannot save voter data: normalized is None")
        return None
    try:
        return UatVoterDetail.objects.create(**normalized, created_by=created_by)
    except Exception as e:
        print(f"[ERROR] Failed to save voter data: {e}")
        return None

