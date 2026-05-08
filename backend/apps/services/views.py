from rest_framework import viewsets
from .models import Category, Service
from .serializers import CategorySerializer, ServiceSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.organization:
            return Category.objects.filter(organization=self.request.user.organization)
        return Category.objects.none()

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('all') == 'true':
            return None
        return super().paginate_queryset(queryset)

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated or not self.request.user.organization:
            return Service.objects.none()
            
        qs = Service.objects.filter(organization=self.request.user.organization)
        
        # Filtering by master
        master_id = self.request.query_params.get('master_id')
        if master_id:
            qs = qs.filter(master__id=master_id)
            
        # Filtering by active status
        active_only = self.request.query_params.get('is_active')
        if active_only == 'true':
            qs = qs.filter(is_active=True)
        elif not self.request.user.is_staff and getattr(self.request.user, 'role', 'client') == 'client':
            # Default for clients
            qs = qs.filter(is_active=True)

        # Search by name
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)

        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)
            
        return qs.order_by('name')

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('all') == 'true':
            return None
        return super().paginate_queryset(queryset)

