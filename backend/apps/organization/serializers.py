from rest_framework import serializers
from .models import Organization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

from apps.accounts.models import User
from apps.masters.models import Master

class EmployeeSerializer(serializers.ModelSerializer):
    services_detail = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    master_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'master_id', 'first_name', 'last_name', 'phone', 'role', 'is_active', 'color', 'services_detail', 'photo_url', 'telegram_id']

    def get_master_id(self, obj):
        if hasattr(obj, 'master_profile'):
            return obj.master_profile.id
        return None

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
