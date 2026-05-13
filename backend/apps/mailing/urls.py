from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MailingTaskViewSet

router = DefaultRouter()
router.register(r'mailings', MailingTaskViewSet, basename='mailing')

urlpatterns = [
    path('', include(router.urls)),
]
