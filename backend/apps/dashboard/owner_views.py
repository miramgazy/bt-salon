from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from apps.appointments.models import Appointment
from apps.expenses.models import Expense, ExpenseCategory
from apps.masters.models import Master
from apps.services.models import Service

class OwnerDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_date_range(self, request):
        period = request.query_params.get('period', 'this_month')
        tz_now = timezone.now()
        today = tz_now.date()
        
        if period == 'custom':
            date_from_str = request.query_params.get('date_from')
            date_to_str = request.query_params.get('date_to')
            if date_from_str and date_to_str:
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            else:
                date_from = today - timedelta(days=30)
                date_to = today
        elif period == 'this_week':
            date_from = today - timedelta(days=today.weekday())
            date_to = today
        elif period == 'last_month':
            first_day_this_month = today.replace(day=1)
            date_to = first_day_this_month - timedelta(days=1)
            date_from = date_to.replace(day=1)
        else:  # Default: this_month
            date_from = today.replace(day=1)
            date_to = today
            
        return date_from, date_to

    def get(self, request):
        if request.user.role not in ['owner', 'superadmin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        org = request.user.organization
        date_from, date_to = self.get_date_range(request)
        
        # 1. Summary Metrics
        appointments = Appointment.objects.filter(
            organization=org,
            start_time__date__range=[date_from, date_to]
        ).exclude(status=Appointment.STATUS_CANCELLED)

        # Use distributed financial fields
        # Count visits: Single + Combo Master
        visit_filter = ~Q(appointment_type=Appointment.TYPE_COMBO_SUB)
        metrics = appointments.aggregate(
            revenue=Sum('total_price'),
            master_share=Sum('master_net_income'),
            salon_share=Sum('salon_net_income'),
            count=Count('id', filter=visit_filter),
            clients=Count('client', distinct=True)
        )
        
        revenue = float(metrics['revenue'] or 0)
        master_share = float(metrics['master_share'] or 0)
        owner_margin_val = float(metrics['salon_share'] or 0)
        
        expenses_qs = Expense.objects.filter(organization=org, date__range=[date_from, date_to])
        total_expenses = float(expenses_qs.aggregate(total=Sum('amount'))['total'] or 0)
        
        profit = owner_margin_val - total_expenses
        margin = (profit / revenue * 100) if revenue > 0 else 0
        avg_check = (revenue / metrics['count']) if metrics['count'] > 0 else 0
        
        # 2. Timeline Data (Combined Revenue and Expenses)
        # For simplicity, we just aggregate by day
        timeline_data = {}
        curr = date_from
        while curr <= date_to:
            timeline_data[curr.strftime('%Y-%m-%d')] = {'revenue': 0, 'expenses': 0, 'profit': 0}
            curr += timedelta(days=1)
            
        # Fill revenue
        rev_by_day = appointments.values('start_time__date').annotate(rev=Sum('total_price'))
        for entry in rev_by_day:
            dt_str = entry['start_time__date'].strftime('%Y-%m-%d')
            if dt_str in timeline_data:
                timeline_data[dt_str]['revenue'] = float(entry['rev'] or 0)
                
        # Fill expenses
        exp_by_day = expenses_qs.values('date').annotate(total=Sum('amount'))
        for entry in exp_by_day:
            dt_str = entry['date'].strftime('%Y-%m-%d')
            if dt_str in timeline_data:
                timeline_data[dt_str]['expenses'] = float(entry['total'] or 0)
                
        # Calc profit per day
        final_timeline = []
        for day, vals in sorted(timeline_data.items()):
            vals['profit'] = vals['revenue'] - vals['expenses']
            vals['day'] = day
            final_timeline.append(vals)

        # 3. Master Stats
        # Sessions should represent unique visits served by the master
        master_stats = appointments.values('master_id', 'master__user__first_name', 'master__user__last_name').annotate(
            rev=Sum('total_price'),
            share=Sum('master_net_income'),
            sessions=Count('id', filter=~Q(appointment_type=Appointment.TYPE_COMBO_SUB))
        ).order_by('-rev')
        
        masters = []
        for m in master_stats:
            masters.append({
                'id': m['master_id'],
                'name': f"{m['master__user__first_name']} {m['master__user__last_name']}".strip(),
                'revenue': float(m['rev'] or 0),
                'commission': float(m['share'] or 0),
                'sessions': m['sessions']
            })

        # 4. Detailed Service Stats
        # Grouping by Service + Master combination for combos
        from collections import defaultdict
        
        # Fetch visits (Single and Combo Master)
        visits = appointments.filter(
            ~Q(appointment_type=Appointment.TYPE_COMBO_SUB)
        ).select_related('service', 'master__user').prefetch_related('children__master__user')
        
        svc_summary = defaultdict(lambda: {'revenue': 0, 'count': 0})
        
        for appt in visits:
            # Construct composite name if combo
            if appt.appointment_type == Appointment.TYPE_COMBO_MASTER:
                # Collect all masters involved
                masters_involved = [appt.master.user.first_name]
                for child in appt.children.all():
                    masters_involved.append(child.master.user.first_name)
                
                # Unique and sorted to keep grouping consistent
                unique_masters = sorted(list(set(masters_involved)))
                masters_str = " + ".join(unique_masters)
                display_name = f"{appt.service.name} ({masters_str})"
                
                # Revenue for combo = parent.total_price + children.total_price
                total_rev = float(appt.total_price or 0)
                for child in appt.children.all():
                    total_rev += float(child.total_price or 0)
            else:
                display_name = appt.service.name
                total_rev = float(appt.total_price or 0)
                
            svc_summary[display_name]['revenue'] += total_rev
            svc_summary[display_name]['count'] += 1
            
        # Convert to list and sort by revenue
        services = []
        for name, stats in svc_summary.items():
            services.append({
                'name': name,
                'revenue': stats['revenue'],
                'count': stats['count']
            })
        services.sort(key=lambda x: x['revenue'], reverse=True)
        services = services[:10]

        # 5. Expenses Breakdown
        # Group by category_type (fixed/variable)
        expenses_categories = expenses_qs.values(
            'category__name', 
            'category__category_type'
        ).annotate(total=Sum('amount')).order_by('-total')
        
        fixed_expenses = []
        variable_expenses = []
        
        for ec in expenses_categories:
            item = {
                'label': ec['category__name'],
                'amount': float(ec['total'] or 0)
            }
            if ec['category__category_type'] == ExpenseCategory.TYPE_FIXED:
                fixed_expenses.append(item)
            else:
                variable_expenses.append(item)

        # 6. Previous Period (for compare)
        duration = (date_to - date_from).days + 1
        prev_date_to = date_from - timedelta(days=1)
        prev_date_from = prev_date_to - timedelta(days=duration - 1)
        
        prev_appts = Appointment.objects.filter(
            organization=org,
            start_time__date__range=[prev_date_from, prev_date_to]
        ).exclude(status=Appointment.STATUS_CANCELLED).aggregate(
            rev=Sum('total_price'),
            share=Sum('master_net_income'),
            salon_share=Sum('salon_net_income')
        )
        
        prev_exp = float(Expense.objects.filter(
            organization=org, 
            date__range=[prev_date_from, prev_date_to]
        ).aggregate(total=Sum('amount'))['total'] or 0)
        
        prev_rev = float(prev_appts['rev'] or 0)
        prev_salon_margin = float(prev_appts['salon_share'] or 0)
        prev_profit = prev_salon_margin - prev_exp
        
        return Response({
            'summary': {
                'revenue': revenue,
                'expenses': total_expenses,
                'profit': profit,
                'margin': round(margin, 1),
                'avg_check': round(avg_check, 0),
                'clients_count': metrics['clients'],
                'sessions_count': metrics['count'],
                'prev_revenue': prev_rev,
                'prev_profit': prev_profit,
            },
            'timeline': final_timeline,
            'masters': masters,
            'services': services,
            'expenses_fixed': fixed_expenses,
            'expenses_variable': variable_expenses,
            'period': {
                'start': date_from.strftime('%Y-%m-%d'),
                'end': date_to.strftime('%Y-%m-%d'),
            }
        })
