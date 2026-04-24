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
from apps.clients.models import Client
from apps.masters.models import Master
from apps.appointments.models import Appointment
from .models import User
from .utils import normalize_phone, send_telegram_message

logger = logging.getLogger(__name__)


class TmaAuthView(APIView):
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
                return Response({'error': 'Organization not identified or signature invalid'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 3. Check Auth Date (Must be within 24 hours)
            auth_date = int(data_dict.get('auth_date', 0))
            if time.time() - auth_date > 86400:
                return Response({'error': 'Data is outdated'}, status=status.HTTP_401_UNAUTHORIZED)

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
                    'organization_id': org.id,
                    'organization_name': org.name,
                },
                'organization_settings': {
                    'design_color': org.design_color,
                    'greeting_text': org.greeting_text,
                    'logo_url': request.build_absolute_uri(org.logo.url) if org.logo else None,
                    'instagram_link': org.instagram_link,
                    'whatsapp_number': org.whatsapp_number,
                }
            })
            
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
            'organization_id': user.organization_id,
            'organization_settings': {
                'greeting_text': user.organization.greeting_text if user.organization else "Добро пожаловать!",
                'design_color': user.organization.design_color if user.organization else "#c9a84c",
                'logo_url': request.build_absolute_uri(user.organization.logo.url) if user.organization and user.organization.logo else None,
                'instagram_link': user.organization.instagram_link if user.organization else None,
                'whatsapp_number': user.organization.whatsapp_number if user.organization else None,
            }
        })

    def patch(self, request, *args, **kwargs):
        user = request.user
        
        # 1. Process phone with normalization
        if 'phone' in request.data:
            raw_phone = request.data['phone']
            normalized = normalize_phone(raw_phone)
            
            if not normalized:
                return Response({'error': 'Invalid phone format'}, status=400)
                
            # Conflict Check / Merging
            existing_client = Client.objects.filter(
                organization_id=user.organization_id, 
                phone=normalized
            ).exclude(user=user).first()
            
            if existing_client:
                # Merge logic
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
        if 'first_name' in request.data: user.first_name = request.data['first_name']
        if 'last_name' in request.data: user.last_name = request.data['last_name']
        if 'language' in request.data: user.language = request.data['language']
        if 'is_bot_subscribed' in request.data: user.is_bot_subscribed = request.data['is_bot_subscribed']
        
        user.save()
        return self.get(request)

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
                    
                    # Send feedback and ask for consent ONLY if not already answered
                    if user.is_bot_subscribed is None:
                        markup = {
                            "inline_keyboard": [[
                                {"text": "✅ Да, согласен", "callback_data": f"consent_yes_{user.id}"},
                                {"text": "❌ Нет", "callback_data": f"consent_no_{user.id}"}
                            ]]
                        }
                        send_telegram_message(
                            token, 
                            tg_id, 
                            f"<b>Ваш номер подтвержден!</b>\n\nВы согласны получать уведомления об акциях и специальных предложениях от <b>{org.name}</b>?",
                            reply_markup=markup
                        )
                    else:
                        send_telegram_message(token, tg_id, "<b>Ваш номер подтвержден!</b> Благодарим за доверие.")

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
                    
                    status_text = "Благодарим за доверие! Вы будете первыми узнавать о наших акциях." if is_yes else "Хорошо, мы не будем беспокоить вас рассылками."
                    
                    # Answer callback query to stop loading state
                    # We can use a simple response message instead of answerCallbackQuery for simplicity
                    send_telegram_message(token, chat_id, f"✅ {status_text}")
                except User.DoesNotExist:
                    pass
            
            # Handle Appointment Confirmation
            elif data.startswith('appt_'):
                # appt_confirm_123 or appt_cancel_123
                parts = data.split('_')
                action = parts[1] # confirm or cancel
                appt_id = parts[2]
                
                try:
                    appt = Appointment.objects.get(id=appt_id)
                    if action == 'confirm':
                        appt.client_confirmation = Appointment.CONFIRMATION_YES
                        msg = "Отлично! Мы ждем вас в запланированное время. 😊"
                    else:
                        appt.client_confirmation = Appointment.CONFIRMATION_NO
                        msg = "Жаль, что вы не сможете прийти. Мы отменили вашу запись. Надеемся увидеть вас в другой раз! 👋"
                        # Optionally change the main appointment status to cancelled
                        # appt.status = Appointment.STATUS_CANCELLED
                    
                    appt.save()
                    send_telegram_message(token, chat_id, f"<b>{appt.organization.name}</b>\n\n{msg}")
                except Appointment.DoesNotExist:
                    send_telegram_message(token, chat_id, "Извините, запись не найдена или уже неактуальна.")

        return Response({'status': 'ok'})
