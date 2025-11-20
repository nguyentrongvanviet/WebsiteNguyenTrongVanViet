#!/usr/bin/env python
"""
Test distance calculation from HCMUS to specific address
Tests: HCMUS to 60/24 Nguyen Trai, District 5, Ho Chi Minh City
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
    chat
)

class MockRequest:
    def __init__(self, data):
        self.body = json.dumps(data).encode('utf-8')

def test_hcmus_to_nguyen_trai():
    """Test distance from HCMUS to 60/24 Nguyen Trai, District 5"""
    print("🏛️ Testing HCMUS to 60/24 Nguyen Trai Distance Calculation")
    print("=" * 70)
    
    start_location = "HCMUS"
    end_location = "60/24 Nguyen Trai district 5 Ho chi minh city"
    
    # Test 1: Location Extraction
    print(f"\n📍 Test 1: Location Extraction")
    test_query = f"What's the distance from {start_location} to {end_location}?"
    print(f"Query: {test_query}")
    
    start_time = time.time()
    locations = extract_locations_with_vietnam_context(test_query)
    end_time = time.time()
    
    print(f"Extracted locations: {locations}")
    print(f"Extraction time: {(end_time - start_time)*1000:.2f}ms")
    
    # Test 2: Individual Geocoding
    print(f"\n🗺️ Test 2: Individual Geocoding")
    
    # Test start location
    print(f"\\nGeocoding start location: {start_location}")
    start_time = time.time()
    start_coords = geocode_location_with_gemini(start_location)
    end_time = time.time()
    if start_coords:
        print(f"✅ HCMUS coordinates: [{start_coords[0]:.6f}, {start_coords[1]:.6f}]")
    else:
        print("❌ Could not geocode HCMUS")
    print(f"Time: {(end_time - start_time)*1000:.2f}ms")
    
    # Test end location (specific address)
    print(f"\\nGeocoding end location: {end_location}")
    start_time = time.time()
    end_coords = geocode_location_with_gemini(end_location)
    end_time = time.time()
    if end_coords:
        print(f"✅ Address coordinates: [{end_coords[0]:.6f}, {end_coords[1]:.6f}]")
    else:
        print("❌ Could not geocode address")
    print(f"Time: {(end_time - start_time)*1000:.2f}ms")
    
    # Test 3: Route Calculation
    print(f"\n📏 Test 3: Route Calculation")
    try:
        request_data = {
            'start': start_location,
            'end': end_location
        }
        mock_request = MockRequest(request_data)
        
        start_time = time.time()
        response = calculate_route(mock_request)
        end_time = time.time()
        
        if hasattr(response, 'content'):
            result = json.loads(response.content.decode('utf-8'))
            if result.get('success'):
                print(f"✅ Route calculation successful!")
                print(f"   📏 Distance: {result.get('distance_km', 0)} km")
                print(f"   📏 Distance: {result.get('distance_m', 0)} meters") 
                print(f"   ⏱️ Duration: {result.get('duration', 'N/A')}")
                print(f"   🚩 Number of waypoints: {len(result.get('waypoints', []))}")
                
                # Show waypoints details
                waypoints = result.get('waypoints', [])
                if waypoints:
                    print(f"   📍 Route details:")
                    for i, wp in enumerate(waypoints):
                        print(f"      {i+1}. {wp.get('name', 'Unknown')} [{wp.get('lon', 0):.6f}, {wp.get('lat', 0):.6f}]")
            else:
                print(f"❌ Route calculation failed: {result.get('error', 'Unknown error')}")
        
        print(f"Calculation time: {(end_time - start_time)*1000:.2f}ms")
        
    except Exception as e:
        print(f"❌ Route calculation error: {e}")
    
    # Test 4: Chat Interface
    print(f"\n💬 Test 4: Chat Interface")
    chat_query = f"What's the distance from {start_location} to {end_location}?"
    print(f"Chat Query: {chat_query}")
    
    try:
        request_data = {
            'message': chat_query,
            'history': []
        }
        mock_request = MockRequest(request_data)
        
        start_time = time.time()
        response = chat(mock_request)
        end_time = time.time()
        
        if hasattr(response, 'content'):
            result = json.loads(response.content.decode('utf-8'))
            if result.get('success'):
                print(f"✅ Chat response: {result.get('response', '')}")
                print(f"   Action: {result.get('action', 'None')}")
                print(f"   Start location: {result.get('start_location', 'None')}")
                print(f"   End location: {result.get('end_location', 'None')}")
                print(f"   All locations: {result.get('all_locations', 'None')}")
            else:
                print(f"❌ Chat error: {result.get('error', 'Unknown error')}")
        
        print(f"Chat response time: {(end_time - start_time)*1000:.2f}ms")
        
    except Exception as e:
        print(f"❌ Chat error: {e}")

def test_address_variations():
    """Test different ways to write the same address"""
    print(f"\n🎯 Test 5: Address Variations")
    
    address_variations = [
        "60/24 Nguyen Trai district 5 Ho chi minh city",
        "60/24 Nguyen Trai, District 5, HCMC",
        "60/24 Nguyen Trai Street, District 5, Ho Chi Minh City",
        "60/24 Đường Nguyễn Trãi, Quận 5, TP.HCM",
        "60/24 Nguyen Trai, Q5, HCMC"
    ]
    
    print("Testing different address formats:")
    for i, address in enumerate(address_variations, 1):
        print(f"\\n{i}. Testing: {address}")
        start_time = time.time()
        coords = geocode_location_with_gemini(address)
        end_time = time.time()
        
        if coords:
            print(f"   ✅ Coordinates: [{coords[0]:.6f}, {coords[1]:.6f}]")
        else:
            print(f"   ❌ Failed to geocode")
        print(f"   Time: {(end_time - start_time)*1000:.2f}ms")

def test_distance_accuracy():
    """Test if the calculated distance seems reasonable"""
    print(f"\n🎯 Test 6: Distance Accuracy Check")
    
    # HCMUS is in District 1, and Nguyen Trai Street in District 5
    # They should be approximately 3-8 km apart in Ho Chi Minh City
    
    hcmus_coords = geocode_location_with_gemini("HCMUS")
    address_coords = geocode_location_with_gemini("60/24 Nguyen Trai district 5 Ho chi minh city")
    
    if hcmus_coords and address_coords:
        import math
        
        lat1, lon1 = hcmus_coords[1], hcmus_coords[0]
        lat2, lon2 = address_coords[1], address_coords[0]
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        print(f"Direct distance calculation:")
        print(f"HCMUS coordinates: [{hcmus_coords[0]:.6f}, {hcmus_coords[1]:.6f}]")
        print(f"Address coordinates: [{address_coords[0]:.6f}, {address_coords[1]:.6f}]")
        print(f"📏 Straight-line distance: {distance:.2f} km")
        
        # Reasonable distance check for locations in HCMC
        if 1 <= distance <= 15:
            print("✅ Distance seems reasonable for locations within Ho Chi Minh City")
        elif distance < 1:
            print("⚠️ Distance seems very short - locations might be very close or identical")
        else:
            print("⚠️ Distance seems large - please verify if coordinates are correct")
    else:
        print("❌ Could not calculate distance - geocoding failed")

if __name__ == "__main__":
    test_hcmus_to_nguyen_trai()
    test_address_variations()
    test_distance_accuracy()
    
    print("\n" + "=" * 70)
    print("🎯 HCMUS to Nguyen Trai Address Test Completed!")
    print("\nTo test in web interface:")
    print('1. Go to http://127.0.0.1:8000/HomeScreen/Welcome/')
    print('2. Click the chat button (💬)')
    print('3. Try: "What\'s the distance from HCMUS to 60/24 Nguyen Trai district 5 Ho chi minh city?"')
    print("\nThis tests the system's ability to handle:")
    print("• University abbreviations (HCMUS)")
    print("• Specific street addresses with house numbers")
    print("• Vietnamese location formatting")
    print("• Mixed English/Vietnamese address formats")