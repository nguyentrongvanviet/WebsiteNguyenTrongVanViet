from django.urls import path ,include
from . import views 
import debug_toolbar

urlpatterns = [
    path('Welcome/',views.Welcome),
    path('api/search-location/', views.search_location, name='search_location'),
    path('api/reverse-geocode/', views.reverse_geocode, name='reverse_geocode'),
    path('api/calculate-distance/', views.calculate_distance, name='calculate_distance'),
    path('api/map-config/', views.get_map_config, name='map_config'),
    path('api/save-marker/', views.save_marker, name='save_marker'),
    path('api/get-markers/', views.get_markers, name='get_markers'),
    path('api/delete-marker/', views.delete_marker, name='delete_marker'),
    path('api/chat/', views.chat, name='chat'),
    path('api/calculate-route/', views.calculate_route, name='calculate_route'),
    path('api/plan-journey/', views.plan_journey, name='plan_journey'),
    path('__debug__/',include(debug_toolbar.urls)),
]