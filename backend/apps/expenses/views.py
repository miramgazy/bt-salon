from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Expense, ExpenseCategory
from .serializers import (
    ExpenseSerializer, ExpenseWriteSerializer,
    ExpenseCategorySerializer
)

class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExpenseCategorySerializer
    pagination_class = None

    def get_queryset(self):
        if not self.request.user.is_authenticated or not self.request.user.organization:
            return ExpenseCategory.objects.none()
        return ExpenseCategory.objects.filter(
            organization=self.request.user.organization
        ).annotate(expenses_count=Count('expenses'))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.expenses.count() > 0:
            return Response(
                {"detail": f"Нельзя удалить статью: к ней привязано {instance.expenses.count()} расходов."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ExpenseWriteSerializer
        return ExpenseSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated or not self.request.user.organization:
            return Expense.objects.none()
            
        org = self.request.user.organization
        qs = Expense.objects.filter(organization=org)
        
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        search = self.request.query_params.get('search')
        category_id = self.request.query_params.get('category_id')
        
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if search:
            qs = qs.filter(name__icontains=search)
        if category_id:
            qs = qs.filter(category_id=category_id)
            
        sort_by = self.request.query_params.get('sort_by', 'date')
        sort_order = self.request.query_params.get('sort_order', 'desc')
        prefix = '-' if sort_order == 'desc' else ''
        
        # Map sort fields if necessary
        if sort_by == 'category':
            sort_by = 'category__name'
            
        return qs.order_by(f"{prefix}{sort_by}")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Calculate total amount before pagination
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            resp = self.get_paginated_response(serializer.data)
            resp.data['total_amount'] = float(total_amount)
            return resp

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'total_amount': float(total_amount)
        })
