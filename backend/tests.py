import pytest
from apps.masters.models import Master, MasterShift
from apps.services.models import Service, Category
from apps.appointments.models import Appointment
from apps.accounts.models import User
from apps.clients.models import Client
from apps.organization.models import Organization
from django.utils import timezone
from datetime import time

@pytest.mark.django_db
def test_available_slots_calculation():
    user = User.objects.create(username='master1')
    master = Master.objects.create(user=user, full_name='Test Master')
    cat = Category.objects.create(name='Hair')
    service = Service.objects.create(
        category=cat, name='Cut',
        duration_minutes=60, base_price=100, margin_type='fixed', margin_value=0
    )
    master.services.add(service)

    today = timezone.now().date()
    # Shift 09:00 - 18:00, lunch 13:00 - 14:00
    shift = MasterShift.objects.create(
        master=master,
        date=today,
        work_start=time(9, 0),
        work_end=time(18, 0),
        lunch_start=time(13, 0),
        lunch_end=time(14, 0),
        is_open=True
    )
    
    # Needs to hit API or test the logic directly
    # Since logic is in view, we test via the test client
    from rest_framework.test import APIClient
    client = APIClient()
    
    user_req = User.objects.create(username='admin', role=User.ROLE_ADMIN)
    client.force_authenticate(user=user_req)

    response = client.get(f'/api/masters/{master.id}/available-slots/?date={today.isoformat()}&service_id={service.id}')
    assert response.status_code == 200
    slots = response.json()

    assert '09:00' in slots
    # Should end at 12:00 because duration is 60 minutes and lunch is at 13:00
    assert '12:00' in slots
    assert '13:00' not in slots # Lunch
    assert '13:30' not in slots # Lunch crossing
    assert '14:00' in slots
    
@pytest.mark.django_db
def test_appointment_conflict():
    from apps.appointments.serializers import AppointmentSerializer
    user = User.objects.create(username='master1')
    master = Master.objects.create(user=user, full_name='Test Master')
    cat = Category.objects.create(name='Hair')
    service = Service.objects.create(
        category=cat, name='Cut',
        duration_minutes=60, base_price=100, margin_type='fixed', margin_value=0
    )
    client_obj = Client.objects.create(phone='12345')
    today = timezone.now().date()
    shift = MasterShift.objects.create(
        master=master, date=today,
        work_start=time(9, 0), work_end=time(18, 0), is_open=True
    )

    from django.utils.timezone import make_aware
    import datetime

    start_1 = make_aware(datetime.datetime.combine(today, time(10, 0)))
    end_1 = make_aware(datetime.datetime.combine(today, time(11, 0)))

    Appointment.objects.create(
        client=client_obj, master=master, service=service,
        shift=shift, start_time=start_1, end_time=end_1,
        status='confirmed'
    )

    start_2 = make_aware(datetime.datetime.combine(today, time(10, 30)))
    end_2 = make_aware(datetime.datetime.combine(today, time(11, 30)))
    
    serializer = AppointmentSerializer(data={
        'client': client_obj.id,
        'master': master.id,
        'service': service.id,
        'shift': shift.id,
        'start_time': start_2,
        'end_time': end_2,
        'status': 'pending'
    })

    assert not serializer.is_valid()
    assert 'non_field_errors' in serializer.errors or 'intersect' in str(serializer.errors)
