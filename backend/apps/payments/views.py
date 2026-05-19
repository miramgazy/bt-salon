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
        if amount <= 0:
            return response.Response({"error": "Prepayment amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine payment method based on organization settings
        payment_method = getattr(org, 'payment_method', 'MANUAL')
        
        # Fallback to MANUAL if SEMI_AUTOMATIC is chosen but no payment link is set
        if payment_method == 'SEMI_AUTOMATIC' and not org.kaspi_payment_link:
            payment_method = 'MANUAL'
            
        # Fallback to SEMI_AUTOMATIC or MANUAL if AUTOMATIC is chosen but keys are not configured
        if payment_method == 'AUTOMATIC' and not (org.is_prepayment_enabled and org.kaspi_api_key and org.kaspi_device_token):
            payment_method = 'SEMI_AUTOMATIC' if org.kaspi_payment_link else 'MANUAL'

        if payment_method == 'SEMI_AUTOMATIC':
            pseudo_payment_id = f"SA_{appointment.id}"
            appointment.kaspi_payment_id = pseudo_payment_id
            appointment.payment_status = Appointment.PAYMENT_PENDING_RECEIPT
            appointment.save(update_fields=['kaspi_payment_id', 'payment_status'])
            
            # Send Telegram Bot check instruction message
            client = appointment.client
            tg_id = client.telegram_id or (client.user.telegram_id if client.user else None)
            if tg_id and org.bot_token:
                from apps.accounts.utils import send_telegram_message
                is_kz = getattr(client.user, 'language', 'ru') == 'kz' if client.user else False
                
                prompt_msg = (
                    f"📄 <b>Төлем күтілуде...</b>\n\n"
                    f"Сілтеме бойынша Kaspi.kz-те <b>{amount} ₸</b> көлемінде алдын ала төлем жасап, осы чатқа алған <b>PDF-түбіртегіңізді</b> жіберіңіз.\n\n"
                    f"Жүйе оны автоматты түрде тексеріп, жазбаңызды растайды!"
                    if is_kz else
                    f"📄 <b>Ожидание оплаты...</b>\n\n"
                    f"Пожалуйста, совершите предоплату в размере <b>{amount} ₸</b> в приложении Kaspi.kz по QR-ссылке ниже, а затем отправьте полученную <b>PDF-квитанцию</b> в этот чат.\n\n"
                    f"Наша система автоматически проверит её и мгновенно подтвердит вашу запись!"
                )
                
                inline_kb = []
                if org.kaspi_payment_link:
                    inline_kb.append([{"text": "📱 Оплатить в Kaspi", "url": org.kaspi_payment_link}])
                
                tma_url = f"https://t.me/{org.bot_username}/{org.tma_name}" if org.bot_username and org.tma_name else None
                if tma_url:
                    inline_kb.append([{"text": "📱 Вернуться в приложение", "url": tma_url}])
                    
                res = send_telegram_message(
                    bot_token=org.bot_token,
                    chat_id=tg_id,
                    text=prompt_msg,
                    reply_markup={"inline_keyboard": inline_kb} if inline_kb else None
                )
                print("TELEGRAM SEND RESULT:", res, flush=True)

            return response.Response({
                "manual_mode": False,
                "payment_method": "SEMI_AUTOMATIC",
                "payment_link": org.kaspi_payment_link,
                "payment_id": pseudo_payment_id,
                "prepayment_amount": amount
            })

        elif payment_method == 'MANUAL':
            appointment.payment_status = Appointment.PAYMENT_PENDING_MANUAL
            appointment.save(update_fields=['payment_status'])
            return response.Response({
                "manual_mode": True,
                "payment_method": "MANUAL",
                "prepayment_amount": amount,
                "message": "Manual invoice required"
            })

        else: # AUTOMATIC
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
                    "payment_method": "AUTOMATIC",
                    "payment_link": payment_data.get('PaymentLink'),
                    "payment_id": payment_data.get('PaymentId'),
                    "prepayment_amount": amount
                })
            else:
                return response.Response({"error": "Failed to create payment link with Kaspi"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentStatusView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, payment_id, *args, **kwargs):
        # Find the appointment associated with this payment_id
        appointment = get_object_or_404(Appointment, kaspi_payment_id=payment_id)
        
        # If it is a semi-automatic payment, we poll the local appointment status directly
        if payment_id.startswith("SA_"):
            if appointment.payment_status == Appointment.PAYMENT_PAID:
                return response.Response({"status": "paid", "appointment_status": appointment.status})
            elif appointment.payment_status == Appointment.PAYMENT_REVIEW:
                return response.Response({"status": "review", "appointment_status": appointment.status})
            elif appointment.payment_status == Appointment.PAYMENT_PENDING_RECEIPT:
                return response.Response({"status": "pending_receipt", "appointment_status": appointment.status})
            else:
                return response.Response({"status": appointment.payment_status, "appointment_status": appointment.status})

        # Standard AUTOMATIC Kaspi status checking
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
