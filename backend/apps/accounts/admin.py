from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'language', 'is_bot_subscribed', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'language')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('role', 'telegram_id', 'organization')}),
        ('Onboarding', {'fields': ('phone', 'language', 'is_bot_subscribed')}),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
