from django.contrib import admin
from .models import Organization

from django.utils.html import format_html

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'bot_username', 'tma_name', 'work_start', 'work_end')
    search_fields = ('name', 'address', 'bot_username')
    readonly_fields = ('tma_link',)
    
    fieldsets = (
        ('General Info', {
            'fields': ('name', 'address', 'latitude', 'longitude')
        }),
        ('Work Hours', {
            'fields': ('work_start', 'work_end', 'lunch_start', 'lunch_end')
        }),
        ('Telegram Bot Settings', {
            'fields': ('bot_token', 'bot_username', 'tma_name', 'tma_link'),
            'description': 'Configure your Telegram Bot and Mini App details here.'
        }),
        ('TMA Appearance', {
            'fields': ('greeting_text', 'design_color', 'logo', 'instagram_link', 'whatsapp_number'),
        }),
    )

    def tma_link(self, obj):
        if obj.bot_username and obj.tma_name:
            link = f"https://t.me/{obj.bot_username}/{obj.tma_name}?startapp={obj.id}"
            return format_html('<a href="{}" target="_blank" style="font-weight:bold; color:#c9a84c;">{}</a>', link, link)
        return "Укажите имя бота и приложения для генерации ссылки"
    tma_link.short_description = "Ссылка на Mini App"
