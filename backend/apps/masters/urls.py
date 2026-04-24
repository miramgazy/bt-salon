from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MasterViewSet, MasterShiftViewSet

router = DefaultRouter()
router.register(r'shifts', MasterShiftViewSet, basename='shifts')
router.register(r'', MasterViewSet, basename='masters')

urlpatterns = [
    path('', include(router.urls)),
]
