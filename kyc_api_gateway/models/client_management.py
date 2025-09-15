from django.db import models


class ClientManagement(models.Model):
    company_name = models.CharField(max_length=255)             
    business_type = models.CharField(max_length=255)           
    registration_number = models.CharField(max_length=255, unique=True)  
    tax_id = models.CharField(max_length=20, unique=True)        
    website = models.CharField(max_length=255, unique=True)      
    industry = models.CharField(max_length=255)                  
    name = models.CharField(max_length=255)          
    email = models.EmailField(max_length=255, unique=True)       
    phone = models.CharField(max_length=15, unique=True)         
    position = models.CharField(max_length=255)                  
    account_status = models.CharField(max_length=100)            
    risk_level = models.CharField(max_length=100)               
    compliance_level = models.CharField(max_length=100)          

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "client_management"
        
    def __str__(self):
        return f"{self.company_name} ({self.business_type})"
