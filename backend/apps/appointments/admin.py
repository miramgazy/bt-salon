from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'master', 'service', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'start_time', 'master', 'service')
    date_hierarchy = 'start_time'
    search_fields = ('client__first_name', 'client__phone', 'master__full_name')
