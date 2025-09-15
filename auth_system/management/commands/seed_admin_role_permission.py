from django.core.management.base import BaseCommand
from django.utils import timezone
from auth_system.models.role import Role
from auth_system.models.role_permission import RolePermission
from auth_system.models.menus import Menu
from auth_system.models.user import TblUser

class Command(BaseCommand):
    help = "Seed the admin role and permissions for all menus"

    def handle(self, *args, **kwargs):
        # Get admin user (assumes [seed_user.py](http://_vscodecontentref_/2) has already run)
        admin_user = TblUser.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR("Admin user not found. Please run seed_user first."))
            return

        # Create admin role if not exists
        admin_role, created = Role.objects.get_or_create(
            role_name="Admin",
            defaults={
                "level": 1,
                "description": "Administrator role with all permissions",
                "role_code": "ADMIN",
                "created_by": admin_user.id,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✅ Admin role created"))
        else:
            self.stdout.write(self.style.WARNING("Admin role already exists"))

        # Assign all permissions for all menus to admin role
        menus = Menu.objects.filter(deleted_at__isnull=True)
        for menu in menus:
            perm, created = RolePermission.objects.get_or_create(
                role=admin_role,
                menu_id=menu,
                defaults={
                    "view": True,
                    "add": True,
                    "edit": True,
                    "delete": True,
                    "print": True,
                    "export": True,
                    "sms_send": True,
                    "api_limit": "",
                    "created_by": admin_user.id,
                    "created_at": timezone.now(),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Permission added for menu: {menu.menu_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Permission already exists for menu: {menu.menu_name}"))