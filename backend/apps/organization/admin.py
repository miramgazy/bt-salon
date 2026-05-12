from django.contrib import admin
import uuid
from .models import Organization
from apps.payments.kaspi_service import KaspiPayService
from django.contrib import messages

from django.utils.html import format_html

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'bot_username', 'tma_name', 'work_start', 'work_end')
    search_fields = ('name', 'address', 'bot_username')
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly.extend(['kaspi_api_key', 'kaspi_device_token'])
        readonly.extend(['kaspi_status', 'tma_link'])
        return readonly

    def kaspi_api_key_display(self, obj):
        if not obj.kaspi_api_key:
            return "Не установлен"
        # Mask if not superuser
        # Note: This is for list_display or custom field, but for detail view we need to handle it differently
        # since it's a field in fieldsets.
        val = obj.kaspi_api_key
        return f"{val[:5]}****{val[-4:]}" if len(val) > 10 else "********"
    
    # Actually, for detail view, if it's read-only, it uses the display value.
    # I'll add these as properties or custom methods.

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
        ('Kaspi Pay Integration (QR)', {
            'fields': ('is_prepayment_enabled', 'kaspi_api_key', 'kaspi_device_token', 'kaspi_status'),
            'description': 'Only Superusers can edit API keys. Device token is generated automatically on save if API key is provided.'
        }),
        ('TMA Appearance', {
            'fields': ('greeting_text', 'design_color', 'logo', 'instagram_link', 'whatsapp_number'),
        }),
    )

    def kaspi_status(self, obj):
        if obj.kaspi_device_token:
            return format_html('<span style="color: green; font-weight: bold;">✅ Активен (Устройство зарегистрировано)</span>')
        if obj.kaspi_api_key:
            return format_html('<span style="color: orange; font-weight: bold;">⚠️ Ключ установлен, но устройство не зарегистрировано</span>')
        return "Не настроено"
    kaspi_status.short_description = "Статус Kaspi"

    def save_model(self, request, obj, form, change):
        # Trigger Kaspi device registration if API key is provided but no token exists
        if obj.kaspi_api_key and not obj.kaspi_device_token:
            service = KaspiPayService(obj.kaspi_api_key)
            trade_points = service.get_trade_points()
            
            if trade_points and len(trade_points) > 0:
                # Use the first trade point for registration
                tp_id = trade_points[0].get('TradePointId')
                device_id = f"VIRTUAL_{obj.id}_{uuid.uuid4().hex[:8]}"
                token = service.register_device(device_id, tp_id)
                
                if token:
                    obj.kaspi_device_token = token
                    messages.success(request, f"Устройство Kaspi успешно зарегистрировано для торговой точки: {trade_points[0].get('TradePointName')}")
                else:
                    messages.error(request, "Ошибка при регистрации устройства в Kaspi. Проверьте ApiKey.")
            else:
                messages.error(request, "Не удалось получить список торговых точек Kaspi. Проверьте ApiKey.")
        
        super().save_model(request, obj, form, change)

    def tma_link(self, obj):
        if obj.bot_username and obj.tma_name:
            link = f"https://t.me/{obj.bot_username}/{obj.tma_name}?startapp={obj.id}"
            return format_html('<a href="{}" target="_blank" style="font-weight:bold; color:#c9a84c;">{}</a>', link, link)
        return "Укажите имя бота и приложения для генерации ссылки"
    tma_link.short_description = "Ссылка на Mini App"
