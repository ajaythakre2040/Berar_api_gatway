import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TelecomService:

    def telecom_otp(mobile_no):
        if not TelecomService._validate_mobile(mobile_no):
            return {"success": False, "error": "Invalid mobile number"}

        url = f"{settings.KYC_API_BASE}/generate-otp"
        headers = TelecomService._aadhaar_headers()
        payload = {"id_number": mobile_no}


        return TelecomService._post(url, payload, headers)
    
    def telecom_submit(client_id, otp):
        if not client_id or not otp:
            return {"success": False, "error": "Client ID and OTP are required"}

        url = f"{settings.KYC_API_BASE}/submit-otp"
        headers = TelecomService._aadhaar_headers()
        payload = {"client_id": client_id, "otp": otp}
        return TelecomService._post(url, payload, headers)

    def karza_send_otp(mobile_no):
        if not TelecomService._validate_mobile(mobile_no):
            return {"success": False, "error": "Invalid mobile number"}

        url = f"{settings.KARZA_API_BASE}/otp"
        headers = TelecomService._karza_headers()
        payload = {
            "mobile": mobile_no,
            "consent": "y",
            "clientData": {"caseId": "123456"}  # TODO: make configurable
        }
        return TelecomService._post(url, payload, headers)

    def karza_submit_otp(request_id, otp):
        if not request_id or not otp:
            return {"success": False, "error": "Request ID and OTP are required"}

        url = f"{settings.KARZA_API_BASE}/status"
        headers = TelecomService._karza_headers()
        payload = {
            "otp": otp,
            "request_id": request_id,
            "clientData": {"caseId": "123456"}
        }
        return TelecomService._post(url, payload, headers)

    def karza_get_details(request_id):
        if not request_id:
            return {"success": False, "error": "Request ID is required"}

        url = f"{settings.KARZA_API_BASE}/details"
        headers = TelecomService._karza_headers()
        payload = {
            "request_id": request_id,
            "clientData": {"caseId": "123456"}
        }
        return TelecomService._post(url, payload, headers)
    

    def send_sms_otp(mobile_number, otp):
        if not TelecomService._validate_mobile(mobile_number):
            return {"success": False, "error": "Invalid mobile number"}

        url = settings.PINNACLE_SMS_URL
        headers = {
            "apikey": settings.API_SMS_KEY,
            "Content-Type": "application/json",
        }

        message = {
            "sender": "berarf",  # TODO: make configurable
            "message": [{
                "number": f"91{mobile_number}",
                "text": (
                    f"Dear User, Use this One Time Password: {otp} to verify your mobile number.\n"
                    f"It is valid for the next 3 Minutes. Thank You Berar Finance Limited"
                )
            }],
            "messagetype": "TXT",
            "dlttempid": "1707170659123947276"  # TODO: make configurable
        }

        return TelecomService._post(url, message, headers)

    # --- Internal Helpers ---

    def _post(url, payload, headers):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed: {e}")
            return {"success": False, "error": str(e)}

    def _aadhaar_headers():
        return {
            "Authorization": f"Bearer {settings.API_SAND_KEY}",
            "Content-Type": "application/json",
        }

    def _karza_headers():
        return {
            "x-karza-key": settings.API_KARZA_KEY,
            "Content-Type": "application/json",
        }

    def _validate_mobile(mobile):
        """Returns True if the mobile is a valid Indian mobile number."""
        return (
            isinstance(mobile, str)
            and len(mobile) == 10
            and mobile.isdigit()
            and mobile.startswith(("6", "7", "8", "9"))
        )
