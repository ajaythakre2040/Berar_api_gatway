from django.db import models


class PanDetails(models.Model):
    # 🔹 Vendor metadata
    request_id = models.CharField(max_length=100, null=True, blank=True)
    client_id = models.CharField(
        max_length=100, null=True, blank=True
    )  # vendor2 specific

    # 🔹 PAN and Name Information
    pan_number = models.CharField(max_length=10, unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    # full_name = models.JSONField(null=True, blank=True)  # Vendor 2

    # 🔹 Aadhaar related
    aadhaar_linked = models.BooleanField(null=True)
    masked_aadhaar = models.CharField(max_length=20, null=True, blank=True)
    aadhaar_match = models.BooleanField(null=True)

    # 🔹 Date of Birth
    dob = models.DateField(null=True, blank=True)
   
    dob_verified = models.BooleanField(null=True)
    dob_check = models.BooleanField(null=True)

    # 🔹 Gender
    gender = models.CharField(max_length=10, null=True, blank=True)

    # 🔹 Contact Info
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    # 🔹 PAN Status and Professional Info
    pan_status = models.CharField(max_length=50, null=True, blank=True)
    is_salaried = models.BooleanField(null=True)
    is_director = models.BooleanField(null=True)
    is_sole_prop = models.BooleanField(null=True)
    issue_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)  # person/company
    less_info = models.BooleanField(null=True)

    # 🔹 Profile match and extra data
    profile_match = models.JSONField(null=True, blank=True)

    # 🔹 Address Info
    address_line_1 = models.CharField(
        max_length=255, null=True, blank=True
    )  # line_1 or building name
    address_line_2 = models.CharField(
        max_length=255, null=True, blank=True
    )  # line_2 or locality
    street_name = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    pin_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=100, default="INDIA")
    full_address = models.TextField(null=True, blank=True)

    # 🔹 Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    created_by = models.IntegerField()

    class Meta:
        db_table = "kyc_pan_details"  # ✅ Table name

    def __str__(self):
        return f"{self.pan_number} - {self.full_name or ''}"
