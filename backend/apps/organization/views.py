from rest_framework import views, status
from rest_framework.response import Response
from .models import Organization
from .serializers import OrganizationSerializer
from rest_framework.permissions import IsAuthenticated

class OrganizationView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        if not org:
            return Response({'error': 'Organization not found for current user'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrganizationSerializer(org).data)

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
            
        slug = slugify_cyrillic(org.name)
        webhook_url = f"{host}/api/accounts/tma/webhook/{slug}/{org.bot_token}/"
        
        try:
            url = f"https://api.telegram.org/bot{org.bot_token}/setWebhook?url={webhook_url}"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
