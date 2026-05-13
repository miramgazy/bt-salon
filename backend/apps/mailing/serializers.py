from rest_framework import serializers
from .models import MailingTask


class MailingTaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    audience_display = serializers.CharField(source='get_audience_type_display', read_only=True)

    class Meta:
        model = MailingTask
        fields = [
            'id',
            'title',
            'message_ru',
            'message_kz',
            'scheduled_at',
            'audience_type',
            'audience_display',
            'status',
            'status_display',
            'total_recipients',
            'sent_success',
            'failed_count',
            'unsubscribed_count',
            'created_at'
        ]
        read_only_fields = [
            'status',
            'total_recipients',
            'sent_success',
            'failed_count',
            'unsubscribed_count',
            'created_at'
        ]

    def validate(self, data):
        # Проверяем, что оба текста заполнены
        if not data.get('message_ru') or not data.get('message_ru').strip():
            raise serializers.ValidationError({'message_ru': 'Текст на русском языке обязателен.'})
        if not data.get('message_kz') or not data.get('message_kz').strip():
            raise serializers.ValidationError({'message_kz': 'Текст на казахском языке обязателен.'})
        return data
