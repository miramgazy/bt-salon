from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, MasterStatsView

urlpatterns = [
    path('master-stats/', MasterStatsView.as_view(), name='master-stats'),
    path('', AppointmentViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/', AppointmentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('<int:pk>/confirm/', AppointmentViewSet.as_view({'post': 'confirm'})),
    path('<int:pk>/done/', AppointmentViewSet.as_view({'post': 'done'})),
    path('<int:pk>/cancel/', AppointmentViewSet.as_view({'post': 'cancel'})),
    path('bulk-create/', AppointmentViewSet.as_view({'post': 'bulk_create'})),
]
