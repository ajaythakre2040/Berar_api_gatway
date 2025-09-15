from django.core.management.base import BaseCommand
from auth_system.models.user import TblUser
from django.utils import timezone
from constant import ADMIN_USER


class Command(BaseCommand):
    help = "Seed the admin user into the database"

    def handle(self, *args, **kwargs):
        email = ADMIN_USER["email"]
        password = ADMIN_USER["password"]
        if TblUser.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"Admin already exists: {email}"))
        else:
            TblUser.objects.create_superuser(
                full_name=ADMIN_USER["full_name"],
                email=ADMIN_USER["email"],
                mobile_number=ADMIN_USER["mobile_number"],
                password=ADMIN_USER["password"],
                created_at=timezone.now(),
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Admin user created\n📧 Email: {email}\n🔑 Password: {password}"
                )
            )
