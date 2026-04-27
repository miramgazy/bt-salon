from rest_framework import viewsets, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer
from django.utils import timezone
from django.utils.dateparse import parse_date
from apps.accounts.models import User

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated or not self.request.user.organization:
            return Appointment.objects.none()
            
        qs = Appointment.objects.filter(organization=self.request.user.organization)
        
        # Filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        master_id = self.request.query_params.get('master_id')
        service_id = self.request.query_params.get('service_id')
        my = self.request.query_params.get('my')

        if date_from:
            qs = qs.filter(start_time__date__gte=date_from)
        if date_to:
            qs = qs.filter(start_time__date__lte=date_to)
        if master_id:
            qs = qs.filter(master_id=master_id)
        if service_id:
            qs = qs.filter(service_id=service_id)
            
        if my == 'true':
            from apps.masters.models import Master
            master = Master.objects.filter(user=self.request.user).first()
            if master:
                qs = qs.filter(master=master)
            elif hasattr(self.request.user, 'telegram_id') and self.request.user.telegram_id:
                # For TMA requests, further filter by client
                qs = qs.filter(client__telegram_id=self.request.user.telegram_id)
            
        return qs.order_by('start_time')

    def perform_create(self, serializer):
        from apps.clients.models import Client
        from apps.masters.models import MasterShift
        
        user = self.request.user
        org = user.organization
        
        client = None
        # Handle Admin creating appointment
        if hasattr(user, 'role') and user.role == User.ROLE_ADMIN:
            # Check if there's an offline client data provided via context or frontend
            client_id = self.request.data.get('client_id')
            client_name = self.request.data.get('client_name')
            client_phone = self.request.data.get('client_phone')
            
            if client_id:
                client = Client.objects.filter(id=client_id, organization=org).first()
            elif client_phone:
                client = Client.objects.filter(phone=client_phone, organization=org).first()
                if not client:
                    client = Client.objects.create(
                        organization=org,
                        full_name=client_name or client_phone,
                        phone=client_phone
                    )
                elif client_name:
                    # Update name if provided explicitly by admin
                    client.full_name = client_name
                    client.save()
            else:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'client_phone': 'Phone number is required for offline clients.'})
        else:
            # 1. Get or create Client profile for the regular user
            client, _ = Client.objects.get_or_create(
                user=user,
                organization=org,
                defaults={
                    'phone': user.phone or '',
                    'full_name': f"{user.first_name} {user.last_name}".strip(),
                    'telegram_id': getattr(user, 'telegram_id', None)
                }
            )
        
        # 2. Find the appropriate Shift for the master and date
        master = serializer.validated_data.get('master')
        start_time = serializer.validated_data.get('start_time')
        
        shift = MasterShift.objects.filter(
            organization=org,
            master=master,
            date=start_time.date()
        ).first()

        if not shift:
            # Try to auto-create a shift
            shift, _ = MasterShift.objects.get_or_create(
                organization=org,
                master=master,
                date=start_time.date(),
                defaults={'is_open': False}
            )
            
        serializer.save(
            organization=org,
            client=client,
            shift=shift,
            created_by_admin=(user.role == User.ROLE_ADMIN)
        )

    def perform_update(self, serializer):
        from apps.masters.models import MasterShift
        start_time = serializer.validated_data.get('start_time')
        master = serializer.validated_data.get('master', serializer.instance.master)
        
        if start_time:
            shift = MasterShift.objects.filter(
                organization=serializer.instance.organization,
                master=master,
                date=start_time.date()
            ).first()
            
            if not shift:
                shift, _ = MasterShift.objects.get_or_create(
                    organization=serializer.instance.organization,
                    master=master,
                    date=start_time.date(),
                    defaults={'is_open': False}
                )
            serializer.save(shift=shift)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        appt = self.get_object()
        appt.status = Appointment.STATUS_CONFIRMED
        appt.save()
        return Response({'status': 'confirmed'})

    @action(detail=True, methods=['post'])
    def done(self, request, pk=None):
        appt = self.get_object()
        appt.status = Appointment.STATUS_DONE
        appt.save()
        return Response({'status': 'done'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appt = self.get_object()
        reason = request.data.get('cancellation_reason', '')
        appt.status = Appointment.STATUS_CANCELLED
        appt.cancellation_reason = reason
        appt.save()
        return Response({'status': 'cancelled'})

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        from apps.clients.models import Client
        from apps.masters.models import MasterShift
        from apps.services.models import Service
        from datetime import datetime, timedelta
        import logging
        
        logger = logging.getLogger(__name__)
        
        client_name = request.data.get('client_name')
        client_phone = request.data.get('client_phone')
        bookings = request.data.get('bookings', [])
        
        if not client_name or not client_phone:
            return Response({'error': 'Имя и номер телефона клиента обязательны'}, status=400)
            
        org = request.user.organization
        
        # Get or create client
        client, _ = Client.objects.get_or_create(
            organization=org,
            phone=client_phone,
            defaults={'full_name': client_name}
        )
        
        created_appointments = []
        errors = []
        
        for idx, b in enumerate(bookings):
            master_id = b.get('master_id')
            service_id = b.get('service_id')
            start_time_iso = b.get('start_time')
            
            if not all([master_id, service_id, start_time_iso]):
                errors.append(f"Строка {idx+1}: Не все данные заполнены (мастер, услуга или время)")
                continue
                
            try:
                service = Service.objects.get(id=service_id, organization=org)
                start_time = datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
                # Handle potentially timezone-aware Comparison if Django USE_TZ is true
                from django.utils import timezone as dj_timezone
                if dj_timezone.is_naive(start_time):
                    start_time = dj_timezone.make_aware(start_time)
                
                end_time = start_time + timedelta(minutes=service.duration_minutes)
                
                # Find appropriate shift
                shift = MasterShift.objects.filter(
                    organization=org,
                    master_id=master_id,
                    date=start_time.date(),
                    is_open=True
                ).first()
                
                if not shift:
                    errors.append(f"У мастера на {start_time.date()} не открыта смена.")
                    continue
                    
                appt = Appointment.objects.create(
                    organization=org,
                    client=client,
                    master_id=master_id,
                    service=service,
                    shift=shift,
                    start_time=start_time,
                    end_time=end_time,
                    status=Appointment.STATUS_CONFIRMED,
                    created_by_admin=True,
                    notes=b.get('notes', '')
                )
                created_appointments.append(appt.id)
            except Exception as e:
                logger.error(f"Error creating appointment: {e}")
                errors.append(f"Ошибка при сохранении строки {idx+1}: {str(e)}")
            
        if not created_appointments and errors:
            return Response({'error': 'Ни одна запись не была создана', 'details': errors}, status=400)
            
        return Response({
            'status': 'success',
            'client_id': client.id,
            'appointment_ids': created_appointments,
            'warnings': errors if errors else None
        })

class CalendarView(views.APIView):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.organization:
            return Response({'error': 'Organization not found'}, status=401)
            
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'date is required'}, status=400)
            
        target_date = parse_date(date_str)
        if not target_date:
            return Response({'error': 'invalid date'}, status=400)
            
        appointments = Appointment.objects.filter(
            organization=request.user.organization,
            start_time__date=target_date
        )
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from datetime import timedelta

class MasterStatsView(views.APIView):
    def get(self, request):
        user = request.user
        from apps.masters.models import Master
        master = Master.objects.filter(user=user).first()
        
        if not master:
            return Response({'error': 'Master profile not found'}, status=404)
            
        date_from_str = request.query_params.get('date_from')
        date_to_str = request.query_params.get('date_to')
        
        if not date_from_str or not date_to_str:
            date_to = timezone.localtime().date()
            date_from = date_to - timedelta(days=6)
        else:
            date_from = parse_date(date_from_str)
            date_to = parse_date(date_to_str)
            
        # We consider both DONE and CONFIRMED for income prediction/tracking
        appointments = Appointment.objects.filter(
            master=master,
            start_time__date__gte=date_from,
            start_time__date__lte=date_to,
        ).exclude(status=Appointment.STATUS_CANCELLED).select_related('service')
        
        total_income = sum(appt.service.total_price for appt in appointments)
        total_clients = appointments.count()
        
        # Breakdown by day for chart
        # Using a dictionary to ensure all days are represented even if no appointments
        daily_map = {}
        curr = date_from
        while curr <= date_to:
            daily_map[curr.isoformat()] = {'date': curr.isoformat(), 'income': 0, 'clients': 0}
            curr += timedelta(days=1)
            
        for appt in appointments:
            d_str = appt.start_time.date().isoformat()
            if d_str in daily_map:
                daily_map[d_str]['income'] += appt.service.total_price
                daily_map[d_str]['clients'] += 1
                
        # Popular services breakdown
        services_map = {}
        for appt in appointments:
            s_name = appt.service.name
            if s_name not in services_map:
                services_map[s_name] = {'name': s_name, 'count': 0, 'income': 0}
            services_map[s_name]['count'] += 1
            services_map[s_name]['income'] += appt.service.total_price
            
        popular_services = sorted(services_map.values(), key=lambda x: x['count'], reverse=True)[:5]
                
        return Response({
            'total_income': total_income,
            'total_clients': total_clients,
            'avg_check': round(total_income / total_clients, 2) if total_clients > 0 else 0,
            'daily': sorted(daily_map.values(), key=lambda x: x['date']),
            'popular_services': popular_services
        })
