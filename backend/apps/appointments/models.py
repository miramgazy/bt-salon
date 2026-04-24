from django.db import models

class Appointment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_DONE = 'done'
    STATUSES = [
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_CONFIRMED, 'Подтверждена'),
        (STATUS_CANCELLED, 'Отменена'),
        (STATUS_DONE, 'Завершена'),
    ]

    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    master = models.ForeignKey('masters.Master', on_delete=models.CASCADE)
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE)
    shift = models.ForeignKey('masters.MasterShift', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUSES, default=STATUS_PENDING)
    
    CONFIRMATION_PENDING = 'pending'
    CONFIRMATION_YES = 'yes'
    CONFIRMATION_NO = 'no'
    CONFIRMATION_CHOICES = [
        (CONFIRMATION_PENDING, 'Ожидает ответа'),
        (CONFIRMATION_YES, 'Да, приду'),
        (CONFIRMATION_NO, 'Нет, не приду'),
    ]
    client_confirmation = models.CharField(
        max_length=10, 
        choices=CONFIRMATION_CHOICES, 
        default=CONFIRMATION_PENDING
    )

    created_by_admin = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
