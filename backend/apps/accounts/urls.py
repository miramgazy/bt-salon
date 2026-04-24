from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import (
    RegisterView, UserProfileView, 
    TmaAuthView, TmaMeView, TmaWebhookView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # TMA implementation based on workflow instructions
    path('tma/auth/', TmaAuthView.as_view(), name='tma_auth'),
    path('tma/me/', TmaMeView.as_view(), name='tma_me'),
    path('tma/webhook/<slug:org_slug>/<str:token>/', TmaWebhookView.as_view(), name='tma_webhook'),
]
