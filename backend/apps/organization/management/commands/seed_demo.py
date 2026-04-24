from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.organization.models import Organization
from apps.masters.models import Master, MasterShift
from apps.services.models import Category, Service
from django.utils import timezone
from datetime import time, timedelta

class Command(BaseCommand):
    help = 'Seed database with demo data'

    def handle(self, *args, **kwargs):
        # Admin
        User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True})
        
        # Org
        Organization.objects.get_or_create(name='BT Salon', defaults={
            'address': 'Main Str', 'bot_token': 'dummy'
        })
        
        # Categories
        cat_hair, _ = Category.objects.get_or_create(name='Hair')
        cat_nails, _ = Category.objects.get_or_create(name='Nails')
        
        # Services
        s1, _ = Service.objects.get_or_create(category=cat_hair, name='Standard Haircut', defaults={
            'duration_minutes': 45, 'base_price': 25.0, 'margin_type': 'fixed', 'margin_value': 0
        })
        s2, _ = Service.objects.get_or_create(category=cat_hair, name='Coloring', defaults={
            'duration_minutes': 120, 'base_price': 100.0, 'margin_type': 'percent', 'margin_value': 10
        })
        s3, _ = Service.objects.get_or_create(category=cat_nails, name='Manicure', defaults={
            'duration_minutes': 60, 'base_price': 30.0, 'margin_type': 'fixed', 'margin_value': 5
        })

        # Masters
        for i in range(1, 4):
            u, _ = User.objects.get_or_create(username=f'master_{i}')
            m, created = Master.objects.get_or_create(user=u, full_name=f'Master {i}')
            if created:
                m.services.add(s1, s2, s3)
            
            # shifts for today
            MasterShift.objects.get_or_create(
                master=m, date=timezone.now().date(),
                defaults={
                    'work_start': time(9, 0),
                    'work_end': time(20, 0),
                    'lunch_start': time(13, 0),
                    'lunch_end': time(14, 0),
                    'is_open': True
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data'))
