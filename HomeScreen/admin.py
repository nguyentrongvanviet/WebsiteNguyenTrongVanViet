from django.contrib import admin
from .models import Infomation, MapMarker

@admin.register(MapMarker)
class MapMarkerAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'country', 'latitude', 'longitude', 'created_at')
    search_fields = ('title', 'address', 'city', 'country')
    list_filter = ('created_at', 'country', 'city')
    readonly_fields = ('created_at', 'updated_at')

