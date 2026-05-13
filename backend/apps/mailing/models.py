from django.db import models


class MailingTask(models.Model):
    AUDIENCE_ALL = 'all'
    AUDIENCE_ACTIVE = 'active'
    AUDIENCE_INACTIVE = 'inactive'
    AUDIENCE_CHOICES = [
        (AUDIENCE_ALL, 'Все пользователи'),
        (AUDIENCE_ACTIVE, 'Активные (записи за последние 60 дней)'),
        (AUDIENCE_INACTIVE, 'Неактивные (без активности более 60 дней)'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'
    STATUS_ERROR = 'error'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик'),
        (STATUS_SCHEDULED, 'Запланирована'),
        (STATUS_IN_PROGRESS, 'В процессе'),
        (STATUS_DONE, 'Завершена'),
        (STATUS_ERROR, 'Ошибка'),
    ]

    organization = models.ForeignKey(
        'organization.Organization',
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Организация'
    )
    title = models.CharField(max_length=255, verbose_name='Название рассылки')
    message_ru = models.TextField(
        verbose_name='Сообщение (RU)',
        help_text='Поддерживается плейсхолдер {{user_name}}'
    )
    message_kz = models.TextField(
        verbose_name='Сообщение (KZ)',
        help_text='Поддерживается плейсхолдер {{user_name}}'
    )
    scheduled_at = models.DateTimeField(verbose_name='Время отправки')
    audience_type = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default=AUDIENCE_ALL,
        verbose_name='Сегмент аудитории'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name='Статус'
    )

    # Аналитика
    total_recipients = models.PositiveIntegerField(default=0, verbose_name='Всего получателей')
    sent_success = models.PositiveIntegerField(default=0, verbose_name='Успешно отправлено')
    failed_count = models.PositiveIntegerField(default=0, verbose_name='Ошибок отправки')
    unsubscribed_count = models.PositiveIntegerField(default=0, verbose_name='Отписалось (403)')

    # Курсор для пагинации батчей
    last_processed_user_id = models.IntegerField(
        default=0,
        verbose_name='Последний обработанный ID'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
