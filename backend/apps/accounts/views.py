import hashlib
import hmac
import urllib.parse
import json
import logging
import time
from django.conf import settings
from django.db import models
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.organization.models import Organization
from apps.organization.serializers import OrganizationSerializer
from apps.clients.models import Client
from apps.masters.models import Master
from apps.appointments.models import Appointment
from .models import User
from .utils import normalize_phone, send_telegram_message, answer_telegram_callback

logger = logging.getLogger(__name__)


class TmaAuthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        init_data = request.data.get('initData')
        # Front can optionally pass organization_id if known
        org_id = request.data.get('organization_id')
        
        if not init_data:
            return Response({'error': 'initData is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parsed_data = urllib.parse.parse_qsl(init_data)
            data_dict = {k: v for k, v in parsed_data}
            hash_param = data_dict.pop('hash')
            
            # 1. Verification string
            data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(data_dict.items())])
            
            def validate_hash(token, data_str, received_hash):
                secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
                calc_hash = hmac.new(secret_key, data_str.encode(), hashlib.sha256).hexdigest()
                return calc_hash == received_hash

            # 2. Multi-bot Discovery
            org = None
            
            # A. Check by receiver (Optimized path)
            user_json = json.loads(data_dict.get('user', '{}'))
            # Note: receiver is sometimes in a separate 'receiver' field or implied by bot token
            # If front sends bot_username or it's in initData
            bot_username = request.data.get('bot_username')
            if bot_username:
                org = Organization.objects.filter(bot_username=bot_username).first()
                if org and not validate_hash(org.bot_token, data_check_string, hash_param):
                    org = None

            # B. Check by ID if provided
            if not org and org_id:
                org = Organization.objects.filter(id=org_id).first()
                if org and not validate_hash(org.bot_token, data_check_string, hash_param):
                    org = None

            # C. Fallback: Iterate all orgs (last resort)
            if not org:
                all_orgs = Organization.objects.exclude(bot_token__isnull=True).exclude(bot_token="")
                for candidate_org in all_orgs:
                    if validate_hash(candidate_org.bot_token, data_check_string, hash_param):
                        org = candidate_org
                        break
            
            if not org:
                print('Not org:', data_dict, hash_param, flush=True); return Response({'error': 'Organization not identified or signature invalid'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 3. Check Auth Date (Must be within 24 hours)
            auth_date = int(data_dict.get('auth_date', 0))
            if time.time() - auth_date > 86400:
                print('Outdated:', auth_date, time.time(), flush=True); return Response({'error': 'Data is outdated'}, status=status.HTTP_401_UNAUTHORIZED)

            # 4. Handle User
            tg_id = user_json.get('id')
            first_name = user_json.get('first_name', '')
            last_name = user_json.get('last_name', '')
            username_tg = user_json.get('username', f"tg_{tg_id}")
            
            user = User.objects.filter(organization=org, telegram_id=tg_id).first()
            
            if not user:
                # Create user
                user = User.objects.create(
                    username=f"tg_{org.id}_{tg_id}",
                    telegram_id=tg_id,
                    organization=org,
                    first_name=first_name,
                    last_name=last_name,
                    role=User.ROLE_CLIENT,
                )

            # 5. CRM Client Sync
            # We look for client by tg_id or by phone (if they were already in CRM)
            client = Client.objects.filter(organization=org, telegram_id=tg_id).first()
            if not client:
                # Check for existing offline client IF we had a temporary phone (rare at this step)
                client = Client.objects.create(
                    organization=org,
                    telegram_id=tg_id,
                    user=user,
                    full_name=f"{first_name} {last_name}".strip(),
                    phone=f"temp_{tg_id}" 
                )
            elif not client.user:
                client.user = user
                client.save(update_fields=['user'])

            # 6. Response
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'phone': user.phone,
                    'is_onboarded': bool(user.phone),
                    'is_bot_subscribed': user.is_bot_subscribed,
                    'has_master_profile': hasattr(user, 'master_profile'),
                    'master_id': user.master_profile.id if hasattr(user, 'master_profile') else None,
                    'organization_id': org.id,
                    'organization_name': org.name,
                    'organization_settings': OrganizationSerializer(org, context={'request': request}).data
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception("[TMA Auth] Error")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TmaMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'phone': user.phone,
            'language': user.language,
            'is_onboarded': bool(user.phone),
            'is_bot_subscribed': user.is_bot_subscribed,
            'has_master_profile': hasattr(user, 'master_profile'),
            'master_id': user.master_profile.id if hasattr(user, 'master_profile') else None,
            'organization_id': user.organization_id,
            'organization_settings': OrganizationSerializer(user.organization, context={'request': request}).data if user.organization else None
        })

    def patch(self, request, *args, **kwargs):
        user = request.user
        merge_happened = False
        new_tokens = {}
        
        # 1. Process phone with normalization
        if 'phone' in request.data:
            raw_phone = request.data['phone']
            normalized = normalize_phone(raw_phone)
            
            if not normalized:
                return Response({'error': 'Invalid phone format'}, status=400)
                
            # Conflict Check / Merging with existing Admin/Master or Client
            # Check if there is an existing USER (Admin/Master) with this phone
            existing_user = User.objects.filter(
                organization_id=user.organization_id, 
                phone=normalized
            ).exclude(id=user.id).first()

            if existing_user:
                # Merge into existing user!
                existing_user.telegram_id = user.telegram_id
                existing_user.save(update_fields=['telegram_id'])
                
                # Cleanup temporary user and its client
                Client.objects.filter(user=user).delete()
                user.delete()
                
                # Generate new tokens
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(existing_user)
                new_tokens = {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
                user = existing_user # continue with existing_user
                merge_happened = True
                
            else:
                existing_client = Client.objects.filter(
                    organization_id=user.organization_id, 
                    phone=normalized
                ).exclude(user=user).first()
                
                if existing_client:
                    # Merge client logic
                    current_client = Client.objects.filter(user=user).first()
                    if current_client:
                        current_client.delete()
                    
                    existing_client.user = user
                    existing_client.full_name = f"{user.first_name} {user.last_name}".strip()
                    existing_client.save()
                    user.phone = normalized
                else:
                    user.phone = normalized
                    client = Client.objects.filter(user=user).first()
                    if client:
                        client.phone = normalized
                        client.save()
        
        # 2. Other fields
        if not merge_happened:
            if 'first_name' in request.data: user.first_name = request.data['first_name']
            if 'last_name' in request.data: user.last_name = request.data['last_name']
            if 'language' in request.data: user.language = request.data['language']
            if 'is_bot_subscribed' in request.data: user.is_bot_subscribed = request.data['is_bot_subscribed']
            user.save()
            
        request.user = user # Ensure the get method uses the correct (possibly swapped) user
        
        response_data = self.get(request).data
        if merge_happened:
            response_data['access'] = new_tokens['access']
            response_data['refresh'] = new_tokens['refresh']
            
        return Response(response_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role', 'organization', 'phone')
        read_only_fields = ('role', 'organization')

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class TmaWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token, org_slug=None, *args, **kwargs):
        # 1. Verify token belongs to an organization
        org = Organization.objects.filter(bot_token=token).first()
        if not org:
            return Response({'status': 'invalid token'}, status=403)

        update = request.data
        message = update.get('message', {})
        contact = message.get('contact', {})
        callback_query = update.get('callback_query', {})

        # Handle text commands
        text = message.get('text', '')
        if text.startswith('/getmyid'):
            tg_id = message.get('from', {}).get('id') or message.get('chat', {}).get('id')
            if tg_id:
                response_text = f"Ваш Telegram ID:\n<code>{tg_id}</code>\n<i>(Нажмите на цифры, чтобы скопировать)</i>"
                send_telegram_message(token, tg_id, response_text)
            return Response({'status': 'ok'})

        # Handle Contact sharing
        if contact:
            tg_id = contact.get('user_id')
            phone = contact.get('phone_number')
            
            if tg_id and phone:
                normalized = normalize_phone(phone)
                user = User.objects.filter(organization=org, telegram_id=tg_id).first()
                
                if user:
                    user.phone = normalized
                    user.save(update_fields=['phone'])
                    
                    # Sync to CRM
                    client = Client.objects.filter(user=user).first()
                    if client:
                        client.phone = normalized
                        client.save(update_fields=['phone'])
                    
                    logger.info(f"[Webhook] Updated phone for user {tg_id}: {normalized}")
                    
                    # Notify via Websocket
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{user.id}",
                        {
                            "type": "user_update",
                            "message": {"event": "phone_updated", "phone": normalized}
                        }
                    )
                    
                    # Send welcome message and return button
                    is_kz = user.language == 'kz'
                    msg = (
                        f"<b>Нөміріңіз расталды!</b>\n\n<b>{org.name}</b> салонына тіркелгеніңізге рахмет. Енді сіз шеберлерге жазылып, өз визиттеріңізді басқара аласыз."
                        if is_kz else
                        f"<b>Ваш номер подтвержден!</b>\n\nБлагодарим за регистрацию в <b>{org.name}</b>. Теперь вы можете записываться к мастерам и управлять своими визитами прямо здесь."
                    )
                    
                    btn_return = "📱 Қосымшаға оралу" if is_kz else "📱 Вернуться в приложение"
                    tma_url = f"https://t.me/{org.bot_username}/{org.tma_name}" if org.bot_username and org.tma_name else None
                    
                    markup = None
                    if tma_url:
                        markup = {
                            "inline_keyboard": [[{"text": btn_return, "url": tma_url}]]
                        }
                        
                    send_telegram_message(token, tg_id, msg, reply_markup=markup)

        # Handle Callback Query (Mailing Consent)
        if callback_query:
            data = callback_query.get('data', '')
            chat_id = callback_query.get('from', {}).get('id')
            
            if data.startswith('consent_'):
                is_yes = data.startswith('consent_yes')
                user_id = data.split('_')[-1]
                
                try:
                    user = User.objects.get(id=user_id)
                    user.is_bot_subscribed = is_yes
                    user.save(update_fields=['is_bot_subscribed'])
                    
                    is_kz = user.language == 'kz'
                    if is_yes:
                        status_text = "Сенім білдіргеніңізге рахмет! Сіз біздің акцияларымыз туралы бірінші болып білетін боласыз." if is_kz else "Благодарим за доверие! Вы будете первыми узнавать о наших акциях."
                    else:
                        status_text = "Жақсы, біз сізді хабарламалармен мазаламаймыз." if is_kz else "Хорошо, мы не будем беспокоить вас рассылками."
                    
                    # Answer callback query to stop loading state
                    answer_telegram_callback(token, callback_query.get('id'))
                    
                    btn_return = "📱 Қосымшаға оралу" if is_kz else "📱 Вернуться в приложение"
                    tma_url = f"https://t.me/{user.organization.bot_username}/{user.organization.tma_name}" if user.organization and user.organization.bot_username and user.organization.tma_name else None
                    
                    markup = None
                    if tma_url:
                        markup = {
                            "inline_keyboard": [[{"text": btn_return, "url": tma_url}]]
                        }

                    send_telegram_message(token, chat_id, f"✅ {status_text}", reply_markup=markup)
                except User.DoesNotExist:
                    answer_telegram_callback(token, callback_query.get('id'), text="Ошибка: пользователь не найден")
            
            # Handle Appointment Confirmation (Client)
            elif data.startswith('appt_'):
                # appt_confirm_123 or appt_cancel_123
                parts = data.split('_')
                action = parts[1] # confirm or cancel
                appt_id = parts[2]
                
                try:
                    appt = Appointment.objects.get(id=appt_id)
                    answer_telegram_callback(token, callback_query.get('id'))
                    
                    if action == 'confirm':
                        appt.client_confirmation = Appointment.CONFIRMATION_YES
                        appt.status = Appointment.STATUS_CONFIRMED
                        msg = "Отлично! Мы ждем вас в запланированное время. 😊"
                    else:
                        appt.client_confirmation = Appointment.CONFIRMATION_NO
                        appt.status = Appointment.STATUS_CANCELLED
                        msg = "Жаль, что вы не сможете прийти. Мы отменили вашу запись. Надеемся увидеть вас в другой раз! 👋"
                    
                    appt.save()
                    send_telegram_message(token, chat_id, f"<b>{appt.organization.name}</b>\n\n{msg}")
                except Appointment.DoesNotExist:
                    answer_telegram_callback(token, callback_query.get('id'), text="Запись не найдена")
                    send_telegram_message(token, chat_id, "Извините, запись не найдена или уже неактуальна.")

            # Handle Master Appointment Status Update
            elif data.startswith('master_'):
                # master_done_123 or master_cancel_123
                parts = data.split('_')
                action = parts[1] # done or cancel
                appt_id = parts[2]
                
                try:
                    appt = Appointment.objects.select_related('master__user').get(id=appt_id)
                    
                    # Security check: only the master of this appointment can update it
                    if appt.master.user.telegram_id != chat_id:
                        answer_telegram_callback(token, callback_query.get('id'), text="Ошибка доступа")
                        return Response({'status': 'error', 'message': 'Forbidden'})
                        
                    # Status check: avoid double updates or conflicting states
                    if appt.status == Appointment.STATUS_DONE:
                        answer_telegram_callback(token, callback_query.get('id'), text="Запись уже завершена")
                        send_telegram_message(token, chat_id, "✅ Эта запись уже отмечена как выполненная.")
                        return Response({'status': 'ok'})
                    
                    if appt.status == Appointment.STATUS_CANCELLED:
                        answer_telegram_callback(token, callback_query.get('id'), text="Запись была отменена")
                        send_telegram_message(token, chat_id, "❌ Эта запись была отменена ранее.")
                        return Response({'status': 'ok'})

                    answer_telegram_callback(token, callback_query.get('id'))
                    
                    is_kz = appt.master.user.language == 'kz'
                    
                    if action == 'done':
                        appt.status = Appointment.STATUS_DONE
                        msg = "Керемет! Жұмыс орындалды деп белгіленді." if is_kz else "Отлично! Работа отмечена как выполненная."
                    else:
                        appt.status = Appointment.STATUS_CANCELLED
                        msg = "Жазба тоқтатылды." if is_kz else "Запись отменена."
                    
                    appt.save()
                    send_telegram_message(token, chat_id, f"✅ {msg}")
                    
                except Appointment.DoesNotExist:
                    answer_telegram_callback(token, callback_query.get('id'), text="Запись не найдена")
                    send_telegram_message(token, chat_id, "Извините, запись не найдена.")

        return Response({'status': 'ok'})
