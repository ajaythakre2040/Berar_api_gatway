from django.db import models


class UserManagement(models.Model):
    first_name = models.CharField(max_length=255)   
    last_name = models.CharField(max_length=255)   
    email = models.EmailField(max_length=255, unique=True)  
    phone = models.CharField(max_length=20, unique=True)   
    username = models.CharField(max_length=255, unique=True) 
    role = models.CharField(max_length=255)        
    status = models.CharField(max_length=50)        
    session_timeout = models.IntegerField(default=30)  
    department = models.CharField(max_length=255)   
    position = models.CharField(max_length=255)  
      

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "user_management"
