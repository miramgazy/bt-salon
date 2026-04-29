from rest_framework import views, status
from rest_framework.response import Response
from .models import Organization
from .serializers import OrganizationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

class OrganizationView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        if not org:
            return Response({'error': 'Organization not found for current user'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrganizationSerializer(org, context={'request': request}).data)

    def put(self, request):
        org = request.user.organization
        
        if not org:
            # Create a new organization for the user if they don't have one
            serializer = OrganizationSerializer(data=request.data)
            if serializer.is_valid():
                org = serializer.save()
                request.user.organization = org
                request.user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = OrganizationSerializer(org, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

import urllib.request
import json
from django.conf import settings
from apps.accounts.utils import slugify_cyrillic

class WebhookInfoView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        if not org or not org.bot_token:
            return Response({'error': 'Bot token not configured'}, status=400)
            
        try:
            url = f"https://api.telegram.org/bot{org.bot_token}/getWebhookInfo"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class SetWebhookView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        org = request.user.organization
        if not org or not org.bot_token:
            return Response({'error': 'Bot token not configured'}, status=400)
            
        # Determine host from settings or request
        host = getattr(settings, 'WEBHOOK_DOMAIN', '')
        if not host:
            host = request.build_absolute_uri('/')[:-1] # e.g. https://yourdomain.com
            
        # Clean host: remove trailing slash and common TMA prefix if it crawled in
        host = host.rstrip('/')
        if host.endswith('/tma'):
            host = host[:-4]
            
        slug = slugify_cyrillic(org.name)
        webhook_url = f"{host}/api/accounts/tma/webhook/{slug}/{org.bot_token}/"
        
        try:
            url = f"https://api.telegram.org/bot{org.bot_token}/setWebhook?url={webhook_url}"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

from rest_framework import viewsets
from apps.accounts.models import User
from .serializers import EmployeeSerializer
from apps.masters.models import Master

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org = self.request.user.organization
        if not org:
            return User.objects.none()
        
        # Lazy ensure virtual master exists
        from apps.masters.utils import get_or_create_virtual_master
        get_or_create_virtual_master(org)

        return User.objects.filter(organization=org, role__in=[User.ROLE_ADMIN, User.ROLE_MASTER])

    def perform_create(self, serializer):
        org = self.request.user.organization
        role = self.request.data.get('role', User.ROLE_MASTER)
        phone = self.request.data.get('phone')
        telegram_id = self.request.data.get('telegram_id')
        
        if not phone and not telegram_id:
            raise serializers.ValidationError({"phone": "Phone or Telegram ID is required."})

        # Check for existing user GLOBALLY
        existing_user = None
        if telegram_id:
            existing_user = User.objects.filter(telegram_id=telegram_id).order_by('-organization').first()
        if not existing_user and phone:
            clean_phone = ''.join(filter(str.isdigit, phone))
            if clean_phone:
                existing_user = User.objects.filter(phone=clean_phone).order_by('-organization').first()

        if existing_user:
            # If user has NO organization, assign this one
            if not existing_user.organization:
                existing_user.organization = org
                existing_user.save()
            
            # If user belongs to THIS organization, update them
            if existing_user.organization == org:
                # Update existing user role and other data
                user = existing_user
                user.role = role
                if phone: user.phone = phone
                if telegram_id: user.telegram_id = telegram_id
                
                # Update fields from serializer validated data
                for attr, value in serializer.validated_data.items():
                    setattr(user, attr, value)
                user.save()
                
                # Ensure Master profile exists if role is master
                if role == User.ROLE_MASTER:
                    from apps.masters.models import Master
                    master, created = Master.objects.get_or_create(user=user, defaults={'organization': org})
                    services = self.request.data.get('services', [])
                    if services:
                        master.services.set(services)
                    color = self.request.data.get('color')
                    if color:
                        master.color = color
                        master.save()
                return

        # Create new user if not found or in another org
        clean_phone = ''.join(filter(str.isdigit, phone)) if phone else str(telegram_id)
        username = f"emp_{clean_phone}_{org.id}_{User.objects.count()}"
        user = serializer.save(
            organization=org, 
            role=role,
            username=username
        )
        user.set_unusable_password()
        user.save()
        
        if role == User.ROLE_MASTER:
            from apps.masters.models import Master
            master, created = Master.objects.get_or_create(user=user, defaults={'organization': org})
            services = self.request.data.get('services', [])
            if services:
                master.services.set(services)
            color = self.request.data.get('color')
            if color:
                master.color = color
                master.save()

    def perform_update(self, serializer):
        user = serializer.save()
        if user.role == User.ROLE_MASTER:
            master, created = Master.objects.get_or_create(user=user, defaults={'organization': user.organization})
            services = self.request.data.get('services')
            if services is not None:
                master.services.set(services)
            color = self.request.data.get('color')
            if color is not None:
                master.color = color
                master.save()

    @action(detail=False, methods=['get'])
    def lookup(self, request):
        telegram_id = request.query_params.get('telegram_id')
        phone = request.query_params.get('phone')
        
        print(f"DEBUG: Employee lookup triggered. TID: {telegram_id}, Phone: {phone}")
        
        if not telegram_id and not phone:
            return Response({'error': 'Telegram ID or Phone is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = None
        
        try:
            # 1. Search by Telegram ID (Global)
            if telegram_id:
                # We search globally because a user might not be assigned to this org yet (e.g. they just started the bot)
                # We order by -organization to pick a record with an org assigned if multiple exist.
                user = User.objects.filter(telegram_id=telegram_id).order_by('-organization').first()
                if user:
                    print(f"DEBUG: Found user by TID: {user.username} (Org: {user.organization_id})")
            
            # 2. Search by Phone (Global)
            if not user and phone:
                clean_phone = ''.join(filter(str.isdigit, phone))
                if clean_phone and len(clean_phone) >= 10:
                    user = User.objects.filter(phone__icontains=clean_phone).order_by('-organization').first()
                    if user:
                        print(f"DEBUG: Found user by Phone: {user.username} (Org: {user.organization_id})")
        except Exception as e:
            print(f"ERROR: Employee lookup failed: {str(e)}")
            return Response({'error': f"Lookup failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        if user:
            return Response({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'telegram_id': user.telegram_id,
                'role': user.role
            })
            
        print("DEBUG: User not found in lookup")
        return Response({'status': 'not_found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='upload-photo')
    def upload_photo(self, request, pk=None):
        user = self.get_object()
        if user.role != User.ROLE_MASTER or not hasattr(user, 'master_profile'):
            return Response({'error': 'User is not a master'}, status=status.HTTP_400_BAD_REQUEST)
            
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': 'No photo provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        master = user.master_profile
        master.photo = photo
        master.save()
        serializer = self.get_serializer(user, context={'request': request})
        return Response({'photo_url': serializer.data.get('photo_url')})
