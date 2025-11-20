"""
Utility Functions for Journey Planning
Common utilities used by both route calculation and journey planning modules.
"""

import math
import requests
from functools import lru_cache

# API Keys
GEOAPIFY_API_KEY = '3600fc44d95e4e578b698c35f3edbb7d'

# Category Stay Time Estimates
CATEGORY_STAY_ESTIMATES = {
    'catering': 75,
    'restaurant': 90,
    'cafe': 45,
    'tourism': 60,
    'shopping mall': 120,
    'commercial': 60,
    'landmark': 60,
    'default': 60,
}

CATEGORY_SYNONYMS = {
    'food': 'restaurant',
    'foods': 'restaurant',
    'eat': 'catering',
    'eating': 'catering',
    'dining': 'restaurant',
    'coffee': 'cafe',
    'coffee shop': 'cafe',
    'tourist': 'tourism',
    'tourist attraction': 'tourism',
    'shopping': 'shopping mall',
    'mall': 'shopping mall',
    'shopping center': 'shopping mall',
    'commercial area': 'commercial',
    'business': 'commercial',
    'landmark': 'landmark',
    'university': 'tourism',
    'museum': 'tourism'
}


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance


def normalize_category_name(name):
    if not name:
        return None
    normalized = str(name).strip().lower()
    return CATEGORY_SYNONYMS.get(normalized, normalized)


def estimate_stay_minutes(category):
    normalized = normalize_category_name(category) or 'default'
    return CATEGORY_STAY_ESTIMATES.get(normalized, CATEGORY_STAY_ESTIMATES['default'])


def geoapify_autocomplete_lookup(query, limit=1, country_bias='vn'):
    """Use Geoapify autocomplete endpoint to resolve a free-text query."""
    if not query:
        return None
    try:
        params = {
            'text': query,
            'limit': limit,
            'apiKey': GEOAPIFY_API_KEY,
        }
        if country_bias:
            params['filter'] = f'countrycode:{country_bias}'
            params['bias'] = f'countrycode:{country_bias}'
        response = requests.get(
            'https://api.geoapify.com/v1/geocode/autocomplete',
            params=params,
            timeout=6
        )
        if response.status_code == 200:
            data = response.json()
            features = data.get('features') or []
            if features:
                coords = features[0].get('geometry', {}).get('coordinates', [])
                if len(coords) >= 2:
                    return coords
        else:
            print(f"Geoapify autocomplete error {response.status_code}: {response.text[:120]}")
    except Exception as e:
        print(f"Geoapify autocomplete exception: {e}")
    return None


@lru_cache(maxsize=512)
def geocode_location_with_geoapify(location_name):
    """Convert a location name to coordinates using Geoapify autocomplete + search."""
    query = (location_name or '').strip()
    if not query:
        return None
    # Try Geoapify autocomplete with Vietnam bias first for faster results
    coords = geoapify_autocomplete_lookup(query)
    if coords:
        return coords
    
    # Retry without country bias to allow non-Vietnam requests
    coords = geoapify_autocomplete_lookup(query, country_bias=None)
    if coords:
        return coords
    
    # Fall back to direct search endpoint
    return geocode_location_direct(query)


def geocode_location_direct(location_name, prefer_vietnam=True):
    """Direct Geoapify geocoding as fallback"""
    query = (location_name or '').strip()
    if not query:
        return None
    try:
        enhanced_query = query
        if prefer_vietnam and 'vietnam' not in query.lower():
            enhanced_query = f"{query}, Vietnam"
        response = requests.get(
            'https://api.geoapify.com/v1/geocode/search',
            params={'text': enhanced_query, 'apiKey': GEOAPIFY_API_KEY},
            timeout=6
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('features'):
                coords = data['features'][0].get('geometry', {}).get('coordinates', [])
                if len(coords) >= 2:
                    print(f"Direct Geoapify found coordinates: [{coords[0]}, {coords[1]}]")
                    return coords
        else:
            print(f"Direct Geoapify error {response.status_code}: {response.text[:120]}")
        return None
        
    except Exception as e:
        print(f"Direct geocoding error: {e}")
        return None


def calculate_route_with_geoapify_api(coords_list):
    """
    Calculate actual route using Geoapify Routing API
    Returns: dict with distance_km, duration_min, route_coordinates, duration_str
    """
    if len(coords_list) < 2:
        return None
        
    try:
        # Prepare waypoints for Geoapify API
        waypoints = []
        for coords in coords_list:
            waypoints.append(f"{coords[1]},{coords[0]}")  # lat,lon format
        
        # Build API URL
        waypoints_param = "|".join(waypoints)
        url = f"https://api.geoapify.com/v1/routing?waypoints={waypoints_param}&mode=drive&apiKey={GEOAPIFY_API_KEY}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('features') and len(data['features']) > 0:
                route = data['features'][0]
                properties = route.get('properties', {})
                
                # Extract route information
                distance_m = properties.get('distance', 0)
                distance_km = distance_m / 1000.0
                
                duration_s = properties.get('time', 0)
                duration_min = duration_s / 60.0
                
                # Format duration
                if duration_min < 60:
                    duration_str = f'{int(duration_min)} min'
                else:
                    duration_hours = duration_min / 60.0
                    duration_str = f'{duration_hours:.1f} hours'
                
                # Extract route coordinates
                geometry = route.get('geometry', {})
                coordinates = geometry.get('coordinates', [])
                geom_type = geometry.get('type', '')
                
                route_coords = []
                if geom_type == 'LineString':
                    for coord in coordinates:
                        route_coords.append({'lat': coord[1], 'lon': coord[0]})
                elif geom_type == 'MultiLineString':
                    for line in coordinates:
                        for coord in line:
                            route_coords.append({'lat': coord[1], 'lon': coord[0]})
                
                return {
                    'distance_km': round(distance_km, 2),
                    'duration_min': int(duration_min),
                    'duration_str': duration_str,
                    'route_coordinates': route_coords
                }
        
        print(f"Geoapify Routing API error: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"Geoapify Routing API error: {e}")
        return None
