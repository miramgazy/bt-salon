from rest_framework import viewsets
from .models import Client
from .serializers import ClientSerializer

from django.db.models import Q

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated or not self.request.user.organization:
            return Client.objects.none()
            
        qs = Client.objects.filter(organization=self.request.user.organization)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search) | 
                Q(phone__icontains=search)
            )
        # TMA filtering
        is_tma = self.request.query_params.get('is_tma')
        if is_tma == 'true':
            qs = qs.filter(user__isnull=False)
        elif is_tma == 'false':
            qs = qs.filter(user__isnull=True)
            
        return qs.order_by('full_name')

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
