

# import requests
# from decouple import config
# from kyc_api_gateway.models import UatElectricityBill
# from kyc_api_gateway.utils.constants import VENDOR_BILL_SERVICE_ENDPOINTS
# from decimal import Decimal

# SUREPASS_TOKEN = config("SUREPASS_TOKEN", default=None)
# if not SUREPASS_TOKEN:
#     raise ValueError("SUREPASS_TOKEN is not set in your environment variables.")

# def build_vendor_request(vendor_name, request_data):
#     if vendor_name.lower() == "karza":
#         return {
#             "consumer_id": request_data.get("consumer_id"),
#             "service_provider": request_data.get("service_provider"),
#             "district": request_data.get("district"),
#             "regMobileNo": request_data.get("regMobileNo"),
#             "consent": request_data.get("consent", "Y"),
#             "clientData": request_data.get("clientData", {}),
#         }

#     elif vendor_name.lower() == "surepass":
#         return {
#             "id_number": request_data.get("consumer_id"),
#             "operator_code": request_data.get("service_provider"),
#         }

#     return request_data


# def call_vendor_api(vendor, request_data, env="uat"):
#     vendor_key = vendor.vendor_name.lower()
#     endpoint_path = VENDOR_BILL_SERVICE_ENDPOINTS.get(vendor_key)

#     print(f"Calling vendor API: {vendor.vendor_name} at {env} environment")

#     if not endpoint_path:
#         print(f"[ERROR] Vendor '{vendor.vendor_name}' has no endpoint path configured.")
#         return None

#     base_url = vendor.end_point_uat if env == "uat" else vendor.end_point_production
#     if not base_url:
#         print(f"[ERROR] Vendor '{vendor.vendor_name}' has no {env} URL configured.")
#         return None

#     key = vendor.uat_key if env == "uat" else vendor.production_key
#     full_url = f"{base_url.rstrip('/')}/{endpoint_path.lstrip('/')}"

#     print(f"Full URL: {full_url}")
#     payload = build_vendor_request(vendor_key, request_data)
#     headers = {"Content-Type": "application/json"}


#     if vendor_key == "karza":
#         headers["x-karza-key"] = key
#     elif vendor_key == "surepass":
#         headers["Authorization"] = f"Bearer {SUREPASS_TOKEN}"

#     try:
#         response = requests.post(full_url, json=payload, headers=headers, timeout=vendor.timeout or 30)
#         return response
#     except Exception as e:
#         print(f"[ERROR] API call failed for vendor '{vendor.vendor_name}': {str(e)}")
#         return None

# def normalize_vendor_response(vendor_name, raw_data):
#     result = raw_data.get("result") or raw_data.get("data") or {}
#     if not result:
#         return None

#     if vendor_name.lower() == "karza":
#         return {
#             "client_id": raw_data.get("request_id"), 
#             "consumer_id": result.get("consumer_number") or result.get("consumer_id"),
#             "customer_id": result.get("consumer_number") or result.get("consumer_id"),
#             "full_name": result.get("consumer_name"),
#             "address": result.get("address"),
#             "mobile": result.get("mobile_number"),
#             "email": result.get("email_address"),
#             "bill_number": result.get("bill_no"),
#             "bill_amount": sanitize_decimal(result.get("bill_amount") or result.get("amount_payable")),
#             "bill_due_date": result.get("bill_due_date") or result.get("dueDate"),
#             "bill_issue_date": result.get("bill_issue_date") or result.get("bill_date"),
#             "bill_status": result.get("status"),
#             "service_provider": result.get("service_provider"),
#             "district": result.get("district"),
#             "operator_code": result.get("operator_code"),
#         }

#     elif vendor_name.lower() == "surepass":
#         return {
#             "client_id": result.get("client_id"),
#             "consumer_id": result.get("customer_id") or result.get("id_number"),
#             "customer_id": result.get("customer_id") or result.get("id_number"),
#             "operator_code": result.get("operator_code"),
#             "state": result.get("state"),
#             "full_name": result.get("full_name"),
#             "address": result.get("address"),
#             "mobile": result.get("mobile"),
#             "email": result.get("user_email"),
#             "bill_number": result.get("bill_number"),
#             "bill_amount": sanitize_decimal(result.get("bill_amount")),
#             "bill_due_date": result.get("bill_due_date"),
#             "bill_issue_date": result.get("bill_issue_date"),
#             "bill_status": result.get("bill_status"),
#             "document_link": result.get("document_link"),
#         }

#     return None

# def sanitize_decimal(value):
#     if value is None:
#         return None
#     if isinstance(value, str):
#         value = value.replace(",", "").strip()
#     try:
#         return Decimal(value)
#     except Exception:
#         return None
    
# def save_bill_data(normalized, created_by):
#     bill_obj = UatElectricityBill.objects.create(
#         client_id=normalized.get("client_id"),
#         consumer_id=normalized.get("consumer_id"),
#         customer_id=normalized.get("customer_id"),
#         service_provider=normalized.get("service_provider"),
#         operator_code=normalized.get("operator_code"),
#         state=normalized.get("state"),
#         district=normalized.get("district"),
#         full_name=normalized.get("full_name"),
#         address=normalized.get("address"),
#         mobile=normalized.get("mobile"),
#         reg_mobile_no=normalized.get("reg_mobile_no"),
#         email=normalized.get("email"),
#         bill_number=normalized.get("bill_number"),
#         bill_amount=sanitize_decimal(normalized.get("bill_amount")),
#         bill_due_date=normalized.get("bill_due_date"),
#         bill_issue_date=normalized.get("bill_issue_date"),
#         bill_status=normalized.get("bill_status"),
#         document_link=normalized.get("document_link"),
#         created_by=created_by,
#     )
#     return bill_obj


import requests
from decimal import Decimal
from decouple import config
from kyc_api_gateway.models import UatElectricityBill
from kyc_api_gateway.utils.constants import VENDOR_BILL_SERVICE_ENDPOINTS

SUREPASS_TOKEN = config("SUREPASS_TOKEN", default=None)
if not SUREPASS_TOKEN:
    raise ValueError("SUREPASS_TOKEN is not set in your environment variables.")



def build_vendor_request(vendor_name, request_data):
    name = vendor_name.lower()

    if name == "karza":
        return {
            "consumer_id": request_data.get("consumer_id"),
            "service_provider": request_data.get("service_provider"),
            "district": request_data.get("district"),
            "regMobileNo": request_data.get("regMobileNo"),
            "consent": {"consent", "Y"},
            "clientData": {"caseId": "123456"},
        }

    if name == "surepass":
        return {
            "id_number": request_data.get("consumer_id"),
            "operator_code": request_data.get("service_provider"),
        }

    return request_data


def call_vendor_api(vendor, request_data, env="uat"):
    vendor_key = vendor.vendor_name.lower()
    endpoint_path = VENDOR_BILL_SERVICE_ENDPOINTS.get(vendor_key)

    print(f"Calling vendor API: {vendor.vendor_name} ({env})")

    if not endpoint_path:
        print(f"[ERROR] Vendor '{vendor.vendor_name}' has no endpoint path configured.")
        return None

    base_url = vendor.end_point_uat if env == "uat" else vendor.end_point_production
    if not base_url:
        print(f"[ERROR] Vendor '{vendor.vendor_name}' has no {env} URL configured.")
        return None

    key = vendor.uat_key if env == "uat" else vendor.production_key
    full_url = f"{base_url.rstrip('/')}/{endpoint_path.lstrip('/')}"

    print(f"Full URL: {full_url}")  

    payload = build_vendor_request(vendor_key, request_data)
    headers = {"Content-Type": "application/json"}

    if vendor_key == "karza":
        headers["x-karza-key"] = key
    elif vendor_key == "surepass":
        headers["Authorization"] = f"Bearer {SUREPASS_TOKEN}" 

    try:
        return requests.post(full_url, json=payload, headers=headers, timeout=vendor.timeout or 30)
    except Exception as e:
        print(f"[ERROR] API call failed for vendor '{vendor.vendor_name}': {str(e)}")
        return None



def normalize_vendor_response(vendor_name, raw_data):
    """Normalize response fields for all vendors."""
    result = raw_data.get("result") or raw_data.get("data") or {}
    if not result:
        return None

    name = vendor_name.lower()

    if name == "karza":
        return {
            "client_id": raw_data.get("request_id"),
            "consumer_id": result.get("consumer_number") or result.get("consumer_id"),
            "customer_id": result.get("consumer_number") or result.get("consumer_id"),
            "full_name": result.get("consumer_name"),
            "address": result.get("address"),
            "mobile": result.get("mobile_number"),
            "email": result.get("email_address"),
            "bill_number": result.get("bill_no"),
            "bill_amount": sanitize_decimal(result.get("bill_amount") or result.get("amount_payable")),
            "bill_due_date": result.get("bill_due_date") or result.get("dueDate"),
            "bill_issue_date": result.get("bill_issue_date") or result.get("bill_date"),
            "bill_status": result.get("status"),
            "service_provider": result.get("service_provider"),
            "district": result.get("district"),
            "operator_code": result.get("operator_code"),
        }

    if name == "surepass":
        return {
            "client_id": result.get("client_id"),
            "consumer_id": result.get("customer_id") or result.get("id_number"),
            "customer_id": result.get("customer_id") or result.get("id_number"),
            "operator_code": result.get("operator_code"),
            "state": result.get("state"),
            "full_name": result.get("full_name"),
            "address": result.get("address"),
            "mobile": result.get("mobile"),
            "email": result.get("user_email"),
            "bill_number": result.get("bill_number"),
            "bill_amount": sanitize_decimal(result.get("bill_amount")),
            "bill_due_date": result.get("bill_due_date"),
            "bill_issue_date": result.get("bill_issue_date"),
            "bill_status": result.get("bill_status"),
            "document_link": result.get("document_link"),
        }

    return None



def sanitize_decimal(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    try:
        return Decimal(value)
    except Exception:
        return None


def save_bill_data(normalized, created_by):
    return UatElectricityBill.objects.create(
        client_id=normalized.get("client_id"),
        consumer_id=normalized.get("consumer_id"),
        customer_id=normalized.get("customer_id"),
        service_provider=normalized.get("service_provider"),
        operator_code=normalized.get("operator_code"),
        state=normalized.get("state"),
        district=normalized.get("district"),
        full_name=normalized.get("full_name"),
        address=normalized.get("address"),
        mobile=normalized.get("mobile"),
        reg_mobile_no=normalized.get("reg_mobile_no"),
        email=normalized.get("email"),
        bill_number=normalized.get("bill_number"),
        bill_amount=sanitize_decimal(normalized.get("bill_amount")),
        bill_due_date=normalized.get("bill_due_date"),
        bill_issue_date=normalized.get("bill_issue_date"),
        bill_status=normalized.get("bill_status"),
        document_link=normalized.get("document_link"),
        created_by=created_by,
    )
