from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.services.models import Service
from apps.masters.models import Master

@receiver(post_save, sender=Service)
def assign_service_to_virtual_master(sender, instance, created, **kwargs):
    """
    Automatically assign new services to the Virtual Master of the same organization.
    Ensures Virtual Master exists.
    """
    if created and instance.organization:
        org = instance.organization
        from apps.masters.utils import get_or_create_virtual_master
        virtual_master = get_or_create_virtual_master(org)
        
        virtual_master.services.add(instance)

@receiver(post_save, sender=Master)
def assign_all_services_to_new_virtual_master(sender, instance, created, **kwargs):
    """
    When a new Virtual Master is created, assign all existing services of the organization to it.
    """
    if created and instance.is_virtual and instance.organization:
        all_services = Service.objects.filter(organization=instance.organization)
        instance.services.set(all_services)
