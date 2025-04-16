# travel_distance_calculator/urls.py

from django.urls import path
from .import views
from .views import google_map_search

urlpatterns = [
    path('distance_calculate/', views.distance_calculate, name='distance_calculate'),
    path('trip_history/', views.trip_history, name='trip_history'),
    path('google-map-search/', views.google_map_search, name='google_map_search'),
    path('leaflet-map/', views.leaflet_map, name='leaflet_map'),
]
