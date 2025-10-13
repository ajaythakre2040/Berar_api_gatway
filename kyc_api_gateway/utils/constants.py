from django.db import models
VENDOR_SERVICE_ENDPOINTS = {
    "karza": "v3/pan-profile",
    "surepass": "api/v1/pan/pan-comprehensive",
}

VENDOR_BILL_SERVICE_ENDPOINTS = {
    "karza": "v2/elec",
    "surepass": "api/v1/utility/electricity/",
}

VENDOR_NAME_SERVICE_ENDPOINTS = {
    "karza": "v3/name",
    "surepass": "api/v1/utils/name-matching/",
}

VENDOR_VOTER_SERVICE_ENDPOINTS = {
    "karza": {
        "uat": "v3/voter",
        "prod": "v3/voter",
    },
    "surepass": {
        "uat": "api/v1/voter-id/voter-id",
        "prod": "api/v1/voter-id/voter-id",
    },
}

VENDOR_RC_SERVICE_ENDPOINTS = {
    
    "karza": "v2/rc-basic",
    "surepass": "/api/v1/rc/rc-full",
}

DEFAULT_COUNTRY = "India"