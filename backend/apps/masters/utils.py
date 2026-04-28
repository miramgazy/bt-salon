from apps.accounts.models import User as AppUser
from .models import Master
import random, string

def get_or_create_virtual_master(organization):
    """
    Ensures a Virtual Master exists for the given organization.
    Returns the Master instance.
    """
    virtual_master = Master.objects.filter(organization=organization, is_virtual=True).first()
    
    if virtual_master:
        # Rename if it has the old name
        if virtual_master.user.first_name == "Виртуальный":
            virtual_master.user.first_name = "Очередь"
            virtual_master.user.last_name = ""
            virtual_master.user.save()
        return virtual_master
    
    if not virtual_master:
        # Create the virtual master on the fly
        username = f"v_{organization.id}_{''.join(random.choices(string.ascii_lowercase, k=4))}"
        v_user = AppUser.objects.create(
            username=username, 
            first_name="Очередь", 
            last_name="", 
            organization=organization, 
            role=AppUser.ROLE_MASTER
        )
        virtual_master = Master.objects.create(
            organization=organization, 
            user=v_user, 
            is_virtual=True, 
            color="#FF9C00"
        )
        
        # Assign all existing services to him
        from apps.services.models import Service
        all_services = Service.objects.filter(organization=organization)
        virtual_master.services.set(all_services)
        
    return virtual_master
