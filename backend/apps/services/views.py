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
        elif not self.request.user.is_staff and not hasattr(self.request.user, 'role'):
            # Default for non-admin/staff users (like TMA clients)
            qs = qs.filter(is_active=True)
            
        return qs

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
