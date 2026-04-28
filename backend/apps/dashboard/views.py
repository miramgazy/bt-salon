from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum, Count, Q, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
import io
from urllib.parse import quote
from datetime import datetime, timedelta
from apps.appointments.models import Appointment
from apps.masters.models import Master, MasterShift
from apps.services.models import Service
from apps.clients.models import Client
from apps.organization.models import Organization
from apps.expenses.models import Expense

class DashboardBaseView(APIView):
    permission_classes = [permissions.IsAuthenticated] # Should check for admin role ideally

    def get_date_range(self, request):
        date_from_str = request.query_params.get('date_from')
        date_to_str = request.query_params.get('date_to')
        
        if date_to_str:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        else:
            date_to = timezone.now().date()
            
        if date_from_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        else:
            date_from = date_to - timedelta(days=30)
            
        return date_from, date_to

    def get_filtered_appointments(self, request, date_from, date_to, include_cancelled=False):
        org = request.user.organization
        qs = Appointment.objects.filter(
            organization=org,
            start_time__date__range=[date_from, date_to]
        )
        
        if not include_cancelled:
            qs = qs.exclude(status=Appointment.STATUS_CANCELLED)
        
        master_ids = request.query_params.getlist('master_ids[]') or request.query_params.getlist('master_ids')
        if master_ids:
            qs = qs.filter(master_id__in=master_ids)
            
        service_ids = request.query_params.getlist('service_ids[]') or request.query_params.getlist('service_ids')
        if service_ids:
            qs = qs.filter(service_id__in=service_ids)
            
        return qs

class SummaryView(DashboardBaseView):
    def get(self, request):
        date_from, date_to = self.get_date_range(request)
        org = request.user.organization
        # Filtered queryset for non-cancelled (as used for revenue)
        qs = self.get_filtered_appointments(request, date_from, date_to)
        
        # Detailed stats including statuses
        full_qs = Appointment.objects.filter(
            organization=org,
            start_time__date__range=[date_from, date_to]
        )
        # Apply master and service filters to full_qs as well
        master_ids = request.query_params.getlist('master_ids[]') or request.query_params.getlist('master_ids')
        if master_ids:
            full_qs = full_qs.filter(master_id__in=master_ids)
        service_ids = request.query_params.getlist('service_ids[]') or request.query_params.getlist('service_ids')
        if service_ids:
            full_qs = full_qs.filter(service_id__in=service_ids)

        # Count unique visits: count only Single and Combo Master records
        # This prevents combo parts from inflating the visit count
        visit_filter = ~Q(appointment_type=Appointment.TYPE_COMBO_SUB)
        status_counts = full_qs.filter(visit_filter).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status=Appointment.STATUS_DONE)),
            pending=Count('id', filter=Q(status=Appointment.STATUS_PENDING)),
            cancelled=Count('id', filter=Q(status=Appointment.STATUS_CANCELLED))
        )

        # Current Period Stats (Revenue uses non-cancelled)
        stats = qs.aggregate(
            revenue=Sum('total_price'),
            master_share=Sum('master_net_income'),
            salon_share=Sum('salon_net_income'),
            # Visit count (Single + Combo Master)
            appointments_count=Count('id', filter=~Q(appointment_type=Appointment.TYPE_COMBO_SUB)),
            unique_clients_count=Count('client', distinct=True)
        )
        
        revenue = stats['revenue'] or 0
        master_share = stats['master_share'] or 0
        owner_margin = stats['salon_share'] or 0
        
        # Expenses and Net Profit
        expenses_qs = Expense.objects.filter(
            organization=org,
            date__range=[date_from, date_to]
        )
        expenses_stats = expenses_qs.aggregate(
            total=Sum('amount'),
            fixed=Sum('amount', filter=Q(category_type='fixed')),
            variable=Sum('amount', filter=Q(category_type='variable'))
        )
        expenses = expenses_stats['total'] or 0
        fixed_expenses = expenses_stats['fixed'] or 0
        variable_expenses = expenses_stats['variable'] or 0
        
        net_profit = revenue - master_share - expenses
        
        # Previous Period Stats (for historical context)
        duration = (date_to - date_from).days + 1
        prev_date_to = date_from - timedelta(days=1)
        prev_date_from = prev_date_to - timedelta(days=duration - 1)
        
        prev_qs = self.get_filtered_appointments(request, prev_date_from, prev_date_to)
        prev_stats = prev_qs.aggregate(
            revenue=Sum('total_price'),
            master_share=Sum('master_net_income'),
            salon_share=Sum('salon_net_income'),
            # Count only visits in previous period too
            appointments_count=Count('id', filter=~Q(appointment_type=Appointment.TYPE_COMBO_SUB)),
            unique_clients_count=Count('client', distinct=True)
        )
        
        prev_revenue = prev_stats['revenue'] or 0
        prev_master_share = prev_stats['master_share'] or 0
        prev_net_profit = (prev_stats['salon_share'] or 0)
 
        return Response({
            "revenue": float(revenue),
            "total_revenue": float(revenue), # Alias for TMA
            "owner_margin": float(owner_margin),
            "master_share": float(master_share),
            "total_expenses": float(expenses),
            "fixed_expenses": float(fixed_expenses),
            "variable_expenses": float(variable_expenses),
            "net_profit": float(net_profit),
            "appointments_count": stats['appointments_count'],
            "unique_clients_count": stats['unique_clients_count'],
            
            # TMA Specific Status Fields
            "total_appointments": status_counts['total'],
            "completed_appointments": status_counts['completed'],
            "pending_appointments": status_counts['pending'],
            "cancelled_appointments": status_counts['cancelled'],
            
            "prev_period": {
                "revenue": float(prev_revenue),
                "net_profit": float(prev_net_profit),
                "appointments_count": prev_stats['appointments_count'],
            }
        })

class TimelineView(DashboardBaseView):
    def get(self, request):
        date_from, date_to = self.get_date_range(request)
        qs = self.get_filtered_appointments(request, date_from, date_to)
        group_by = request.query_params.get('group_by', 'day')
        
        if group_by == 'month':
            trunc_fn = TruncMonth('start_time')
        elif group_by == 'week':
            trunc_fn = TruncWeek('start_time')
        else:
            trunc_fn = TruncDay('start_time')
            
        timeline = qs.annotate(date=trunc_fn).values('date').annotate(
            revenue=Sum('total_price'),
            master_share=Sum('master_net_income'),
            salon_share=Sum('salon_net_income')
        ).order_by('date')
        
        results = []
        for item in timeline:
            rev = item['revenue'] or 0
            margin = item['salon_share'] or 0
            results.append({
                "date": item['date'].strftime('%Y-%m-%d'),
                "revenue": float(rev),
                "owner_margin": float(margin)
            })
            
        return Response({"timeline": results})

class MasterStatsView(DashboardBaseView):
    def get(self, request):
        date_from, date_to = self.get_date_range(request)
        org = request.user.organization
        
        # Basic stats
        qs = self.get_filtered_appointments(request, date_from, date_to)
        master_stats = qs.values('master_id', 'master__user__first_name', 'master__user__last_name').annotate(
            appointments_count=Count('id'),
            revenue=Sum('total_price'),
            master_share=Sum('master_net_income'),
            owner_margin=Sum('salon_net_income')
        )
        
        # Organization work hours for utilization
        # Assuming fixed hours if org settings exist
        work_hours_per_day = 8 # Default fallback
        if org and org.work_start and org.work_end:
            start = datetime.combine(date_from, org.work_start)
            end = datetime.combine(date_from, org.work_end)
            work_hours_per_day = (end - start).seconds / 3600
            
        days_count = (date_to - date_from).days + 1
        total_possible_hours = work_hours_per_day * days_count
        
        results = []
        for item in master_stats:
            rev = item['revenue'] or 0
            share = item['master_share'] or 0
            margin = item['owner_margin'] or 0
            
            # Simple utilization: 1 appointment = 1 hour (as fallback if service duration not used)
            # Better utilization: sum of service.duration_minutes / 60
            # Let's use duration_minutes
            duration_stats = qs.filter(master_id=item['master_id']).aggregate(total_mins=Sum('service__duration_minutes'))
            total_work_hours = (duration_stats['total_mins'] or 0) / 60
            utilization = (total_work_hours / total_possible_hours * 100) if total_possible_hours > 0 else 0
            
            results.append({
                "master_id": item['master_id'],
                "master_name": f"{item['master__user__first_name']} {item['master__user__last_name']}".strip(),
                "appointments_count": item['appointments_count'],
                "revenue": float(rev),
                "master_share": float(share),
                "owner_margin": float(margin),
                "utilization_percent": round(utilization, 1)
            })
            
        return Response({"masters": results})

class ServiceStatsView(DashboardBaseView):
    def get(self, request):
        date_from, date_to = self.get_date_range(request)
        qs = self.get_filtered_appointments(request, date_from, date_to)
        
        from collections import defaultdict
        # Grouping by Service + Master combination for combos
        visits = qs.filter(
            ~Q(appointment_type=Appointment.TYPE_COMBO_SUB)
        ).select_related('service', 'master__user').prefetch_related('children__master__user')
        
        svc_summary = defaultdict(lambda: {'revenue': 0, 'count': 0})
        
        for appt in visits:
            if appt.appointment_type == Appointment.TYPE_COMBO_MASTER:
                masters_involved = [appt.master.user.first_name]
                for child in appt.children.all():
                    masters_involved.append(child.master.user.first_name)
                
                unique_masters = sorted(list(set(masters_involved)))
                masters_str = " + ".join(unique_masters)
                display_name = f"{appt.service.name} ({masters_str})"
                
                total_rev = float(appt.total_price or 0)
                for child in appt.children.all():
                    total_rev += float(child.total_price or 0)
            else:
                display_name = appt.service.name
                total_rev = float(appt.total_price or 0)
                
            svc_summary[display_name]['revenue'] += total_rev
            svc_summary[display_name]['count'] += 1
            
        results = []
        for name, stats in svc_summary.items():
            results.append({
                "service_id": None, 
                "service_name": name,
                "appointments_count": stats['count'],
                "revenue": stats['revenue']
            })
        
        results.sort(key=lambda x: x['revenue'], reverse=True)
            
        return Response({"services": results})

class DashboardAppointmentsView(DashboardBaseView):
    def get(self, request):
        date_from, date_to = self.get_date_range(request)
        qs = self.get_filtered_appointments(request, date_from, date_to, include_cancelled=True)
        qs = qs.select_related('client', 'master__user', 'service', 'parent__service').prefetch_related('children__master__user')
        
        # Sort
        sort_by = request.query_params.get('sort_by', 'start_time')
        sort_order = request.query_params.get('sort_order', 'desc')
        prefix = '-' if sort_order == 'desc' else ''
        
        # To keep combo parts together, we sort by start_time, then parent_id
        # We handle sort_by for datetime/master/client if provided
        if sort_by == 'start_time':
            qs = qs.order_by(f"{prefix}start_time", 'parent_id', 'id')
        else:
            qs = qs.order_by(f"{prefix}{sort_by}")
        
        # Pagination
        from django.core.paginator import Paginator
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 25)
        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page_number)
        
        results = []
        for appt in page_obj:
            rev = appt.total_price or 0
            share = appt.master_net_income or 0
            margin = appt.salon_net_income or 0
            
            # Get display title (e.g. "Combo: Service")
            from apps.appointments.serializers import AppointmentSerializer
            display_title = AppointmentSerializer().get_display_title(appt)
            
            # Safe user names
            m_name = "—"
            if appt.master and appt.master.user:
                m_name = f"{appt.master.user.first_name} {appt.master.user.last_name}".strip()
            
            results.append({
                "id": appt.id,
                "datetime": appt.start_time.isoformat(),
                "client_name": appt.client.full_name if appt.client else "Оффлайн",
                "master_name": m_name,
                "services": [display_title],
                "total_cost": float(rev),
                "master_share": float(share),
                "owner_margin": float(margin),
                "status": appt.status,
                "appointment_type": appt.appointment_type,
                "parent_id": appt.parent_id
            })
            
        return Response({
            "count": paginator.count,
            "results": results
        })

class DashboardAppointmentsExportView(DashboardBaseView):
    def get(self, request):
        from openpyxl import Workbook
        from django.http import HttpResponse
        
        date_from, date_to = self.get_date_range(request)
        qs = self.get_filtered_appointments(request, date_from, date_to).order_by('-start_time')
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Appointments"
        
        # Headers
        headers = ['Дата', 'Время', 'Клиент', 'Мастер', 'Услуги', 'Стоимость', 'Доля мастера', 'Маржа', 'Статус']
        ws.append(headers)
        
        from apps.appointments.serializers import AppointmentSerializer
        serializer = AppointmentSerializer()
        qs = qs.select_related('client', 'master__user', 'service', 'parent__service')
        
        for appt in qs:
            rev = appt.total_price or 0
            share = appt.master_net_income or 0
            margin = appt.salon_net_income or 0
            display_title = serializer.get_display_title(appt)
            
            m_name = "—"
            if appt.master and appt.master.user:
                m_name = f"{appt.master.user.first_name} {appt.master.user.last_name}".strip()
                
            ws.append([
                appt.start_time.strftime('%Y-%m-%d'),
                appt.start_time.strftime('%H:%M'),
                appt.client.full_name if appt.client else "Оффлайн",
                m_name,
                display_title,
                float(rev),
                float(share),
                float(margin),
                appt.get_status_display()
            ])
            
        # Format columns width
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        filename = f"Записи_с_{date_from.strftime('%d-%m-%y')}_по_{date_to.strftime('%d-%m-%y')}.xlsx"
        # RFC 6266 encoding for non-ASCII filenames
        encoded_filename = quote(filename)
        
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
        return response

class DashboardFiltersView(APIView):
    def get(self, request):
        org = request.user.organization
        masters = Master.objects.filter(organization=org, is_active=True).values('id', 'user__first_name', 'user__last_name')
        services = Service.objects.filter(organization=org, is_active=True).values('id', 'name')
        
        return Response({
            "masters": [{"id": m['id'], "name": f"{m['user__first_name']} {m['user__last_name']}".strip()} for m in masters],
            "services": [{"id": s['id'], "name": s['name']} for s in services]
        })
