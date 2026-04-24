from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    is_tma = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['id', 'organization', 'user', 'phone', 'full_name', 'telegram_id', 'is_tma', 'created_at']
        read_only_fields = ['organization', 'is_tma']

    def get_is_tma(self, obj):
        return obj.user is not None

    def create(self, validated_data):
        # organization is already in validated_data from perform_create
        return super().create(validated_data)
