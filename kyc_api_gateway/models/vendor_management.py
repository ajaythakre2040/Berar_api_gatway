from django.db import models
from django.utils import timezone


class VendorManagement(models.Model):
    vendor_name = models.CharField(max_length=255, unique=True)
    base_url = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField(max_length=255, unique=True)
    priority = models.IntegerField(default=30, unique=True)
    timeout = models.IntegerField(default=30)
    max_retries = models.IntegerField(default=3)
    api_key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    secret_key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=50, default="Active")

    error_rate = models.FloatField(default=0.0)
    response_time = models.FloatField(default=0.0)
    downtime = models.FloatField(default=0.0)
    health_score = models.FloatField(default=0.0)

    end_point_production = models.CharField(max_length=255, null=True, blank=True)
    end_point_uat = models.CharField(max_length=255, null=True, blank=True)
    production_key = models.CharField(max_length=255, null=True, blank=True)
    uat_key = models.CharField(max_length=255, null=True, blank=True)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "kyc_vendor_management"
        ordering = ["priority"]  # default ordering by priority

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
