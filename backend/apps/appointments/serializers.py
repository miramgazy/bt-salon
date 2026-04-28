from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    master_detail = serializers.SerializerMethodField()
    service_detail = serializers.SerializerMethodField()
    client_detail = serializers.SerializerMethodField()
    is_combo = serializers.SerializerMethodField()
    display_title = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = [
            'organization', 'client', 'shift', 'parent', 'appointment_type',
            'master_net_income', 'salon_net_income', 'is_overflow', 'display_title', 'is_combo'
        ]

    def get_is_combo(self, obj):
        return obj.appointment_type in [Appointment.TYPE_COMBO_MASTER, Appointment.TYPE_COMBO_SUB]

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
        # Use appointment's total_price if set, otherwise fallback to service's total_price
        price = obj.total_price if obj.total_price > 0 else obj.service.total_price
        return {
            'id': obj.service.id,
            'name': obj.service.name,
            'duration_minutes': obj.service.duration_minutes,
            'total_price': price,
        }

    def get_display_title(self, obj):
        if obj.appointment_type == 'combo_master':
            # Collect all masters involved in the combo
            masters = [obj.master.user.first_name]
            for child in obj.children.all():
                if child.master and child.master.user:
                    masters.append(child.master.user.first_name)
            
            unique_masters = sorted(list(set(masters)))
            masters_str = " + ".join(unique_masters)
            return f"{obj.service.name} ({masters_str})"
            
        elif obj.appointment_type == 'combo_sub':
            parent_name = obj.parent.service.name if obj.parent else "Комбо"
            return f"{parent_name}: {obj.service.name}"
            
        return obj.service.name

    def validate(self, data):
        master = data.get('master')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        pk = self.instance.pk if self.instance else None

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Время окончания должно быть позже времени начала")

        if master and not master.is_virtual:
            service = data.get('service') or (self.instance.service if self.instance else None)
            if service and not master.services.filter(pk=service.pk).exists():
                raise serializers.ValidationError(f"Мастер {master.user.first_name} не оказывает услугу {service.name}")

            if start_time and end_time:
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
