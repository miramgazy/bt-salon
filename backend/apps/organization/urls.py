from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationView, WebhookInfoView, SetWebhookView, EmployeeViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('', OrganizationView.as_view(), name='organization'),
    path('webhook-info/', WebhookInfoView.as_view(), name='webhook_info'),
    path('set-webhook/', SetWebhookView.as_view(), name='set_webhook'),
    path('', include(router.urls)),
]
