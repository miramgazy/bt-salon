from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('administrator/', admin.site.urls),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/organization/', include('apps.organization.urls')),
    path('api/masters/', include('apps.masters.urls')),
    path('api/clients/', include('apps.clients.urls')),
    path('api/appointments/', include('apps.appointments.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/expenses/', include('apps.expenses.urls')),
    path('api/', include('apps.services.urls')),
    path('api/', include('apps.appointments.calendar_urls')), # for /api/calendar/
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
