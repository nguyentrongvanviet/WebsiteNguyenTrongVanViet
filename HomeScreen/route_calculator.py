"""
Basic Route Planning Module - Task 1: Distance/Route Calculation
Handles simple distance and route calculations between locations.
"""

from .utils import (
    geocode_location_with_geoapify,
    calculate_route_with_geoapify_api,
    haversine_distance
)


def calculate_route_between_locations(locations_to_route):
    """
    Calculate route between locations using Geoapify geocoding
    Supports single route or multiple waypoints
    Falls back to direct line calculation if routing API is unavailable
    """
    try:
        if not locations_to_route or len(locations_to_route) < 2:
            return {'error': 'Need at least 2 locations', 'success': False}
        
        # Geocode all locations
        coords_list = []
        location_details = {}
        
        for location in locations_to_route:
            coords = geocode_location_with_geoapify(location)
            if coords:
                coords_list.append(coords)
                location_details[location] = {
                    'lat': coords[1],
                    'lon': coords[0]
                }
            else:
                return {'error': f'Could not find location: {location}', 'success': False}
        
        if len(coords_list) < 2:
            return {'error': 'Need at least 2 valid locations', 'success': False}
        
        # Calculate route using Geoapify Routing API for accurate results
        routing_result = calculate_route_with_geoapify_api(coords_list)
        
        if routing_result:
            # Use actual routing data
            total_distance_km = routing_result['distance_km']
            duration_min = routing_result['duration_min']
            route_coords = routing_result['route_coordinates']
            duration_str = routing_result['duration_str']
        else:
            # Fallback to Haversine if routing API fails
            print("Routing API failed, falling back to Haversine calculation")
            total_distance_km = 0
            route_coords = []
            
            # Add first waypoint
            first_coords = coords_list[0]
            route_coords.append({'lat': first_coords[1], 'lon': first_coords[0]})
            
            # Calculate distance between consecutive waypoints
            for i in range(len(coords_list) - 1):
                coords1 = coords_list[i]
                coords2 = coords_list[i + 1]
                
                # Calculate distance using Haversine formula
                lat1, lon1 = coords1[1], coords1[0]
                lat2, lon2 = coords2[1], coords2[0]
                
                distance_km = haversine_distance(lat1, lon1, lat2, lon2)
                total_distance_km += distance_km
                
                # Create interpolated route points between waypoints
                num_points = max(10, int(distance_km / 5))  # ~5km per segment
                for j in range(1, num_points + 1):
                    t = j / num_points
                    interp_lat = lat1 + (lat2 - lat1) * t
                    interp_lon = lon1 + (lon2 - lon1) * t
                    route_coords.append({'lat': interp_lat, 'lon': interp_lon})
            
            # Estimate duration based on average speed of 60 km/h
            duration_hours = total_distance_km / 60.0
            duration_min = duration_hours * 60
            
            # Format duration nicely
            if duration_min < 60:
                duration_str = f'{int(duration_min)} min'
            else:
                duration_str = f'{duration_hours:.1f} hours'
        
        # Build waypoints info for response
        waypoints_info = []
        for i, loc in enumerate(locations_to_route):
            waypoints_info.append({
                'name': loc,
                'lat': location_details[loc]['lat'],
                'lon': location_details[loc]['lon'],
                'order': i + 1
            })
        
        return {
            'success': True,
            'distance_km': round(total_distance_km, 2),
            'distance_m': total_distance_km * 1000,
            'duration': duration_str,
            'duration_min': int(duration_min),
            'route_coordinates': route_coords,
            'waypoints': waypoints_info,
            'num_stops': len(locations_to_route)
        }
    
    except Exception as e:
        print(f"Route calculation error: {e}")
        return {'error': str(e), 'success': False}


def search_places_nearby_geoapify(lat, lon, category, limit=3):
    """
    Search for places of a specific category near coordinates using Geoapify
    Used as fallback when SerpAPI is not available
    """
    try:
        import requests
        GEOAPIFY_API_KEY = '3600fc44d95e4e578b698c35f3edbb7d'
        
        # Map common categories to Geoapify categories
        category_map = {
            'restaurant': 'catering.restaurant',
            'cafe': 'catering.cafe',
            'coffee': 'catering.cafe',
            'shopping': 'commercial.shopping_mall,commercial.supermarket',
            'park': 'leisure.park',
            'museum': 'entertainment.museum',
            'tourism': 'tourism.attraction',
            'hotel': 'accommodation.hotel'
        }
        
        geoapify_category = category_map.get(category.lower(), 'commercial')
        
        url = f"https://api.geoapify.com/v2/places?categories={geoapify_category}&filter=circle:{lon},{lat},5000&limit={limit}&apiKey={GEOAPIFY_API_KEY}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            for feature in data.get('features', []):
                props = feature.get('properties', {})
                results.append({
                    'name': props.get('name', 'Unknown Place'),
                    'lat': props.get('lat'),
                    'lon': props.get('lon'),
                    'address': props.get('formatted'),
                    'distance': props.get('distance')
                })
            
            return results
            
        return []
        
    except Exception as e:
        print(f"Place search error: {e}")
        return []
