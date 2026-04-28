from rest_framework import viewsets, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Master, MasterShift
from .serializers import MasterSerializer, MasterShiftSerializer
from apps.services.models import Service
from apps.appointments.models import Appointment
from apps.organization.models import Organization
from apps.accounts.models import User
from django.utils import timezone
from datetime import datetime, time, timedelta
import math

class MasterViewSet(viewsets.ModelViewSet):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer

    def get_queryset(self):
        org = self.request.user.organization
        if not org:
            return Master.objects.none()
            
        # Lazy ensure virtual master exists for organizations that had services/shifts before update
        from .utils import get_or_create_virtual_master
        get_or_create_virtual_master(org)

        qs = Master.objects.filter(organization=org).select_related('user')
        shifts_open_today = self.request.query_params.get('shifts_open_today')
        if shifts_open_today == 'true':
            qs = qs.filter(mastershift__date=timezone.now().date(), mastershift__is_open=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=False, methods=['get', 'patch', 'put'], url_path='me')
    def me(self, request):
        master = Master.objects.filter(user=request.user).first()
        if not master:
            return Response({'error': 'Master profile not found'}, status=404)
        
        if request.method in ['PATCH', 'PUT']:
            serializer = self.get_serializer(master, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
            
        serializer = self.get_serializer(master)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='me/upload-photo')
    def me_upload_photo(self, request):
        master = Master.objects.filter(user=request.user).first()
        if not master:
            return Response({'error': 'Master profile not found'}, status=404)
            
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': 'No photo provided'}, status=status.HTTP_400_BAD_REQUEST)
        master.photo = photo
        master.save()
        serializer = self.get_serializer(master, context={'request': request})
        return Response({'photo_url': serializer.data.get('photo_url')})

    @action(detail=True, methods=['post'], url_path='upload-photo')
    def upload_photo(self, request, pk=None):
        master = self.get_object()
        # Security: Only allow masters to upload their own photo, or admins
        if request.user.role == 'master' and master.user != request.user:
            return Response({'error': 'Permission denied'}, status=403)
            
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': 'No photo provided'}, status=status.HTTP_400_BAD_REQUEST)
        master.photo = photo
        master.save()
        serializer = self.get_serializer(master, context={'request': request})
        return Response({'photo_url': serializer.data.get('photo_url')})

    @action(detail=True, methods=['get'], url_path='available-slots')
    def available_slots(self, request, pk=None):
        master = self.get_object()
        date_str = request.query_params.get('date')
        service_id = request.query_params.get('service_id')
        
        if not date_str:
            return Response({'error': 'date required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        org = master.organization
        duration_minutes = org.slot_duration
        if service_id:
            try:
                service = Service.objects.get(id=service_id)
                # Verify master provides this service
                if not master.services.filter(id=service.id).exists():
                    return Response({'error': 'Master does not provide this service'}, status=status.HTTP_400_BAD_REQUEST)
                duration_minutes = service.duration_minutes
            except Service.DoesNotExist:
                return Response({'error': 'Service not found'}, status=status.HTTP_400_BAD_REQUEST)

        shift = MasterShift.objects.filter(master=master, date=target_date, is_open=True).first()
        if not shift:
            return Response({'error': 'shift_closed'}, status=status.HTTP_400_BAD_REQUEST)

        appointments = Appointment.objects.filter(
            master=master, 
            start_time__date=target_date
        ).exclude(status=Appointment.STATUS_CANCELLED)

        slots = []
        
        # We step by organization slot duration
        current_dt = datetime.combine(target_date, shift.work_start)
        end_dt = datetime.combine(target_date, shift.work_end)
        
        service_duration = timedelta(minutes=duration_minutes)
        step = timedelta(minutes=org.slot_duration)
        
        while current_dt + service_duration <= end_dt:
            slot_end_dt = current_dt + service_duration
            status_code = 'available'
            
            # 1. Lunch Check
            if org.has_lunch_break and shift.lunch_start and shift.lunch_end:
                lunch_start_dt = datetime.combine(target_date, shift.lunch_start)
                lunch_end_dt = datetime.combine(target_date, shift.lunch_end)
                if lunch_start_dt <= current_dt < lunch_end_dt:
                    status_code = 'lunch'
            
            # 2. Selected Master Busy Check
            if status_code == 'available':
                for appt in appointments:
                    appt_start_naive = timezone.make_naive(appt.start_time) if timezone.is_aware(appt.start_time) else appt.start_time
                    appt_end_naive = timezone.make_naive(appt.end_time) if timezone.is_aware(appt.end_time) else appt.end_time
                    if current_dt < appt_end_naive and slot_end_dt > appt_start_naive:
                        status_code = 'busy'
                        break

            # 3. Combo Capacity Check
            if status_code == 'available' and service_id:
                svc = Service.objects.filter(id=service_id).first()
                if svc and svc.is_combo:
                    # For combo services, we need both the selected master AND the virtual master
                    # (which acts as a queue/buffer for sub-services) to be available.
                    virtual_master = Master.objects.filter(organization=org, is_virtual=True).first()
                    if not virtual_master:
                        status_code = 'no_virtual_master'
                    else:
                        v_shift = MasterShift.objects.filter(master=virtual_master, date=target_date, is_open=True).first()
                        if not v_shift:
                            status_code = 'no_capacity'
                        else:
                            # Check if virtual master is working at this time
                            v_start = datetime.combine(target_date, v_shift.work_start)
                            v_end = datetime.combine(target_date, v_shift.work_end)
                            if not (v_start <= current_dt and current_dt + service_duration <= v_end):
                                status_code = 'no_capacity'
                            # Note: We don't check if Virtual Master is 'busy' because 
                            # it represents a queue with parallel capacity.
            
            slots.append({
                'time': current_dt.strftime('%H:%M'),
                'start_iso': current_dt.isoformat(),
                'end_iso': slot_end_dt.isoformat(),
                'status': status_code,
                'is_available': status_code == 'available'
            })
                
            current_dt += step

        return Response(slots)

    @action(detail=False, methods=['get'], url_path='working')
    def working_on_date(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'date required'}, status=400)
            
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)
            
        shifts = MasterShift.objects.filter(
            organization=request.user.organization,
            date=target_date,
            is_open=True
        ).select_related('master')
        
        masters = [s.master for s in shifts]
        from .serializers import MasterSerializer
        return Response(MasterSerializer(masters, many=True, context={'request': request}).data)

class MasterShiftViewSet(viewsets.ModelViewSet):
    queryset = MasterShift.objects.all()
    serializer_class = MasterShiftSerializer

    def get_queryset(self):
        if not (self.request.user.is_authenticated and self.request.user.organization):
            return MasterShift.objects.none()
        qs = MasterShift.objects.filter(
            organization=self.request.user.organization
        ).select_related('master')

        # Filter by master identity if user has a master profile
        from .models import Master
        master = Master.objects.filter(user=self.request.user).first()
        if master and (self.request.user.role == User.ROLE_MASTER or self.request.query_params.get('my') == 'true'):
            qs = qs.filter(master=master)

        # Filter by single date
        date = self.request.query_params.get('date')
        if date:
            qs = qs.filter(date=date)
        # Filter by month (YYYY-MM)
        month = self.request.query_params.get('month')
        if month:
            try:
                year, m = month.split('-')
                qs = qs.filter(date__year=year, date__month=m)
            except ValueError:
                pass
        return qs

    def create(self, request, *args, **kwargs):
        master_id = request.data.get('master')
        date = request.data.get('date')
        
        if master_id and date:
            existing = MasterShift.objects.filter(master_id=master_id, date=date).first()
            if existing:
                if existing.is_open:
                    return Response(
                        {'error': 'shift_already_open', 'message': 'Смена для этого мастера на указанную дату уже открыта.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    return Response(
                        {'error': 'shift_exists', 'message': 'Смена на эту дату уже создана, но сейчас закрыта.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        org = self.request.user.organization
        # Set defaults from organization if not provided
        defaults = {
            'organization': org,
            'opened_by_admin': True
        }
        
        # If work times not in request, take from org
        if 'work_start' not in self.request.data:
            defaults['work_start'] = org.work_start
        if 'work_end' not in self.request.data:
            defaults['work_end'] = org.work_end
            
        # Lunch times: only set if organization has lunch break
        if org.has_lunch_break:
            if 'lunch_start' not in self.request.data:
                defaults['lunch_start'] = org.lunch_start
            if 'lunch_end' not in self.request.data:
                defaults['lunch_end'] = org.lunch_end
        else:
            # Force None if disabled in org
            defaults['lunch_start'] = None
            defaults['lunch_end'] = None
            
        serializer.save(**defaults)

    @action(detail=False, methods=['post'], url_path='open')
    def open_shifts(self, request):
        date_str = request.data.get('date', timezone.localtime(timezone.now()).date().isoformat())
        shifts_data = request.data.get('shifts', []) # List of {master_id, work_start, work_end, ...}
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)
            
        org = request.user.organization
        if not org:
            return Response({'error': 'Organization not found for current user'}, status=400)
            
        opened = []
        for s_data in shifts_data:
            mid = s_data.get('master_id')
            if not mid: continue
            
            shift, created = MasterShift.objects.update_or_create(
                master_id=mid,
                date=target_date,
                organization=org,
                defaults={
                    'work_start': s_data.get('work_start', org.work_start),
                    'work_end': s_data.get('work_end', org.work_end),
                    'lunch_start': s_data.get('lunch_start', org.lunch_start) if org.has_lunch_break else None,
                    'lunch_end': s_data.get('lunch_end', org.lunch_end) if org.has_lunch_break else None,
                    'comment': s_data.get('comment'),
                    'is_open': True,
                    'opened_by_admin': True
                }
            )
            opened.append(shift.id)
            
        return Response({'opened': opened})

    @action(detail=False, methods=['post'], url_path='start')
    def start_shift(self, request):
        user = request.user
        # Allow masters, and allow admins/owners if they have a master profile
        has_master_profile = hasattr(user, 'master_profile')
        if user.role != 'master' and not has_master_profile:
            return Response({'error': 'Only masters or staff with master profile can start a shift'}, status=403)
            
        lat_str = request.data.get('latitude')
        lon_str = request.data.get('longitude')
        
        if not lat_str or not lon_str:
            return Response({'error': 'Latitude and longitude are required'}, status=400)
            
        try:
            lat1 = float(lat_str)
            lon1 = float(lon_str)
        except ValueError:
            return Response({'error': 'Invalid coordinates format'}, status=400)
            
        org = user.organization
        if org.latitude is None or org.longitude is None:
            return Response({'error': 'Organization coordinates not set'}, status=400)
            
        lat2, lon2 = org.latitude, org.longitude
        
        # Haversine
        R = 6371.0 # km
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        dist = R * c # km
        
        if dist > 0.05: # 50 meters
            return Response({'error': 'out_of_range', 'message': f'Вы находитесь слишком далеко ({int(dist*1000)}м) от салона.'}, status=400)
            
        today = timezone.localtime(timezone.now()).date()
        master = Master.objects.filter(user=user, organization=org).first()
        if not master:
            return Response({'error': 'Master profile not found'}, status=404)
            
        # Set defaults in case we need to create
        defaults = {
            'is_open': True,
            'actual_start': timezone.now(),
        }
        
        # Check if shift exists to keep current fields or set defaults for new shift
        shift = MasterShift.objects.filter(master=master, date=today).first()
        
        if not shift:
            # Create new shift with org defaults
            shift = MasterShift.objects.create(
                master=master,
                date=today,
                organization=org,
                work_start=org.work_start,
                work_end=org.work_end,
                lunch_start=org.lunch_start if org.has_lunch_break else None,
                lunch_end=org.lunch_end if org.has_lunch_break else None,
                is_open=True,
                actual_start=timezone.now(),
                opened_by_admin=False
            )
        else:
            # Update existing shift
            shift.is_open = True
            if not shift.actual_start: # Only set arrival time if not already set
                shift.actual_start = timezone.now()
            shift.save(update_fields=['is_open', 'actual_start'])
        
        return Response({
            'success': True, 
            'start_time': shift.actual_start.isoformat(),
            'is_open': shift.is_open
        })
