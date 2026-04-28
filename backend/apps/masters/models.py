from django.db import models
from apps.accounts.models import User

class Master(models.Model):
    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, related_name='masters', null=True, blank=True)
    # Master IS a system user. If deleted, master profile is gone.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='master_profile')
    
    # Specific master metadata
    photo = models.ImageField(upload_to='masters/photos/', null=True, blank=True)
    bio = models.TextField(blank=True, help_text="Short bio in Markdown format")
    color = models.CharField(max_length=7, default='#3C50E0', help_text="Hex color code for calendar appointments")
    
    is_active = models.BooleanField(default=True)
    is_virtual = models.BooleanField(default=False)
    services = models.ManyToManyField('services.Service', blank=True)

    def __str__(self):
        return f"Master: {self.user.first_name} {self.user.last_name}"

class MasterShift(models.Model):
    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, related_name='master_shifts')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='shifts')
    date = models.DateField()
    work_start = models.TimeField()
    work_end = models.TimeField()
    lunch_start = models.TimeField(null=True, blank=True)
    lunch_end = models.TimeField(null=True, blank=True)
    is_open = models.BooleanField(default=False)
    opened_by_admin = models.BooleanField(default=False, help_text="True if the shift was manually opened by an administrator")
    
    actual_start = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('master', 'date')
