from django.db import models
from django.utils import timezone


class VendorManagement(models.Model):

    vendor_name = models.CharField(max_length=255, unique=True)
    header_key_name = models.CharField(max_length=255, unique=True)
    uat_base_url = models.CharField(max_length=255, unique=True)
    uat_api_key = models.CharField(max_length=255, unique=True)
    prod_base_url = models.CharField(max_length=255,unique=True,blank=True, null=True)
    prod_api_key = models.CharField(max_length=255,unique=True,blank=True, null=True)
    contact_phone = models.CharField(max_length=10,blank=True, null=True,unique=True)
    contact_email = models.EmailField(max_length=255,unique=True,blank=True, null=True)
    status = models.BooleanField(default=False)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)git

    class Meta:
        db_table = "kyc_vendor_management"

    def __str__(self):
        return self.vendor_name

    # Optional: Soft delete method
    def soft_delete(self, user_id):
        self.deleted_at = timezone.now()
        self.deleted_by = user_id
        self.save()

    # Optional: Check if vendor is active (not deleted and status active)
    @property
    def is_active(self):
        return self.status.lower() == "active" and self.deleted_at is None
