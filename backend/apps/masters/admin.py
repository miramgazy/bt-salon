from django.contrib import admin
from .models import Master, MasterShift

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_first_name', 'get_last_name', 'get_phone', 'is_active', 'organization')
    search_fields = ('user__first_name', 'user__last_name', 'user__phone')
    filter_horizontal = ('services',)

    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else ""
    get_first_name.short_description = 'Имя'

    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else ""
    get_last_name.short_description = 'Фамилия'
    
    def get_phone(self, obj):
        return obj.user.phone if obj.user else ""
    get_phone.short_description = 'Телефон'

@admin.register(MasterShift)
class MasterShiftAdmin(admin.ModelAdmin):
    list_display = ('master', 'date', 'work_start', 'work_end', 'is_open')
    list_filter = ('master', 'date', 'is_open')
    date_hierarchy = 'date'
    search_fields = ('master__user__first_name', 'master__user__last_name')
