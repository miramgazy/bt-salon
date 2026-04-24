from django.db import models
from apps.accounts.models import User

class Client(models.Model):
    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, related_name='clients', null=True, blank=True)
    # Link to registered user (TMA users). Optional for offline clients.
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='client_profile')
    
    # These fields are required for everyone (Offline clients store them here, 
    # Online clients sync them from User or we keep them for quick access)
    phone = models.CharField(max_length=20)
    full_name = models.CharField(max_length=255, blank=True)
    
    # Metadata
    telegram_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('organization', 'phone'), ('organization', 'telegram_id'))

    def __str__(self):
        return f"Client: {self.full_name} ({self.phone})"
