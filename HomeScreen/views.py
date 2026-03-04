from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import math
import random
import re
import requests
from functools import lru_cache
from datetime import datetime, timedelta
from .models import MapMarker

import google.generativeai as genai

# Try to import SerpAPI (optional dependency)
try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    GoogleSearch = None
    SERPAPI_AVAILABLE = False

# Import modular components
# Task 1: Route Calculation
from .route_calculator import (
    calculate_route_between_locations,
    search_places_nearby_geoapify
)

# Task 2: Journey Planning with SerpAPI
from .journey_planner import execute_journey_plan

# Shared utilities
from .utils import (
    geocode_location_with_geoapify,
    haversine_distance
)

# API Keys
GEOAPIFY_API_KEY = '3600fc44d95e4e578b698c35f3edbb7d'
GEMINI_API_KEY = 'AIzaSyA5gbKv4E25_qaRWvOQqradQ85vX3cu5Xg'
SERPAPI_KEY = '00a31c33d0bc5e4d27ac6619405b39762c71b00cf04a523fb394c5024d349a20'  # Add your SerpAPI key here if available

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

DEFAULT_JOURNEY_CATEGORY_POOL = [
    'catering',
    'restaurant',
    'cafe',
    'tourism',
    'shopping mall',
    'commercial'
]

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

def Welcome(request): 
    # return HttpResponse("Hello World! It's Nguyễn Trọng Văn Viết 's Blog ")
    return render(request,'Welcome.html',{'name':'Nguyen Trong Van Viet'})


# API Endpoints for Map Logic

@csrf_exempt
@require_http_methods(["POST"])
def search_location(request):
    """
    Search for a location by name using Geoapify API
    Returns: JSON with coordinates and address information
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({'error': 'Query is required'}, status=400)
        
        # Call Geoapify Geocoding API
        url = f'https://api.geoapify.com/v1/geocode/search?text={query}&apiKey={GEOAPIFY_API_KEY}'
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to search location'}, status=500)
        
        data = response.json()
        results = []
        
        if data.get('features'):
            for feature in data['features'][:5]:  # Return top 5 results
                props = feature.get('properties', {})
                coords = feature.get('geometry', {}).get('coordinates', [])
                
                results.append({
                    'lat': coords[1] if len(coords) > 1 else None,
                    'lon': coords[0] if len(coords) > 0 else None,
                    'name': props.get('formatted', 'Unknown'),
                    'address': props.get('address_line1', ''),
                    'city': props.get('city', ''),
                    'country': props.get('country', ''),
                })
        
        return JsonResponse({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reverse_geocode(request):
    """
    Convert coordinates to address using Geoapify API
    Returns: JSON with address information
    """
    try:
        data = json.loads(request.body)
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))
        
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return JsonResponse({'error': 'Invalid coordinates'}, status=400)
        
        # Call Geoapify Reverse Geocoding API
        url = f'https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={GEOAPIFY_API_KEY}'
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to reverse geocode'}, status=500)
        
        data = response.json()
        
        if data.get('features'):
            props = data['features'][0].get('properties', {})
            return JsonResponse({
                'success': True,
                'address': props.get('formatted', 'Address not found'),
                'lat': lat,
                'lon': lon,
                'city': props.get('city', 'N/A'),
                'country': props.get('country', 'N/A'),
                'postcode': props.get('postcode', 'N/A'),
            })
        
        return JsonResponse({
            'success': True,
            'address': 'Coordinates found',
            'lat': lat,
            'lon': lon,
        })
    
    except ValueError:
        return JsonResponse({'error': 'Invalid latitude or longitude'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def calculate_distance(request):
    """
    Calculate distance between two coordinates using Haversine formula
    Returns: JSON with distance in km and miles
    """
    try:
        data = json.loads(request.body)
        lat1 = float(data.get('lat1'))
        lon1 = float(data.get('lon1'))
        lat2 = float(data.get('lat2'))
        lon2 = float(data.get('lon2'))
        
        # Haversine formula to calculate distance
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance_km = R * c
        distance_miles = distance_km * 0.621371
        
        return JsonResponse({
            'success': True,
            'distance_km': round(distance_km, 2),
            'distance_miles': round(distance_miles, 2),
        })
    
    except ValueError:
        return JsonResponse({'error': 'Invalid coordinates'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_map_config(request):
    """
    Return map configuration from Python (instead of hardcoded in JS)
    """
    return JsonResponse({
        'default_coords': {
            'lat': 10.8231,
            'lon': 106.6797
        },
        'default_zoom': 12,
        'cities': [
            {'name': 'Ho Chi Minh City', 'lat': 10.8231, 'lon': 106.6797, 'emoji': '🏠'},
            {'name': 'Hanoi', 'lat': 21.0285, 'lon': 105.8542, 'emoji': '🏯'},
            {'name': 'Can Tho', 'lat': 10.3157, 'lon': 103.8484, 'emoji': '🌴'},
        ],
        'map_tiles': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'leaflet_cdn': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js',
    })


@csrf_exempt
@require_http_methods(["POST"])
def save_marker(request):
    """
    Save a marker/location to the database
    Input: {"title": "...", "latitude": ..., "longitude": ..., "address": "...", "city": "...", "country": "..."}
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        if not data.get('latitude') or not data.get('longitude'):
            return JsonResponse({'error': 'Latitude and longitude are required'}, status=400)
        
        # Create marker
        marker = MapMarker.objects.create(
            title=data.get('title', 'Unnamed Location'),
            latitude=float(data.get('latitude')),
            longitude=float(data.get('longitude')),
            address=data.get('address', ''),
            city=data.get('city', ''),
            country=data.get('country', ''),
            postcode=data.get('postcode', ''),
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Marker saved successfully',
            'marker': {
                'id': marker.id,
                'title': marker.title,
                'latitude': marker.latitude,
                'longitude': marker.longitude,
                'address': marker.address,
                'city': marker.city,
                'country': marker.country,
                'created_at': marker.created_at.isoformat()
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_markers(request):
    """
    Retrieve all saved markers from the database
    """
    try:
        markers = MapMarker.objects.all().values()
        return JsonResponse({
            'success': True,
            'count': len(list(markers)),
            'markers': list(markers)
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_marker(request):
    """
    Delete a marker by ID
    Input: {"marker_id": ...}
    """
    try:
        data = json.loads(request.body)
        marker_id = data.get('marker_id')
        
        if not marker_id:
            return JsonResponse({'error': 'Marker ID is required'}, status=400)
        
        marker = MapMarker.objects.get(id=marker_id)
        marker.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Marker {marker_id} deleted successfully'
        })
    
    except MapMarker.DoesNotExist:
        return JsonResponse({'error': 'Marker not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """
    Main chat endpoint - processes user messages
    Uses Gemini AI to understand intent with Vietnam location context
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        chat_history = data.get('history', [])
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Determine action based on keywords
        action = None
        start_location = None
        end_location = None
        categories = []
        bot_response = ""
        all_locations = []
        
        message_lower = user_message.lower()
        
        # Check for journey planning request (Prioritize this over simple distance)
        if any(word in message_lower for word in ['journey', 'plan', 'visit', 'explore', 'places', 'restaurant', 'restaurants', 'cafe', 'cafes', 'shop', 'shops', 'museum', 'museums', 'start', 'trip']):
            action = 'journey'
            
            # Always try to get full journey info to capture destinations
            journey_info = {}
            try:
                journey_info = analyze_journey_request(user_message)
            except:
                pass

            # Use info from analysis if available, otherwise fallback to fast extraction
            start_location = journey_info.get('start_location') or extract_location_with_vietnam_context(user_message, 0)
            categories = journey_info.get('must_go_categories') or extract_categories(user_message)
            must_go_destinations = journey_info.get('must_go_destinations', [])
            
            if not categories:
                categories = ['restaurant', 'cafe']
            
            if start_location:
                bot_response = f"🗺️ Planning a journey from {start_location}"
                if must_go_destinations:
                    bot_response += f" to {', '.join(must_go_destinations)}"
                bot_response += f" visiting {', '.join(categories)}..."
            else:
                bot_response = "Please specify a starting location in Vietnam for journey planning."
                action = None

        # Check for distance/route calculation request
        elif any(word in message_lower for word in ['distance', 'time', 'how far', 'how long', 'travel', 'route', 'shortest path', 'way', 'from', 'to']):
            action = 'distance'
            # Try fast extraction first, fallback to AI if needed
            all_locations = extract_locations_with_vietnam_context(user_message)
            
            # If fast extraction didn't find enough locations, try AI
            if len(all_locations) < 2:
                try:
                    all_locations = extract_locations_with_gemini_ai(user_message)
                except:
                    pass  # Keep the original results if AI fails
            
            if len(all_locations) >= 2:
                start_location = all_locations[0]
                end_location = all_locations[1]
                # Store additional locations if more than 2
                if len(all_locations) > 2:
                    action = 'multi_route'
                bot_response = f"📍 Calculating route from {start_location} to {end_location}"
                if len(all_locations) > 2:
                    waypoints = ' → '.join(all_locations[1:-1])
                    bot_response += f" via {waypoints}"
                bot_response += "..."
            else:
                bot_response = "Please specify at least two locations in Vietnam. (e.g., 'distance from Hanoi to Ho Chi Minh City')"
                action = None
        
        else:
            # Generic response
            bot_response = "I can help you with:\n1. Calculate distance between places in Vietnam (e.g., 'distance from Hanoi to Ho Chi Minh City')\n2. Plan a journey visiting specific types of places\n\nWhat would you like to do?"
        
        return JsonResponse({
            'success': True,
            'response': bot_response,
            'action': action,
            'start_location': start_location,
            'end_location': end_location,
            'categories': categories,
            'must_go_destinations': locals().get('must_go_destinations', []),
            'preferences': extract_preferences(user_message),
            'all_locations': all_locations if action in ['distance', 'multi_route'] else None
        })
    
    except Exception as e:
        print(f"Chat error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def calculate_route(request):
    """
    TASK 1: Calculate route between locations
    Uses route_calculator module for basic distance/route calculations
    """
    try:
        data = json.loads(request.body)
        start = data.get('start')
        end = data.get('end')
        waypoints = data.get('waypoints', [])
        all_locations = data.get('all_locations', [])
        
        # Use all_locations if provided, otherwise use start and end
        if all_locations and len(all_locations) >= 2:
            locations_to_route = all_locations
        elif start and end:
            locations_to_route = [start, end] + waypoints
        else:
            return JsonResponse({'error': 'Start and end locations required'}, status=400)
        
        # Use the modular route calculator
        result = calculate_route_between_locations(locations_to_route)
        
        if result.get('success'):
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
    
    except Exception as e:
        print(f"Route calculation error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def plan_journey(request):
    """
    TASK 2: Plan journey with SerpAPI integration
    Uses journey_planner module for intelligent route planning with ratings and operating hours
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message') or ''
        
        # Step 1: Analyze user intent with Gemini
        journey_intent = analyze_journey_request(user_message)
        
        # Log the extracted features as requested
        print("\n" + "="*50)
        print("JOURNEY INTENT EXTRACTION LOG")
        print("="*50)
        print(json.dumps(journey_intent, indent=2))
        print("="*50 + "\n")
        
        # If start_location is missing in intent, try to use the one from request (user's current location)
        if not journey_intent.get('start_location') and data.get('start_location'):
            journey_intent['start_location'] = data.get('start_location')
            print(f"Using user provided start location: {journey_intent['start_location']}")

        # Execute the journey plan (imported from journey_planner module)
        journey_result = execute_journey_plan(journey_intent)
        
        return JsonResponse(journey_result)
    
    except Exception as e:
        print(f"Plan journey error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def execute_journey_plan(intent):
    """
    Execute the journey plan: geocode locations, find places, calculate route.
    """
    try:
        start_location = intent.get('start_location')
        must_go_destinations = intent.get('must_go_destinations', [])
        must_go_categories = intent.get('must_go_categories', [])
        
        if not start_location:
            return {'success': False, 'error': 'Start location is required'}
            
        # 1. Geocode Start Location
        start_coords = geocode_location_with_geoapify(start_location)
        if not start_coords:
            return {'success': False, 'error': f'Could not find start location: {start_location}'}
            
        journey_stops = []
        
        # Add Start
        journey_stops.append({
            'name': start_location,
            'lat': start_coords[1],
            'lon': start_coords[0],
            'category': 'start',
            'order': 1,
            'must_visit': True,
            'stay_minutes': 0,
            'rating': 'N/A',
            'operating_hours': 'N/A'
        })
        
        current_coords = start_coords
        order_counter = 2
        
        # 2. Process Must-Go Destinations with SerpAPI for details
        must_go_details = []
        for dest_name in must_go_destinations:
            # Try to get details from SerpAPI first
            details = get_place_details_serpapi(dest_name)
            
            if details:
                must_go_details.append({
                    'name': details.get('title', dest_name),
                    'lat': details.get('lat'),
                    'lon': details.get('lon'),
                    'category': 'destination',
                    'must_visit': True,
                    'stay_minutes': 60,
                    'rating': details.get('rating', 'N/A'),
                    'operating_hours': details.get('operating_hours', 'N/A'),
                    'address': details.get('address', '')
                })
            else:
                # Fallback to Geoapify
                dest_coords = geocode_location_with_geoapify(dest_name)
                if dest_coords:
                    must_go_details.append({
                        'name': dest_name,
                        'lat': dest_coords[1],
                        'lon': dest_coords[0],
                        'category': 'destination',
                        'must_visit': True,
                        'stay_minutes': 60,
                        'rating': 'N/A',
                        'operating_hours': 'N/A'
                    })
                else:
                    print(f"Warning: Could not find destination {dest_name}")

        # 3. Find Candidates for Categories
        # We search for candidates near Start and all Must-Go locations
        category_candidates = {} # category -> list of places
        
        search_anchors = [{'lat': start_coords[1], 'lon': start_coords[0]}]
        for d in must_go_details:
            search_anchors.append({'lat': d['lat'], 'lon': d['lon']})
            
        for category in must_go_categories:
            candidates = []
            # Search near each anchor
            for anchor in search_anchors:
                # Use SerpAPI to find top rated places
                results = search_places_serpapi(f"{category}", anchor['lat'], anchor['lon'])
                candidates.extend(results)
            
            # Deduplicate by name/address
            unique_candidates = []
            seen = set()
            for c in candidates:
                key = f"{c['title']}_{c.get('address','')}"
                if key not in seen:
                    seen.add(key)
                    unique_candidates.append(c)
            
            # Sort by rating
            unique_candidates.sort(key=lambda x: float(x.get('rating', 0) or 0), reverse=True)
            category_candidates[category] = unique_candidates[:5] # Keep top 5

        # 4. Schedule the Journey (Greedy Approach with Time)
        # Start time: 9:00 AM
        current_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Pending items
        pending_must_gos = must_go_details[:]
        pending_categories = must_go_categories[:]
        
        # Current location is Start
        curr_loc = journey_stops[0]
        
        while pending_must_gos or pending_categories:
            best_next_stop = None
            best_score = -float('inf')
            is_category = False
            selected_category = None
            
            # Evaluate Must-Gos
            for i, stop in enumerate(pending_must_gos):
                dist = haversine_distance(curr_loc['lat'], curr_loc['lon'], stop['lat'], stop['lon'])
                # Simple score: closer is better
                score = -dist 
                
                # Check hours if available
                if is_open_at_time(stop.get('operating_hours'), current_time + timedelta(minutes=dist*2)): # approx travel time
                    score += 100 # Bonus for being open
                else:
                    score -= 100 # Penalty for being closed
                    
                if score > best_score:
                    best_score = score
                    best_next_stop = stop
                    is_category = False
            
            # Evaluate Categories
            for cat in pending_categories:
                candidates = category_candidates.get(cat, [])
                for cand in candidates:
                    dist = haversine_distance(curr_loc['lat'], curr_loc['lon'], cand['lat'], cand['lon'])
                    rating = float(cand.get('rating', 0) or 0)
                    
                    # Score: Rating is important, Distance is cost
                    score = (rating * 10) - dist
                    
                    # Check hours
                    if is_open_at_time(cand.get('operating_hours'), current_time + timedelta(minutes=dist*2)):
                        score += 100
                    else:
                        score -= 100
                        
                    if score > best_score:
                        best_score = score
                        best_next_stop = {
                            'name': cand['title'],
                            'lat': cand['lat'],
                            'lon': cand['lon'],
                            'category': cat,
                            'must_visit': False,
                            'stay_minutes': estimate_stay_minutes(cat),
                            'rating': cand.get('rating'),
                            'operating_hours': cand.get('operating_hours'),
                            'address': cand.get('address')
                        }
                        is_category = True
                        selected_category = cat
            
            if best_next_stop:
                # Add to journey
                best_next_stop['order'] = order_counter
                journey_stops.append(best_next_stop)
                order_counter += 1
                
                # Update state
                curr_loc = best_next_stop
                
                # Estimate travel time (rough: 30km/h = 0.5km/min)
                dist = haversine_distance(journey_stops[-2]['lat'], journey_stops[-2]['lon'], curr_loc['lat'], curr_loc['lon'])
                travel_minutes = int(dist * 2) 
                stay_minutes = best_next_stop.get('stay_minutes', 60)
                
                current_time += timedelta(minutes=travel_minutes + stay_minutes)
                
                # Remove from pending
                if is_category:
                    pending_categories.remove(selected_category)
                else:
                    # Remove the specific must-go object
                    pending_must_gos = [p for p in pending_must_gos if p['name'] != best_next_stop['name']]
            else:
                break # Should not happen unless empty
        
        # 5. Calculate Final Route
        route_coords = []
        total_distance = 0
        total_duration = 0
        
        coords_list = [[stop['lon'], stop['lat']] for stop in journey_stops]
        route_result = calculate_route_with_geoapify_api(coords_list)
        
        if route_result:
            route_coords = route_result['route_coordinates']
            total_distance = route_result['distance_km']
            total_duration = route_result['duration_min']
        
        # Calculate stay time
        total_stay_time = sum(stop.get('stay_minutes', 0) for stop in journey_stops)
        total_time = total_duration + total_stay_time
        
        return {
            'success': True,
            'journey': journey_stops,
            'route_coordinates': route_coords,
            'summary': {
                'stops_planned': len(journey_stops),
                'total_distance_km': round(total_distance, 2),
                'estimated_total_minutes': int(total_time),
                'must_visit_satisfied': must_go_destinations,
                'categories_covered': must_go_categories
            }
        }

    except Exception as e:
        print(f"Execute journey error: {e}")
        return {'success': False, 'error': str(e)}


def search_places_serpapi(query, lat, lon, limit=5):
    """Search for places using SerpAPI Google Maps engine"""
    if not SERPAPI_AVAILABLE or not GoogleSearch:
        print("SerpAPI not installed")
        return []
        
    try:
        params = {
            "engine": "google_maps",
            "q": query,
            "ll": f"@{lat},{lon},14z",
            "type": "search",
            "api_key": SERPAPI_KEY,
            "hl": "en"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        local_results = results.get("local_results", [])
        
        places = []
        for res in local_results[:limit]:
            places.append({
                'title': res.get('title'),
                'rating': res.get('rating'),
                'reviews': res.get('reviews'),
                'address': res.get('address'),
                'operating_hours': res.get('operating_hours'),
                'lat': res.get('gps_coordinates', {}).get('latitude'),
                'lon': res.get('gps_coordinates', {}).get('longitude')
            })
        return places
    except Exception as e:
        print(f"SerpAPI search error: {e}")
        return []

def get_place_details_serpapi(place_name):
    """Get details for a specific place using SerpAPI"""
    if not SERPAPI_AVAILABLE or not GoogleSearch:
        return None
        
    try:
        params = {
            "engine": "google_maps",
            "q": place_name,
            "type": "search",
            "api_key": SERPAPI_KEY,
            "hl": "en"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        local_results = results.get("local_results", [])
        
        if local_results:
            res = local_results[0]
            return {
                'title': res.get('title'),
                'rating': res.get('rating'),
                'address': res.get('address'),
                'operating_hours': res.get('operating_hours'),
                'lat': res.get('gps_coordinates', {}).get('latitude'),
                'lon': res.get('gps_coordinates', {}).get('longitude')
            }
        return None
    except Exception as e:
        print(f"SerpAPI details error: {e}")
        return None

def is_open_at_time(operating_hours, check_time):
    """
    Check if place is open at specific time.
    operating_hours format from SerpAPI: {'monday': '9AM-5PM', ...} or similar
    """
    if not operating_hours:
        return True # Assume open if no data
        
    try:
        # Get day name (lowercase)
        day_name = check_time.strftime('%A').lower()
        
        hours_str = operating_hours.get(day_name)
        if not hours_str or hours_str.lower() == 'closed':
            return False
        if hours_str.lower() == 'open 24 hours':
            return True
            
        # Simple parser for "9 AM - 5 PM" or "09:00 - 17:00"
        # This is a simplified parser and might need robustness for complex strings
        # For now, we'll just return True if we have hours, assuming the scheduler isn't too strict
        # Implementing a full natural language time parser is complex
        return True 
        
    except Exception:
        return True

def search_places_nearby(lat, lon, category, limit=3):
    """
    Search for places of a specific category near coordinates using Geoapify
    """
    try:
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



def analyze_journey_request(user_text):
    """
    Analyze user text using Gemini to extract journey parameters.
    """
    try:
        # raise Exception("Force fallback testing")
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        prompt = f"""
        Analyze the following travel request. The input is in English.
        
        Request: "{user_text}"
        
        Please extract the following information and return as JSON:
        1. start_location: The starting location. If not found, return null.
        2. must_go_destinations: A list of specific places the user wants to visit. If none, return [].
        3. must_go_categories: A list of categories (e.g., catering, restaurant, cafe, tourism, commercial, shopping mall). If none, return [].
        4. travel_period: The time period for travel (e.g., "morning", "afternoon", "whole day", "2 hours"). If not found, return "whole day".
        5. destination_count: The number of destinations to visit. If not found, return 5.
        
        JSON Format:
        {{
            "start_location": "string or null",
            "must_go_destinations": ["string", ...],
            "must_go_categories": ["string", ...],
            "travel_period": "string",
            "destination_count": integer
        }}
        """
        
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=500,
            candidate_count=1
        )
        
        response = model.generate_content(prompt, generation_config=generation_config)
        result_text = response.text.strip()
        
        # Parse JSON
        try:
            # clean markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
                
            data = json.loads(result_text)
            
            # Apply defaults if missing or null
            if not data.get('must_go_categories'):
                # Randomly choose from set if empty
                pool = ['catering', 'restaurant', 'cafe', 'tourism', 'commercial', 'shopping mall']
                # Pick 1-3 random categories
                count = random.randint(1, 3)
                data['must_go_categories'] = random.sample(pool, count)
            
            if not data.get('travel_period'):
                data['travel_period'] = "whole day"
                
            if not data.get('destination_count'):
                data['destination_count'] = 5
                
            return data
            
        except json.JSONDecodeError:
            print(f"Failed to parse Gemini response: {result_text}")
            # Return defaults
            return {
                "start_location": None,
                "must_go_destinations": [],
                "must_go_categories": random.sample(['catering', 'restaurant', 'cafe', 'tourism', 'commercial', 'shopping mall'], 2),
                "travel_period": "whole day",
                "destination_count": 5
            }
            
    except Exception as e:
        print(f"Gemini analysis error: {e}")
        # Fallback logic
        print("Using fallback extraction logic...")
        
        try:
            # Extract locations using regex
            print("Calling extract_locations_with_vietnam_context...")
            locations = extract_locations_with_vietnam_context(user_text)
            print(f"Locations found: {locations}")
            
            start_loc = locations[0] if locations else None
            destinations = locations[1:] if len(locations) > 1 else []
            
            # Extract categories using keywords
            print("Calling extract_categories...")
            categories = extract_categories(user_text)
            print(f"Categories found: {categories}")
            
            if not categories:
                 categories = random.sample(['catering', 'restaurant', 'cafe', 'tourism', 'commercial', 'shopping mall'], 2)
            
            print("Returning fallback result...")
            return {
                "start_location": start_loc,
                "must_go_destinations": destinations,
                "must_go_categories": categories,
                "travel_period": "whole day",
                "destination_count": 5,
                "error": str(e) # Keep error for debugging
            }
        except Exception as fallback_error:
            print(f"CRITICAL ERROR in fallback: {fallback_error}")
            return {
                "error": f"Fallback failed: {fallback_error}",
                "original_error": str(e)
            }


def extract_locations_with_vietnam_context(text):
    """Extract all location names from text - improved for complex addresses"""
    locations = []
    normalized_text = text or ""

    # Normalize leading bullets and fancy quotes so the fallback parser sees clean words
    bullet_translation = str.maketrans({
        '\u2022': ' ',  # •
        '\u25aa': ' ',  # ▪
        '\u25ab': ' ',  # ▫
        '\u25e6': ' ',  # ◦
        '\u25cf': ' ',  # ●
        '\u00b7': ' ',  # ·
    })
    normalized_text = normalized_text.translate(bullet_translation)
    normalized_text = (normalized_text
                       .replace('“', '"')
                       .replace('”', '"')
                       .replace('‘', "'")
                       .replace('’', "'"))
    normalized_text = normalized_text.strip()
    strip_chars = " \"'`´.,;:?!•*-()[]{}"
    text_lower = normalized_text.lower()
    
    print(f"DEBUG: Extracting locations from: '{normalized_text}'")
    
    # Only basic university abbreviations - let Gemini AI handle all other locations
    vietnam_abbrev = {
        'uit': 'UIT',
        'hcmus': 'HCMUS',
        'vnu': 'VNU',
        'bk': 'Bach Khoa',
    }
    
    # Check abbreviations with word boundaries
    for abbrev, full_name in vietnam_abbrev.items():
        if f' {abbrev} ' in f' {text_lower} ' or text_lower.startswith(abbrev + ' ') or text_lower.endswith(f' {abbrev}'):
            if full_name not in locations:
                locations.append(full_name)
    
    # Special handling for addresses with numbers and street names
    # Pattern for Vietnamese addresses: number/number street_name district number city
    address_pattern = r'(\d+/\d+\s+[A-Za-z\s]+(?:district|quan|quận)\s*\d+[^?]*(?:ho chi minh city|hcmc|tp hcm))'
    address_matches = re.findall(address_pattern, normalized_text, re.IGNORECASE)
    for match in address_matches:
        cleaned = match.strip(strip_chars)
        if cleaned not in locations:
            locations.append(cleaned)
    
    # Pattern for street addresses: number street_name
    street_pattern = r'(\d+/\d+\s+[A-Za-z\s]+(?:street|đường)?)'
    street_matches = re.findall(street_pattern, normalized_text, re.IGNORECASE)
    for match in street_matches:
        cleaned = match.strip(strip_chars)
        # Only add if it's not already covered by full address
        if cleaned not in locations and len(cleaned) > 5:
            locations.append(cleaned)
            
    # Pattern for "starting from X" or "end at Y" (handling lowercase)
    # Capture text between "starting from" and next keyword (and, then, to, etc.)
    start_patterns = [
        r'starting from\s+(.*?)(?=\s+(?:and|then|to|with|having|visiting)|\s*$)',
        r'start from\s+(.*?)(?=\s+(?:and|then|to|with|having|visiting)|\s*$)',
        r'begin at\s+(.*?)(?=\s+(?:and|then|to|with|having|visiting)|\s*$)',
        r'end at\s+(.*?)(?=\s+(?:and|then|with|having)|\s*$)',
        r'end the trip at\s+(.*?)(?=\s+(?:and|then|with|having)|\s*$)',
        r'finish at\s+(.*?)(?=\s+(?:and|then|with|having)|\s*$)'
    ]
    
    for pattern in start_patterns:
        matches = re.findall(pattern, normalized_text, re.IGNORECASE)
        for match in matches:
            cleaned = match.strip(strip_chars)
            # Filter out common non-location words if captured by mistake
            if (cleaned and len(cleaned) > 2 and 
                cleaned.lower() not in ['the', 'a', 'an', 'some', 'any', 'here', 'there']):
                # Capitalize it nicely since we found it in a location context
                if cleaned.lower() == 'thao cam vien':
                    cleaned = 'Thao Cam Vien'
                elif cleaned.islower():
                    cleaned = cleaned.title()
                    
                if cleaned not in locations:
                    locations.append(cleaned)
                    print(f"DEBUG: Extracted context-based location: '{cleaned}'")
    
    # Use Gemini AI to intelligently extract only actual locations
    additional_locations = []
    try:
        additional_locations = extract_smart_locations_with_gemini(normalized_text, locations)
        locations.extend(additional_locations)
    except Exception as e:
        print(f"Smart location extraction error: {e}")

    # Fallback extraction if Gemini failed or returned nothing
    if not additional_locations:
        print("DEBUG: Entering fallback extraction block")
        # Improved fallback extraction for landmarks and buildings
        words = normalized_text.split()
        print(f"DEBUG FALLBACK: Processing {len(words)} words: {words}")
        i = 0
        while i < len(words):
            word = words[i].strip(strip_chars)
            
            # Check for landmark patterns like "landmark 81", "building 123", "tower 456"
            # Also handle joined cases like "landmark81"
            if 'landmark' in word.lower() or 'building' in word.lower() or 'tower' in word.lower():
                # Case 1: "landmark81" (joined)
                if any(char.isdigit() for char in word):
                     if word not in locations:
                        locations.append(word.title())
                        print(f"Extracted joined landmark: {word.title()}")
                     i += 1
                     continue
                
                # Case 2: "landmark 81" (separated)
                if i + 1 < len(words):
                    next_word = words[i + 1].strip(strip_chars)
                    if next_word.isdigit() or (next_word and next_word[0].isupper()):
                        landmark_name = f"{word.title()} {next_word}"  # Capitalize properly
                        if landmark_name not in locations:
                            locations.append(landmark_name)
                            print(f"Extracted landmark: {landmark_name}")
                        i += 2
                        continue
            
            # Regular capitalized word extraction for fallback
            elif (len(word) > 2 and 
                word[0].isupper() and 
                word not in locations and
                word.lower() not in ['what', 'how', 'can', 'the', 'distance', 'from', 'to', 'calculating', 'design', 'trip', 'finish', 'locations']):
                
                print(f"DEBUG FALLBACK: Found capitalized word: '{word}'")
                
                # Check if it's part of a multi-word location
                location_phrase = word
                j = i + 1
                while j < len(words) and j < i + 3:  # Max 3 words for location
                    if j < len(words):
                        next_word = words[j].strip(strip_chars)
                        if (len(next_word) > 0 and 
                            (next_word[0].isupper() or 
                             next_word.lower() in ['of', 'and', 'city', 'university', 'technology', 'science'])):
                            location_phrase += ' ' + next_word
                            j += 1
                        else:
                            break
                    else:
                        break
                
                if location_phrase not in locations:
                    locations.append(location_phrase)
                    print(f"DEBUG FALLBACK: Added location: '{location_phrase}'")
                i = j if j > i + 1 else i + 1
            else:
                i += 1
    
    # Clean trailing punctuation picked up during parsing
    cleaned_locations = []
    for loc in locations:
        cleaned_loc = loc.strip(strip_chars)
        cleaned_loc = re.sub(r'\b(and|or)$', '', cleaned_loc, flags=re.IGNORECASE).strip()
        if cleaned_loc:
            cleaned_locations.append(cleaned_loc)
    locations = cleaned_locations

    # Remove duplicates and subsets to avoid multi-route confusion
    print(f"DEBUG: Before filtering, locations = {locations}")
    unique_locations = []
    for loc in locations:
        # Skip obvious non-locations
        if loc.lower() in [
            'what\'s', 'how', 'can', 'do', 'the', 'a', 'distance', 'from', 'to', 'between',
            'route', 'is', 'are', 'calculating', 'calculate', 'find', 'show', 'get', 'give',
            'tell', 'please', 'design', 'trip', 'visit', 'finish', 'locations'
        ]:
            continue
            
        # Check if this location is already covered by a longer, more specific one
        is_duplicate = False
        for i, unique_loc in enumerate(unique_locations):
            # If current location is subset of existing unique location, skip it
            if loc.lower() in unique_loc.lower() and loc != unique_loc and len(loc) < len(unique_loc):
                is_duplicate = True
                break
            # If existing unique location is subset of current location, replace it
            elif unique_loc.lower() in loc.lower() and loc != unique_loc and len(unique_loc) < len(loc):
                unique_locations[i] = loc
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_locations.append(loc)
    
    return unique_locations


def extract_location_with_vietnam_context(text, position=0):
    """Extract location with Vietnam abbreviations - FAST"""
    locations = extract_locations_with_vietnam_context(text)
    
    if position < len(locations):
        return locations[position]
    elif locations:
        return locations[0]
    return None


def extract_smart_locations_with_gemini(text, existing_locations):
    """Use Gemini AI to intelligently extract only actual location names"""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        prompt = f"""
        Analyze this English text and extract ONLY actual location names (places, cities, addresses, landmarks):
        "{text}"
        
        Already found: {existing_locations}
        
        Rules:
        1. Only return real places, cities, addresses, or landmarks
        2. Ignore action words like: calculating, find, show, get, what, how, from, to, distance, route
        3. Ignore common words like: the, a, an, is, are, can, do, will
        4. Focus on proper nouns that represent actual places
        5. Don't duplicate locations already found
        
        Return only new location names as a comma-separated list.
        If no new locations found, return "NONE"
        
        Examples:
        - "Calculating route from HCMUS to Nguyen Trai" → "NONE" (HCMUS already found, Nguyen Trai is address)
        - "Find distance between Ho Chi Minh City and Hanoi" → "Ho Chi Minh City, Hanoi"
        - "Show me the way to District 1" → "District 1"
        """
        
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=100,
            candidate_count=1
        )
        
        response = model.generate_content(prompt, generation_config=generation_config)
        result = response.text.strip()
        
        if result == "NONE" or not result:
            return []
        
        # Parse comma-separated locations
        new_locations = [loc.strip().strip('"\'') for loc in result.split(',') if loc.strip()]
        
        # Filter out any that are already found or are obviously not locations
        filtered_locations = []
        for loc in new_locations:
            if (loc and 
                loc not in existing_locations and 
                len(loc) > 1 and
                loc.lower() not in ['none', 'calculating', 'route', 'distance', 'from', 'to']):
                filtered_locations.append(loc)
        
        return filtered_locations
        
    except Exception as e:
        print(f"Smart Gemini location extraction error: {e}")
        return []


def extract_locations_with_gemini_ai(text):
    """Extract location names using Gemini AI for better accuracy"""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        prompt = f"""
        Extract all location names from the following text. Focus on places in Vietnam but include international locations too.
        Text: "{text}"
        
        Return only the location names as a simple comma-separated list. No explanations.
        Examples of expected formats:
        - "Hanoi, Ho Chi Minh City"
        - "UIT, Bach Khoa University"
        - "Ben Nha, Vung Tau"
        
        If no locations found, return "NONE"
        """
        
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=100,
            candidate_count=1
        )
        
        response = model.generate_content(prompt, generation_config=generation_config)
        result = response.text.strip()
        
        if result == "NONE":
            return []
        
        locations = [loc.strip() for loc in result.split(',') if loc.strip()]
        
        cleaned_locations = []
        for loc in locations:
            loc = loc.strip('"\'')
            if len(loc) > 1 and loc.lower() not in ['the', 'a', 'an', 'and', 'or', 'from', 'to', 'distance', 'time', 'travel']:
                cleaned_locations.append(loc)
        
        return cleaned_locations
        
    except Exception as e:
        print(f"Gemini AI location extraction error: {e}")
        return extract_locations_with_vietnam_context(text)
def extract_categories(text):
    """Extract place categories from text"""
    category_keywords = {
        'coffee': ['coffee', 'cafe', 'café', 'drink', 'tea', 'milk tea'],
        'restaurant': ['restaurant', 'dining', 'food', 'eat', 'lunch', 'dinner', 'breakfast', 'banh mi', 'pho', 'noodle', 'rice', 'bread', 'snack'],
        'shopping': ['shopping', 'mall', 'store', 'shop', 'buy', 'market', 'supermarket'],
        'park': ['park', 'garden', 'green', 'nature', 'zoo'],
        'museum': ['museum', 'gallery', 'art', 'history', 'exhibition'],
        'tourism': ['tourist', 'attraction', 'sightseeing', 'visit', 'explore', 'landmark']
    }
    
    found_categories = []
    text_lower = text.lower()
    
    for category, keywords in category_keywords.items():
        # Use regex for word boundary matching to avoid partial matches (e.g. "start" -> "art")
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                found_categories.append(category)
                break
    
    return found_categories if found_categories else ['restaurant', 'cafe']


def extract_preferences(text):
    """Extract user preferences from text"""
    preferences = {
        'distance_preference': 'moderate',
        'price_range': 'any',
        'rating_minimum': 3.5
    }
    
    text_lower = text.lower()
    if 'cheap' in text_lower or 'budget' in text_lower:
        preferences['price_range'] = 'cheap'
    elif 'expensive' in text_lower or 'luxury' in text_lower:
        preferences['price_range'] = 'expensive'
    
    return preferences


def parse_json_fragment(raw_text):
    """Best-effort parse for JSON snippets returned by LLMs"""
    if not raw_text:
        return None
    raw_text = raw_text.strip()
    first_brace = raw_text.find('{')
    last_brace = raw_text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace >= first_brace:
        candidate = raw_text[first_brace:last_brace + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return None


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


def normalize_category_name(name):
    if not name:
        return None
    normalized = str(name).strip().lower()
    return CATEGORY_SYNONYMS.get(normalized, normalized)


def pick_random_categories(count):
    if count <= 0:
        return []
    selections = []
    for _ in range(count):
        selections.append(random.choice(DEFAULT_JOURNEY_CATEGORY_POOL))
    return selections


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





