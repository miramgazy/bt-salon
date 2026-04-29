from rest_framework import serializers
from .models import Organization

class OrganizationSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'address', 'work_start', 'work_end', 'lunch_start',
            'lunch_end', 'has_lunch_break', 'bot_token', 'bot_username', 'tma_name', 
            'instagram_link', 'whatsapp_number', 'greeting_text',
            'design_color', 'logo', 'logo_url', 'slot_duration', 
            'latitude', 'longitude', 'is_reminders_enabled', 
            'reminder_hours_before', 'reminder_template_ru', 'reminder_template_kz'
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None

from apps.accounts.models import User
from apps.masters.models import Master

class EmployeeSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    services_detail = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    master_id = serializers.SerializerMethodField()
    today_shift = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'master_id', 'first_name', 'last_name', 'phone', 'role', 'is_active', 'color', 'services', 'services_detail', 'photo_url', 'telegram_id', 'today_shift']

    def get_today_shift(self, obj):
        if obj.role == 'master' and hasattr(obj, 'master_profile'):
            from django.utils import timezone
            from apps.masters.models import MasterShift
            
            # Use date from context if provided, otherwise default to today
            request = self.context.get('request')
            shift_date_str = None
            if request:
                shift_date_str = request.query_params.get('date')
            
            if shift_date_str:
                from django.utils.dateparse import parse_date
                shift_date = parse_date(shift_date_str)
            else:
                shift_date = timezone.localtime(timezone.now()).date()
            
            if not shift_date:
                shift_date = timezone.localtime(timezone.now()).date()

            shift = MasterShift.objects.filter(
                master=obj.master_profile, 
                date=shift_date
            ).first()
            if shift:
                return {
                    'is_open': shift.is_open,
                    'opened_by_admin': shift.opened_by_admin,
                    'actual_start': shift.actual_start.isoformat() if shift.actual_start else None,
                    'date': str(shift.date)
                }
        return None

    def get_master_id(self, obj):
        if hasattr(obj, 'master_profile'):
            return obj.master_profile.id
        return None

    def get_services(self, obj):
        if hasattr(obj, 'master_profile'):
            return list(obj.master_profile.services.values_list('id', flat=True))
        return []

    def get_services_detail(self, obj):
        if hasattr(obj, 'master_profile'):
            from apps.services.serializers import ServiceSerializer
            return ServiceSerializer(obj.master_profile.services.all(), many=True).data
        return []

    def get_color(self, obj):
        if hasattr(obj, 'master_profile'):
            return obj.master_profile.color
        return '#3C50E0'

    def get_photo_url(self, obj):
        if hasattr(obj, 'master_profile') and obj.master_profile.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.master_profile.photo.url)
            return obj.master_profile.photo.url
        return None
