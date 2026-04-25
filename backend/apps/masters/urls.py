from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MasterViewSet, MasterShiftViewSet

router = DefaultRouter()
router.register(r'shifts', MasterShiftViewSet, basename='shifts')

urlpatterns = [
    path('me/', MasterViewSet.as_view({'get': 'me', 'patch': 'me', 'put': 'me'}), name='master-me'),
    path('me/upload-photo/', MasterViewSet.as_view({'post': 'me_upload_photo'}), name='master-me-photo'),
    path('working/', MasterViewSet.as_view({'get': 'working_on_date'}), name='master-working'),
    path('', MasterViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/', MasterViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('<int:pk>/upload-photo/', MasterViewSet.as_view({'post': 'upload_photo'})),
    path('<int:pk>/available-slots/', MasterViewSet.as_view({'get': 'available_slots'})),
    path('', include(router.urls)),
]
