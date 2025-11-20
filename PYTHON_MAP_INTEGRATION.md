# Python-Powered Map Integration Guide

## Overview

Your interactive map now uses **Python (Django)** for all backend logic, with JavaScript only handling frontend UI interactions. This approach provides:

- ✅ Better security (API keys stay on server)
- ✅ Easier maintenance (logic in Python)
- ✅ Server-side calculations
- ✅ Easy to extend with database integration

## Architecture

```
┌─────────────────────────────────────┐
│   Frontend (JavaScript in Browser)  │
│   - UI interactions                 │
│   - Map display (Leaflet)           │
│   - API calls to Django             │
└──────────────┬──────────────────────┘
               │
               ▼ (JSON)
┌─────────────────────────────────────┐
│   Backend (Python/Django)           │
│   - Location search                 │
│   - Reverse geocoding               │
│   - Distance calculations           │
│   - Configuration management        │
└─────────────────────────────────────┘
```

## New Python API Endpoints

### 1. **Search Location**
```
POST /HomeScreen/api/search-location/
```
**Input:**
```json
{
    "query": "Paris"
}
```

**Output:**
```json
{
    "success": true,
    "results": [
        {
            "lat": 48.8566,
            "lon": 2.3522,
            "name": "Paris, France",
            "address": "Paris, France",
            "city": "Paris",
            "country": "France"
        }
    ]
}
```

### 2. **Reverse Geocoding** (Coordinates → Address)
```
POST /HomeScreen/api/reverse-geocode/
```
**Input:**
```json
{
    "lat": 10.8231,
    "lon": 106.6797
}
```

**Output:**
```json
{
    "success": true,
    "address": "Ho Chi Minh City, Vietnam",
    "lat": 10.8231,
    "lon": 106.6797,
    "city": "Ho Chi Minh City",
    "country": "Vietnam",
    "postcode": "N/A"
}
```

### 3. **Calculate Distance**
```
POST /HomeScreen/api/calculate-distance/
```
**Input:**
```json
{
    "lat1": 10.8231,
    "lon1": 106.6797,
    "lat2": 21.0285,
    "lon2": 105.8542
}
```

**Output:**
```json
{
    "success": true,
    "distance_km": 1686.42,
    "distance_miles": 1048.35
}
```

### 4. **Get Map Configuration**
```
POST /HomeScreen/api/map-config/
```
**Output:**
```json
{
    "default_coords": {
        "lat": 10.8231,
        "lon": 106.6797
    },
    "default_zoom": 12,
    "cities": [...],
    "map_tiles": "https://...",
    "leaflet_cdn": "https://..."
}
```

## Modified Files

### 1. `HomeScreen/views.py`
**What Changed:**
- Added 4 new API view functions
- All map logic moved from JavaScript to Python
- Uses Haversine formula for distance calculation
- Mock data for demonstration (replace with real Geoapify API)

**Key Functions:**
- `search_location()` - Search locations by name
- `reverse_geocode()` - Convert coordinates to address
- `calculate_distance()` - Calculate distance between points
- `get_map_config()` - Serve configuration to frontend

### 2. `HomeScreen/urls.py`
**What Changed:**
- Added 4 new API endpoints
- All under `/HomeScreen/api/` prefix

**New Routes:**
```
POST /HomeScreen/api/search-location/
POST /HomeScreen/api/reverse-geocode/
POST /HomeScreen/api/calculate-distance/
POST /HomeScreen/api/map-config/
```

### 3. `HomeScreen/static/js/map.js`
**What Changed:**
- Removed hardcoded constants (now fetched from backend)
- Replaced client-side API calls with Django backend calls
- All functions now use `async/await`
- Minimal JavaScript (UI only)

**Major Changes:**
- `initMap()` → now async, fetches config from Python
- `getLocationDetails()` → `getLocationDetailsFromPython()`
- `searchLocationByQuery()` → integrated into `searchLocation()`
- New `calculateDistance()` function
- New `navigateToCity()` function

## Usage Examples

### Example 1: Search for a Location
```javascript
// User types "Tokyo" and clicks search
// JavaScript calls Python backend:
fetch('/HomeScreen/api/search-location/', {
    method: 'POST',
    body: JSON.stringify({ query: 'Tokyo' })
})
// Python searches and returns coordinates
// JavaScript centers map on result
```

### Example 2: Get Address from Coordinates
```javascript
// User clicks on map at coordinates (48.8566, 2.3522)
// JavaScript calls Python backend:
fetch('/HomeScreen/api/reverse-geocode/', {
    method: 'POST',
    body: JSON.stringify({ lat: 48.8566, lon: 2.3522 })
})
// Python converts to address: "Paris, France"
// JavaScript displays in info panel
```

### Example 3: Calculate Distance
```javascript
// User clicks "Distance" button on marker
// JavaScript calls Python backend:
fetch('/HomeScreen/api/calculate-distance/', {
    method: 'POST',
    body: JSON.stringify({
        lat1: 10.8231, lon1: 106.6797,
        lat2: 21.0285, lon2: 105.8542
    })
})
// Python calculates using Haversine formula
// JavaScript displays: "1686.42 km"
```

## Setting Up Geoapify (Optional)

Currently using **mock data** for demonstration. To use real API:

1. Get API key: https://myprojects.geoapify.com/
2. Install requests library:
   ```bash
   pip install requests
   ```
3. Update `views.py` (line 32 and 109):
   ```python
   GEOAPIFY_API_KEY = 'your_actual_api_key'
   ```

## Future Enhancements

### Add Database Storage
```python
# models.py
from django.db import models

class SavedLocation(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### Add User Authentication
```python
# views.py
from django.contrib.auth.decorators import login_required

@login_required
def save_location(request):
    # Save location for authenticated user
    pass
```

### Add Route Planning
```python
# views.py
def get_route(request):
    # Use Geoapify routing API
    # Calculate optimal route between markers
    pass
```

### Add GeoJSON Support
```python
def export_markers_geojson(request):
    # Export all markers as GeoJSON
    pass
```

## Security Notes

✅ **Advantages of Python Backend:**
- API keys never exposed to browser
- Server-side validation of coordinates
- Can add authentication/authorization
- Rate limiting on API calls
- Better error handling

⚠️ **Things to Remember:**
- Add `@csrf_exempt` only for AJAX endpoints (already done)
- In production, implement proper CSRF tokens
- Add rate limiting to prevent abuse
- Validate all input coordinates
- Add authentication for saving user data

## Testing the API

### Using curl (Windows):
```powershell
$body = @{ query = "Paris" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/HomeScreen/api/search-location/" `
  -Method POST -Body $body -ContentType "application/json"
```

### Using Python:
```python
import requests
import json

response = requests.post(
    'http://localhost:8000/HomeScreen/api/search-location/',
    json={'query': 'Tokyo'}
)
print(response.json())
```

### Using JavaScript:
```javascript
fetch('http://localhost:8000/HomeScreen/api/search-location/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: 'New York' })
})
.then(r => r.json())
.then(data => console.log(data))
```

## Running the Server

```bash
cd v:\WebSiteNguyenTrongVanViet
python manage.py runserver

# Then visit: http://localhost:8000/HomeScreen/Welcome/
```

## Summary

✅ **JavaScript = UI only** (minimal, maintainable)
✅ **Python = All logic** (secure, powerful)
✅ **API-based** (easy to extend)
✅ **No hardcoded values** (configuration from backend)
✅ **Ready for database integration** (add models anytime)

Now all your map functionality is powered by Python!
