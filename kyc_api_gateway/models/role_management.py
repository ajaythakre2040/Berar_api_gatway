from django.db import models


class RoleManagement(models.Model):
    role_name  = models.CharField(max_length=255, unique=True)
    access_level   = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True) 
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_by = models.IntegerField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "role_management"  # This will be the table name in the DB
        