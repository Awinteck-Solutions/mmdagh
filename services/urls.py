# URLs
from django.urls import path
from . import views
from .views import (
    SignalCreateView,
    InboxView,
    OutboxView,
    DetailView,
    DeliveryReportView,
    load_divisions,  # Add this
    load_districts,  #
    load_policestations
)
from . views import GhanaPoliceServiceListView,GhanaPoliceServiceDetailView,police_dashboard,educationservice_dashboard,prisonsservice_dashboard,ghpolice_reports,fireservice_dashboard,GhanaFireStationListView,GhanaFireStationDetailView,GhanaFireStation_reports,FirehydrantListView,FirehydrantDetailView,Firehydrant_reports,ghmedical_dashboard,ghmedicalfacilityListView,ghmedicalfacilityDetailView,ghmedicalfacility_reports
urlpatterns = [
     path('police-dashboard/', police_dashboard, name='police_dashboard'),
    path('police/', GhanaPoliceServiceListView.as_view(), name='ghpolice_list'),
    path('police/<int:pk>/', GhanaPoliceServiceDetailView.as_view(), name='ghpolice_detail'),
    path('police/reports/', ghpolice_reports, name='ghpolice_reports'),

    #gnfs
    path('fireservice-dashboard/', fireservice_dashboard, name='fireservice_dashboard'),
    path('gnfs/', GhanaFireStationListView.as_view(), name='gnfs_list'),
    path('gnfs/<int:pk>/', GhanaFireStationDetailView.as_view(), name='gnfs_detail'),
    path('gnfs/reports/', GhanaFireStation_reports, name='GNFS_reports'),

    path('firehydrant/', FirehydrantListView.as_view(), name='firehydrant_list'),
    path('firehydrant/<int:pk>/', FirehydrantDetailView.as_view(), name='firehydrant_details'),
    path('firehydrant/reports/', Firehydrant_reports, name='firehydrant_reports'),

    path('ghmedical-dashboard/', views.ghmedical_dashboard, name='ghmedical_dashboard'),
    path('ghmedical/', views.ghmedicalfacilityListView.as_view(), name='ghmedical_list'),
    path('ghmedical/<int:pk>/', views.ghmedicalfacilityDetailView.as_view(), name='ghmedical_details'),
    path('ghmedical/reports/', views.ghmedicalfacility_reports, name='ghmedical_reports'),


    path('educationservice-dashboard/', views.educationservice_dashboard, name='educationservice_dashboard'),
    path('prisonsservice-dashboard/', views.prisonsservice_dashboard, name='prisonsservice_dashboard'),

# urls.py (app-level)
    # Message Handling
    path('create/', SignalCreateView.as_view(), name='signal_create'),
    path('inbox/', InboxView.as_view(), name='signal-inbox'),
    path('outbox/', OutboxView.as_view(), name='signal-outbox'),
    path('message/<int:pk>/',DetailView.as_view(), name='message-detail'),
    
    # Delivery Reports
    path('reports/<int:message_id>/', 
         DeliveryReportView.as_view(), 
         name='delivery_reports'),
    
    # AJAX Endpoints
    #path('ajax/load-divisions/', load_divisions, name='ajax-load_divisions'),
    #path('ajax/load-districts/', load_districts, name='ajax-load_districts'),
    #path('ajax/load-policestations/', load_policestations, name='ajax-load_policestations'),


    path('ajax/load-divisions/', views.load_divisions, name='ajax-load-divisions'),
    path('ajax/load-districts/', views.load_districts, name='ajax-load-districts'),
    path('ajax/load-policestations/', load_policestations, name='ajax-load-policestations'),
]


