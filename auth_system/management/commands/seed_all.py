from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = "Run all seed commands in order: user, menu, admin role & permissions"

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write(self.style.NOTICE("Seeding admin user..."))
            call_command('seed_user')
            self.stdout.write(self.style.NOTICE("Seeding menus..."))
            call_command('seed_menu')
            self.stdout.write(self.style.NOTICE("Seeding admin role and permissions..."))
            call_command('seed_admin_role_permission')
            self.stdout.write(self.style.SUCCESS("All seeders executed successfully!"))
        except CommandError as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))