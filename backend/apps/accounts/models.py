from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_SUPERADMIN = 'superadmin'
    ROLE_ADMIN = 'admin'
    ROLE_OWNER = 'owner'
    ROLE_MASTER = 'master'
    ROLE_CLIENT = 'client'
    ROLES = [
        (ROLE_SUPERADMIN, 'Суперадмин'), 
        (ROLE_ADMIN, 'Администратор'),
        (ROLE_OWNER, 'Владелец'),
        (ROLE_MASTER, 'Мастер'),
        (ROLE_CLIENT, 'Клиент')
    ]
    role = models.CharField(max_length=20, choices=ROLES, default=ROLE_CLIENT)
    telegram_id = models.BigIntegerField(null=True, blank=True)
    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='users')

    # Onboarding fields
    phone = models.CharField(max_length=20, blank=True, default='')
    language = models.CharField(max_length=10, blank=True, default='ru', help_text='Preferred UI language code (ru/kz)')
    is_bot_subscribed = models.BooleanField(null=True, blank=True, help_text='Has user consented to bot notifications')
    bot_sync_uuid = models.UUIDField(null=True, blank=True, unique=True, help_text='Used to pair bot interactions with this user')

    class Meta:
        unique_together = ('organization', 'telegram_id')
