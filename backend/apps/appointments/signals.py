from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Appointment
from .notifications import (
    notify_master_new_appointment, 
    notify_master_appointment_updated, 
    notify_master_appointment_cancelled
)

@receiver(pre_save, sender=Appointment)
def track_appointment_changes(sender, instance, **kwargs):
    """
    Stores old values to detect changes in post_save.
    """
    if instance.id:
        try:
            old_instance = Appointment.objects.get(id=instance.id)
            instance._old_master_id = old_instance.master_id
            instance._old_start_time = old_instance.start_time
            instance._old_status = old_instance.status
        except Appointment.DoesNotExist:
            instance._old_master_id = None
            instance._old_start_time = None
            instance._old_status = None
    else:
        instance._old_master_id = None
        instance._old_start_time = None
        instance._old_status = None

@receiver(post_save, sender=Appointment)
def broadcast_appointment_update(sender, instance, created, **kwargs):
    """
    Broadcasts appointment updates to the organization group via WebSocket
    AND notifies masters about changes via Telegram.
    """
    if not instance.organization:
        return
        
    # 1. WebSocket Broadcast
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

    # 2. Master Notifications
    if created:
        # New appointment notification
        notify_master_new_appointment(instance)
    else:
        # Check if master changed
        if instance._old_master_id and instance.master_id != instance._old_master_id:
            # Notify old master about removal
            from apps.masters.models import Master
            try:
                old_master = Master.objects.get(id=instance._old_master_id)
                notify_master_appointment_cancelled(instance, master=old_master)
            except Master.DoesNotExist:
                pass
            
            # Notify new master about new assignment
            notify_master_new_appointment(instance)
            
        # Check if time changed (but master same)
        elif instance._old_start_time and instance.start_time != instance._old_start_time:
            notify_master_appointment_updated(instance)
            
        # Check if cancelled
        elif instance._old_status and instance.status != instance._old_status:
            if instance.status == Appointment.STATUS_CANCELLED:
                notify_master_appointment_cancelled(instance)
