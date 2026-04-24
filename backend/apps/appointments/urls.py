from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, MasterStatsView

router = DefaultRouter()
router.register(r'', AppointmentViewSet)

urlpatterns = [
    path('master-stats/', MasterStatsView.as_view(), name='master-stats'),
    path('', include(router.urls)),
]
