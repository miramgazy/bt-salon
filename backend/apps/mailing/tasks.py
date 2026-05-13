import logging
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from apps.accounts.models import User
from .models import MailingTask
from .selectors import get_mailing_recipients_queryset
from .utils import send_telegram_mailing_message

logger = logging.getLogger(__name__)


@shared_task
def check_scheduled_mailings():
    """
    Периодическая задача (запускается каждую минуту).
    Ищет все рассылки, время отправки которых наступило, и инициирует их обработку.
    """
    now = timezone.now()
    tasks = MailingTask.objects.filter(
        status__in=[MailingTask.STATUS_SCHEDULED, MailingTask.STATUS_IN_PROGRESS],
        scheduled_at__lte=now
    ).values_list('id', flat=True)

    for task_id in tasks:
        process_mailing_batch.delay(task_id)


@shared_task
def process_mailing_batch(task_id):
    """
    Воркер-задача для обработки одной порции (батча) получателей конкретной рассылки.
    Обеспечивает атомарность через select_for_update и защищает от лимитов Telegram API.
    """
    with transaction.atomic():
        task = MailingTask.objects.select_for_update().filter(
            id=task_id,
            status__in=[MailingTask.STATUS_SCHEDULED, MailingTask.STATUS_IN_PROGRESS]
        ).first()

        if not task:
            return

        # Получаем полный QuerySet целевой аудитории
        recipients_qs = get_mailing_recipients_queryset(task.organization, task.audience_type)

        # Если запуск первый — инициализируем счетчик аудитории и переводим статус
        if task.status == MailingTask.STATUS_SCHEDULED:
            task.total_recipients = recipients_qs.count()
            task.status = MailingTask.STATUS_IN_PROGRESS
            task.save(update_fields=['total_recipients', 'status'])

        # Если у организации не настроен бот — завершаем с ошибкой
        if not task.organization.bot_token:
            task.status = MailingTask.STATUS_ERROR
            task.save(update_fields=['status'])
            logger.error(f"[Mailing] Organization {task.organization.name} has no bot_token.")
            return

        # Выбираем батч (не более 30 пользователей со следующим ID)
        batch = list(recipients_qs.filter(id__gt=task.last_processed_user_id).order_by('id')[:30])

        if not batch:
            task.status = MailingTask.STATUS_DONE
            task.save(update_fields=['status'])
            logger.info(f"[Mailing] Task {task.id} successfully completed.")
            return

        for user in batch:
            # Выбор локали
            text_template = task.message_kz if user.language == 'kz' else task.message_ru
            
            # Рендеринг плейсхолдера
            user_name = user.first_name or "Клиент"
            message_text = text_template.replace('{{user_name}}', user_name)

            # Отправка
            res = send_telegram_mailing_message(
                task.organization.bot_token,
                user.telegram_id,
                message_text
            )

            # Обработка статусов и ошибок
            if res['status_code'] == 403:
                # Пользователь заблокировал бота — отписываем его
                User.objects.filter(id=user.id).update(is_bot_subscribed=False)
                task.unsubscribed_count += 1
            elif res['success']:
                task.sent_success += 1
            else:
                task.failed_count += 1

            task.last_processed_user_id = user.id

        task.save(update_fields=[
            'sent_success',
            'failed_count',
            'unsubscribed_count',
            'last_processed_user_id'
        ])

        # Если размер батча был 30, значит в базе могут оставаться еще пользователи.
        # Планируем асинхронный перезапуск этой же задачи с задержкой 1 секунда.
        if len(batch) == 30:
            process_mailing_batch.apply_async(args=[task.id], countdown=1)
        else:
            # Если меньше 30 — это была последняя страница
            task.status = MailingTask.STATUS_DONE
            task.save(update_fields=['status'])
            logger.info(f"[Mailing] Task {task.id} successfully completed on final short batch.")
