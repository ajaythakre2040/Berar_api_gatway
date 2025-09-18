from django.db import migrations
class Migration(migrations.Migration):
    dependencies = [
        ('kyc_api_gateway', '0001_initial'),
    ]
    operations = [
        migrations.DeleteModel(
            name='RoleManagement',
        ),
    ]