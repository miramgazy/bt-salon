from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MailingTask
from .serializers import MailingTaskSerializer
from .selectors import get_mailing_recipients_queryset
from .utils import send_telegram_mailing_message


class MailingTaskViewSet(viewsets.ModelViewSet):
    serializer_class = MailingTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ограничиваем доступ только рассылками текущей организации
        user = self.request.user
        if not user.organization:
            return MailingTask.objects.none()
        return MailingTask.objects.filter(organization=user.organization)

    def perform_create(self, serializer):
        # Автоматически привязываем организацию авторизованного пользователя
        serializer.save(organization=self.request.user.organization, status=MailingTask.STATUS_SCHEDULED)

    @action(detail=False, methods=['get'])
    def count_recipients(self, request):
        """
        Прекалькуляция размера целевой аудитории для выбранного сегмента.
        """
        user = request.user
        if not user.organization:
            return Response({'count': 0})

        audience_type = request.query_params.get('audience_type', MailingTask.AUDIENCE_ALL)
        qs = get_mailing_recipients_queryset(user.organization, audience_type)
        return Response({'count': qs.count()})

    @action(detail=True, methods=['post'])
    def send_test(self, request, pk=None):
        """
        Отправка тестового сообщения напрямую указанному пользователю (админу)
        без изменения состояния и статистики основной рассылки.
        """
        task = self.get_object()
        telegram_id = request.data.get('telegram_id')

        if not telegram_id:
            return Response(
                {'error': 'Не указан telegram_id получателя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not task.organization.bot_token:
            return Response(
                {'error': 'У организации не настроен Telegram бот.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Выбираем язык на основе языка текущего администратора
        user_lang = request.user.language
        text_template = task.message_kz if user_lang == 'kz' else task.message_ru

        # Рендерим плейсхолдер
        user_name = request.user.first_name or "Тест"
        message_text = text_template.replace('{{user_name}}', user_name)
        
        # Добавляем пометку
        message_text = f"<b>[ТЕСТОВОЕ СООБЩЕНИЕ]</b>\n\n{message_text}"

        res = send_telegram_mailing_message(
            task.organization.bot_token,
            telegram_id,
            message_text
        )

        if res['success']:
            return Response({'success': True, 'message': 'Тестовое сообщение успешно отправлено.'})
        
        return Response(
            {
                'success': False,
                'error': f"Ошибка отправки: {res['response'].get('description', 'Неизвестная ошибка')}"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
