from celery import shared_task
from apps.appointments.models import Appointment

@shared_task
def cancel_expired_appointments_task():
    Appointment.cancel_expired_appointments()
