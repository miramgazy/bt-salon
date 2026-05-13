from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.appointments.models import Appointment
from .models import MailingTask


def get_mailing_recipients_queryset(organization, audience_type):
    """
    Возвращает QuerySet пользователей (User), подходящих под условия рассылки
    для указанной организации.
    """
    # Базовый фильтр: пользователи этой организации, подписанные на бота, с известным telegram_id
    base_qs = User.objects.filter(
        organization=organization,
        is_bot_subscribed=True,
        telegram_id__isnull=False
    )

    if audience_type == MailingTask.AUDIENCE_ALL:
        return base_qs

    now = timezone.now()
    days_ago_60 = now - timedelta(days=60)

    if audience_type == MailingTask.AUDIENCE_ACTIVE:
        # Активные: есть записи за последние 60 дней
        return base_qs.filter(
            client_profile__appointments__start_time__gte=days_ago_60,
            client_profile__appointments__status__in=[
                Appointment.STATUS_CONFIRMED,
                Appointment.STATUS_DONE
            ]
        ).distinct()

    if audience_type == MailingTask.AUDIENCE_INACTIVE:
        # Неактивные: нет записей вообще ИЛИ последняя запись была более 60 дней назад
        # Исключаем тех, у кого есть хотя бы одна запись за последние 60 дней
        active_users = base_qs.filter(
            client_profile__appointments__start_time__gte=days_ago_60
        ).values('id')
        return base_qs.exclude(id__in=active_users)

    return base_qs
