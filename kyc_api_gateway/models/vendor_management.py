from django.db import models


class VendorManagement(models.Model):
    display_name = models.CharField(max_length=255)               
    internal_name = models.CharField(max_length=255)              
    base_url = models.CharField(max_length=255, unique=True)  

    contact_email = models.EmailField(max_length=255, unique=True) 
    priority = models.CharField(max_length=100)                     
    timeout = models.IntegerField(default=30)                       
    max_retries = models.IntegerField(default=3)                    
    status = models.CharField(max_length=50, default="Active")      

    api_key = models.CharField(max_length=255, unique=True)         
    secret_key = models.CharField(max_length=255)                  
    pricing_model = models.CharField(max_length=100)                
    cost_per_request = models.DecimalField(max_digits=10, decimal_places=2)  
    currency = models.CharField(max_length=50, default="INR")      

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "vendor_management"

    def __str__(self):
        return f"{self.display_name} ({self.internal_name})"
