from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MasterShift, Master

@receiver(post_save, sender=MasterShift)
def ensure_virtual_shift(sender, instance, created, **kwargs):
    """
    Ensures that when any shift is opened for a real master, 
    the virtual master also has an open shift on that date.
    """
    # 1. Skip if the shift belongs to a virtual master to avoid recursion
    if instance.master.is_virtual:
        return

    # 2. Only act if the shift is being opened
    if instance.is_open:
        org = instance.organization
        from .utils import get_or_create_virtual_master
        virtual_master = get_or_create_virtual_master(org)
        
        # 3. We use get_or_create to find or create the virtual shift
        v_shift, created_v = MasterShift.objects.get_or_create(
            organization=org,
            master=virtual_master,
            date=instance.date,
            defaults={
                'work_start': org.work_start or '09:00',
                'work_end': org.work_end or '21:00',
                'is_open': True,
                'opened_by_admin': True
            }
        )
        
        # 4. If shift existed but was closed, open it
        if not created_v and not v_shift.is_open:
            v_shift.is_open = True
            v_shift.save(update_fields=['is_open'])
