#!/usr/bin/env python
"""
Specific test for UIT and HCMUS queries
Tests distance calculation and journey planning between universities
"""

import os
import sys
import time
import django
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')
django.setup()

from HomeScreen.views import (
    extract_locations_with_vietnam_context,
    geocode_location_with_gemini,
    calculate_route,
    plan_journey,
    chat
)
from django.test import RequestFactory
from django.http import JsonResponse

class MockRequest:
    def __init__(self, data):
        self.body = json.dumps(data).encode('utf-8')

def test_uit_hcmus():
    """Test UIT and HCMUS specific functionality"""
    print("🎓 Testing UIT and HCMUS Functionality\n")
    print("=" * 60)
    
    # Test 1: Location extraction
    print("\n📍 Test 1: Location Extraction")
    test_queries = [
        "What's the distance from UIT to HCMUS?",
        "How far is University of Information Technology from Ho Chi Minh City University of Science?",
        "Plan a journey from UIT visiting restaurants",
        "Distance between HCMUS and University of Information Technology"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        start_time = time.time()
        locations = extract_locations_with_vietnam_context(query)
        end_time = time.time()
        print(f"Extracted locations: {locations}")
        print(f"Time: {(end_time - start_time)*1000:.2f}ms")
    
    # Test 2: Geocoding
    print("\n\n🗺️ Test 2: Geocoding")
    test_locations = ['UIT', 'HCMUS', 'University of Information Technology', 'Ho Chi Minh City University of Science']
    
    for location in test_locations:
        print(f"\nLocation: {location}")
        start_time = time.time()
        coords = geocode_location_with_gemini(location)
        end_time = time.time()
        if coords:
            print(f"Coordinates: [{coords[0]:.6f}, {coords[1]:.6f}]")
        else:
            print("❌ Could not geocode")
        print(f"Time: {(end_time - start_time)*1000:.2f}ms")
    
    # Test 3: Distance Calculation
    print("\n\n📏 Test 3: Distance Calculation")
    try:
        request_data = {
            'start': 'UIT',
            'end': 'HCMUS'
        }
        mock_request = MockRequest(request_data)
        
        start_time = time.time()
        response = calculate_route(mock_request)
        end_time = time.time()
        
        if hasattr(response, 'content'):
            result = json.loads(response.content.decode('utf-8'))
            if result.get('success'):
                print(f"✅ Distance from UIT to HCMUS:")
                print(f"   📏 Distance: {result.get('distance_km', 0)} km")
                print(f"   ⏱️ Duration: {result.get('duration', 'N/A')}")
                print(f"   🚩 Waypoints: {len(result.get('waypoints', []))}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        print(f"Calculation time: {(end_time - start_time)*1000:.2f}ms")
        
    except Exception as e:
        print(f"❌ Distance calculation error: {e}")
    
    # Test 4: Chat Function
    print("\n\n💬 Test 4: Chat Function")
    chat_queries = [
        "What's the distance from UIT to HCMUS?",
        "Plan a journey from University of Information Technology visiting cafes and restaurants"
    ]
    
    for query in chat_queries:
        print(f"\nChat Query: {query}")
        try:
            request_data = {
                'message': query,
                'history': []
            }
            mock_request = MockRequest(request_data)
            
            start_time = time.time()
            response = chat(mock_request)
            end_time = time.time()
            
            if hasattr(response, 'content'):
                result = json.loads(response.content.decode('utf-8'))
                if result.get('success'):
                    print(f"✅ Bot response: {result.get('response', '')[:100]}...")
                    print(f"   Action: {result.get('action', 'None')}")
                    if result.get('start_location'):
                        print(f"   Start: {result.get('start_location')}")
                    if result.get('end_location'):
                        print(f"   End: {result.get('end_location')}")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
            print(f"Response time: {(end_time - start_time)*1000:.2f}ms")
            
        except Exception as e:
            print(f"❌ Chat error: {e}")
    
    # Test 5: Journey Planning
    print("\n\n🛤️ Test 5: Journey Planning")
    try:
        request_data = {
            'start_location': 'UIT',
            'categories': ['restaurant', 'cafe']
        }
        mock_request = MockRequest(request_data)
        
        start_time = time.time()
        response = plan_journey(mock_request)
        end_time = time.time()
        
        if hasattr(response, 'content'):
            result = json.loads(response.content.decode('utf-8'))
            if result.get('success'):
                routes = result.get('routes', [])
                print(f"✅ Journey planning from UIT:")
                print(f"   🛤️ Found {len(routes)} route options")
                for i, route in enumerate(routes):
                    print(f"   Route {i+1}: {route.get('category', 'N/A')} - {route.get('total_time', 'N/A')}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        print(f"Planning time: {(end_time - start_time)*1000:.2f}ms")
        
    except Exception as e:
        print(f"❌ Journey planning error: {e}")

def test_coordinates_accuracy():
    """Test that UIT and HCMUS coordinates are accurate"""
    print("\n\n🎯 Test 6: Coordinates Accuracy")
    
    uit_coords = geocode_location_with_gemini('UIT')
    hcmus_coords = geocode_location_with_gemini('HCMUS')
    
    print(f"UIT coordinates: {uit_coords}")
    print(f"HCMUS coordinates: {hcmus_coords}")
    
    if uit_coords and hcmus_coords:
        # Calculate distance between them
        import math
        
        lat1, lon1 = uit_coords[1], uit_coords[0]
        lat2, lon2 = hcmus_coords[1], hcmus_coords[0]
        
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        print(f"\n📏 Direct distance between UIT and HCMUS: {distance:.2f} km")
        
        # This should be approximately 5-10 km since both are in HCMC
        if 5 <= distance <= 15:
            print("✅ Distance seems reasonable for two universities in HCMC")
        else:
            print("⚠️ Distance might be incorrect - please verify coordinates")

if __name__ == "__main__":
    test_uit_hcmus()
    test_coordinates_accuracy()
    print("\n" + "=" * 60)
    print("🎓 UIT and HCMUS test completed!")
    print("\nTo test in the web interface:")
    print('1. Go to http://127.0.0.1:8000/HomeScreen/Welcome/')
    print('2. Click the chat button (💬)')
    print('3. Try: "What\'s the distance from UIT to HCMUS?"')
    print('4. Try: "Plan a journey from University of Information Technology visiting restaurants"')