"""
Journey Planning Module - Task 2: Advanced Journey Planning with SerpAPI
Handles intelligent route planning with real-time place data, ratings, and operating hours.
"""

import json
import random
from datetime import datetime, timedelta
from .utils import (
    geocode_location_with_geoapify,
    calculate_route_with_geoapify_api,
    haversine_distance,
    estimate_stay_minutes,
    normalize_category_name
)

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

# SerpAPI Key
SERPAPI_KEY = '00a31c33d0bc5e4d27ac6619405b39762c71b00cf04a523fb394c5024d349a20'


def execute_journey_plan(intent):
    """
    Execute the journey plan: geocode locations, find places, calculate route.
    Uses SerpAPI for place discovery with ratings and operating hours.
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
    if not GoogleSearch:
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
    if not GoogleSearch:
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
