from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Organization
from apps.masters.models import Master
from apps.accounts.models import User
import random
import string

@receiver(post_save, sender=Organization)
def create_virtual_master(sender, instance, created, **kwargs):
    if created:
        # Create a system user for the virtual master
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        username = f"virtual_{instance.id}_{random_suffix}"
        user = User.objects.create(
            username=username,
            first_name="Очередь",
            last_name="/ Свободный мастер",
            role=User.ROLE_MASTER,
            organization=instance
        )
        
        Master.objects.create(
            organization=instance,
            user=user,
            is_virtual=True,
            color="#FF9C00" # Orange color as requested
        )
