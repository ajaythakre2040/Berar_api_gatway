
import random
import string
import base64

def generate_otp(length=6):
    return "".join(random.choices(string.digits, k=length))

def generate_client_id(prefix, otp):
    encoded = base64.urlsafe_b64encode(str(otp).encode()).decode().rstrip("=")
    return f"{prefix}_{encoded}"