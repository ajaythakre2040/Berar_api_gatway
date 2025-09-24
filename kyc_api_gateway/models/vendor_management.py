from django.db import models


class VendorManagement(models.Model):
    vendor_name = models.CharField(max_length=255,unique=True)               
    base_url = models.CharField(max_length=255, unique=True)  
    contact_email = models.EmailField(max_length=255, unique=True) 
    priority = models.CharField(max_length=100, unique=True)
    timeout = models.IntegerField(default=30)                       
    api_key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=50, default="Active")# true false ya active
     
    end_point_production = models.CharField(max_length=255, null=True, blank=True)
    end_point_uat = models.CharField(max_length=255, null=True, blank=True)
    production_key = models.CharField(max_length=255, null=True, blank=True)
    uat_key = models.CharField(max_length=255, null=True, blank=True)

    internal_name = models.CharField(max_length=255,unique=True)              
    max_retries = models.IntegerField(default=3)    
    error_rate = models.FloatField(default=0.0)
    health_score = models.FloatField(default=0.0)
    response_time = models.FloatField(default=0.0)
    downtime = models.FloatField(default=0.0)
    secret_key = models.CharField(max_length=255, unique=True, null=True, blank=True)              


    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.IntegerField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "vendor_management"

    def __str__(self):
        return f"{self.vendor_name} ({self.internal_name})"
