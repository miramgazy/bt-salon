from django.urls import path
from .views import OrganizationView, WebhookInfoView, SetWebhookView

urlpatterns = [
    path('', OrganizationView.as_view(), name='organization'),
    path('webhook-info/', WebhookInfoView.as_view(), name='webhook_info'),
    path('set-webhook/', SetWebhookView.as_view(), name='set_webhook'),
]
