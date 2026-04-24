from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    master_detail = serializers.SerializerMethodField()
    service_detail = serializers.SerializerMethodField()
    client_detail = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['organization', 'client', 'shift']

    def get_client_detail(self, obj):
        if not obj.client:
            return None
        return {
            'id': obj.client.id,
            'full_name': obj.client.full_name,
            'phone': obj.client.phone,
        }

    def get_master_detail(self, obj):
        if not obj.master:
            return None
        user = obj.master.user
        return {
            'id': obj.master.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'color': obj.master.color,
            'photo_url': obj.master.photo.url if obj.master.photo else None,
        }

    def get_service_detail(self, obj):
        if not obj.service:
            return None
        return {
            'id': obj.service.id,
            'name': obj.service.name,
            'duration_minutes': obj.service.duration_minutes,
            'total_price': obj.service.total_price,
        }

    def validate(self, data):
        master = data.get('master')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        pk = self.instance.pk if self.instance else None

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Время окончания должно быть позже времени начала")

        if master and start_time and end_time:
            request = self.context.get('request')
            overlaps = Appointment.objects.filter(
                master=master,
                status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
            )
            if request and hasattr(request.user, 'organization') and request.user.organization:
                overlaps = overlaps.filter(organization=request.user.organization)
            if pk:
                overlaps = overlaps.exclude(pk=pk)

            for appt in overlaps:
                if start_time < appt.end_time and end_time > appt.start_time:
                    raise serializers.ValidationError("Это время уже занято другой записью")
                    
        return data
