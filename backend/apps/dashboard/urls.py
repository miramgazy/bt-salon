from django.urls import path
from . import views
from . import owner_views

urlpatterns = [
    path('summary/', views.SummaryView.as_view(), name='dashboard-summary'),
    path('timeline/', views.TimelineView.as_view(), name='dashboard-timeline'),
    path('by-master/', views.MasterStatsView.as_view(), name='dashboard-by-master'),
    path('by-service/', views.ServiceStatsView.as_view(), name='dashboard-by-service'),
    path('appointments/', views.DashboardAppointmentsView.as_view(), name='dashboard-appointments'),
    path('appointments/export/', views.DashboardAppointmentsExportView.as_view(), name='dashboard-appointments-export'),
    path('filters/', views.DashboardFiltersView.as_view(), name='dashboard-filters'),
    path('owner/', owner_views.OwnerDashboardAPIView.as_view(), name='dashboard-owner'),
]
