import os
import django
from django.utils import timezone
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import Appointment
from apps.organization.models import Organization
from django.db.models import Sum, Count, Q

org = Organization.objects.first()
if org:
    today = timezone.localtime().date()
    full_qs = Appointment.objects.filter(
        organization=org,
        start_time__date__range=[today, today]
    )
    visit_filter = ~Q(appointment_type=Appointment.TYPE_COMBO_SUB)
    status_counts = full_qs.filter(visit_filter).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status=Appointment.STATUS_DONE)),
        pending=Count('id', filter=Q(status=Appointment.STATUS_PENDING)),
        cancelled=Count('id', filter=Q(status=Appointment.STATUS_CANCELLED))
    )
    print(f"Org: {org.name}")
    print(f"Date: {today}")
    print(f"Counts: {status_counts}")
else:
    print("No organization found")
