from rest_framework import serializers
from .models import Category, Service, ComboItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['organization']

class ComboItemSerializer(serializers.ModelSerializer):
    sub_service_name = serializers.CharField(source='sub_service.name', read_only=True)
    sub_service_price = serializers.DecimalField(source='sub_service.total_price', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = ComboItem
        fields = ['id', 'sub_service', 'sub_service_name', 'sub_service_price', 'quantity', 'is_main']

class ServiceSerializer(serializers.ModelSerializer):
    combo_items = ComboItemSerializer(many=True, read_only=True)
    sub_services = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )
    
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['organization']

    def validate(self, data):
        if data.get('is_combo'):
            sub_services = data.get('sub_services', [])
            if not sub_services:
                # If it's an update and sub_services is not provided, 
                # we should check existing combo items.
                if self.instance and not self.instance.combo_items.exists():
                    raise serializers.ValidationError("Комбо-услуга должна содержать хотя бы одну под-услугу.")
            else:
                main_count = sum(1 for item in sub_services if item.get('is_main'))
                if main_count != 1:
                    raise serializers.ValidationError("В комбо-услуге должна быть выбрана ровно одна главная услуга.")
        return data

    def create(self, validated_data):
        sub_services_data = validated_data.pop('sub_services', [])
        service = super().create(validated_data)
        if service.is_combo:
            for item in sub_services_data:
                ComboItem.objects.create(
                    service=service, 
                    sub_service_id=item.get('sub_service'),
                    quantity=item.get('quantity', 1),
                    is_main=item.get('is_main', False)
                )
        return service

    def update(self, instance, validated_data):
        sub_services_data = validated_data.pop('sub_services', None)
        instance = super().update(instance, validated_data)
        if sub_services_data is not None and instance.is_combo:
            instance.combo_items.all().delete()
            for item in sub_services_data:
                ComboItem.objects.create(
                    service=instance, 
                    sub_service_id=item.get('sub_service'),
                    quantity=item.get('quantity', 1),
                    is_main=item.get('is_main', False)
                )
        return instance
