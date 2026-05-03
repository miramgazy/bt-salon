from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Appointment

@receiver(post_save, sender=Appointment)
def broadcast_appointment_update(sender, instance, created, **kwargs):
    """
    Broadcasts appointment updates to the organization group via WebSocket.
    """
    if not instance.organization:
        return
        
    channel_layer = get_channel_layer()
    group_name = f'org_{instance.organization.id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'appointment_update',
            'action': 'created' if created else 'updated',
            'appointment_id': instance.id,
            'status': instance.status,
            'client_confirmation': instance.client_confirmation
        }
    )
