from rest_framework import views, status, response, permissions
from django.shortcuts import get_object_or_404
from apps.appointments.models import Appointment
from .kaspi_service import KaspiPayService
import logging

logger = logging.getLogger(__name__)

class CreatePaymentLinkView(views.APIView):
    permission_classes = [permissions.AllowAny] # TMA users might not be authenticated via DRF JWT

    def post(self, request, *args, **kwargs):
        appointment_id = request.data.get('appointment_id')
        client_phone = request.data.get('client_phone')
        
        if not appointment_id:
            return response.Response({"error": "appointment_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        appointment = get_object_or_404(Appointment, id=appointment_id)
        org = appointment.organization
        
        # Save phone if provided
        if client_phone:
            appointment.client_phone_for_invoice = client_phone
            appointment.save(update_fields=['client_phone_for_invoice'])

        # Calculate prepayment amount
        amount = appointment.calculate_prepayment_amount()
        
        # Determine if we should use manual mode
        manual_mode = not (org.is_prepayment_enabled and org.kaspi_api_key and org.kaspi_device_token)
        
        if manual_mode:
            appointment.payment_status = Appointment.PAYMENT_PENDING_MANUAL
            appointment.save(update_fields=['payment_status'])
            return response.Response({
                "manual_mode": True,
                "prepayment_amount": amount,
                "message": "Manual invoice required"
            })

        if amount <= 0:
            # If for some reason amount is 0 but it's required? 
            # Or if it's not required, the frontend shouldn't even call this.
            return response.Response({"error": "Prepayment amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

        service = KaspiPayService(org.kaspi_api_key)
        payment_data = service.create_payment_link(
            device_token=org.kaspi_device_token,
            amount=amount,
            external_id=appointment.id
        )

        if payment_data:
            appointment.kaspi_payment_id = payment_data.get('PaymentId')
            appointment.payment_status = Appointment.PAYMENT_PENDING_AUTO
            appointment.save(update_fields=['kaspi_payment_id', 'payment_status'])
            
            return response.Response({
                "manual_mode": False,
                "payment_link": payment_data.get('PaymentLink'),
                "payment_id": payment_data.get('PaymentId'),
                "prepayment_amount": amount
            })
        else:
            return response.Response({"error": "Failed to create payment link with Kaspi"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentStatusView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, payment_id, *args, **kwargs):
        # We need to find the appointment associated with this payment_id
        appointment = get_object_or_404(Appointment, kaspi_payment_id=payment_id)
        org = appointment.organization

        service = KaspiPayService(org.kaspi_api_key)
        kaspi_status = service.get_payment_status(payment_id)

        if kaspi_status == "Processed":
            if not appointment.is_paid:
                appointment.is_paid = True
                appointment.payment_status = Appointment.PAYMENT_PAID
                appointment.prepayment_received = appointment.calculate_prepayment_amount()
                appointment.status = Appointment.STATUS_CONFIRMED
                appointment.save(update_fields=['is_paid', 'status', 'payment_status', 'prepayment_received'])
                
            return response.Response({"status": "paid", "appointment_status": appointment.status})
        
        return response.Response({"status": kaspi_status or "unknown", "appointment_status": appointment.status})
