from django.urls import path
from .views import CreatePaymentLinkView, PaymentStatusView

urlpatterns = [
    path('create-link/', CreatePaymentLinkView.as_view(), name='create-payment-link'),
    path('status/<str:payment_id>/', PaymentStatusView.as_view(), name='payment-status'),
]
