from django.db import migrations

def seed_categories(apps, schema_editor):
    ExpenseCategory = apps.get_model('expenses', 'ExpenseCategory')
    try:
        Organization = apps.get_model('organization', 'Organization')
        
        categories = ["Аренда", "Расходники", "Ком услуга", "Хоз товары"]
        
        # We should add these to all organizations
        for org in Organization.objects.all():
            for name in categories:
                ExpenseCategory.objects.get_or_create(organization=org, name=name)
    except LookupError:
        # If Organization model is not found in apps.get_model, we skip (should not happen normally)
        pass

def reverse_seed(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_seed),
    ]
