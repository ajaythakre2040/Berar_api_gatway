from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class PasswordResetLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, null=True, blank=True)
    action = models.CharField(
        max_length=50
    )  # forgot_password_requested, change_password
    timestamp = models.DateTimeField(default=timezone.now)
    successful = models.BooleanField(default=False)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.email} - {self.action} - {self.timestamp}"
