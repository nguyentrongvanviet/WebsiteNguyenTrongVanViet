#!/usr/bin/env python
"""
Test UIT to Hanoi distance query to identify the issue
"""

import requests
import json

def test_uit_hanoi():
    """Test the UIT to Hanoi distance query"""
    print("🏫 TESTING: UIT to Hanoi Distance")
    print("=" * 40)
    
    query = "What's the distance from UIT to Hanoi?"
    print(f"Query: {query}")
    
    url = "http://127.0.0.1:8000/HomeScreen/api/chat/"
    payload = {"message": query, "history": []}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=20)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n📝 CHAT RESPONSE:")
            print(f"Success: {result.get('success')}")
            print(f"Action: {result.get('action')}")
            print(f"Response: {result.get('response')}")
            print(f"All locations: {result.get('all_locations')}")
            print(f"Start location: {result.get('start_location')}")
            print(f"End location: {result.get('end_location')}")
            
            # Analyze the issue
            locations = result.get('all_locations', [])
            if not locations or len(locations) < 2:
                print(f"\n❌ ISSUE: Location extraction failed")
                print(f"Expected: ['UIT', 'Hanoi']")
                print(f"Got: {locations}")
                return False
            
            # Check if it triggers route calculation
            if result.get('action') == 'distance':
                print(f"\n✅ Action correct: triggers distance calculation")
                
                # Now test the actual route calculation
                print(f"\n🗺️ Testing route calculation...")
                
                route_url = "http://127.0.0.1:8000/HomeScreen/calculate_route/"
                route_payload = {
                    "all_locations": locations
                }
                
                route_response = requests.post(route_url, 
                                             data=json.dumps(route_payload), 
                                             headers=headers, 
                                             timeout=30)
                
                if route_response.status_code == 200:
                    route_result = route_response.json()
                    
                    print(f"Route calculation success: {route_result.get('success')}")
                    if route_result.get('success'):
                        print(f"Distance: {route_result.get('distance_km')} km")
                        print(f"Duration: {route_result.get('duration')}")
                        print(f"Waypoints: {len(route_result.get('waypoints', []))}")
                        
                        # Check if distance is reasonable (UIT to Hanoi should be ~1600+ km)
                        distance = route_result.get('distance_km', 0)
                        if distance < 1000:
                            print(f"⚠️ WARNING: Distance seems too short ({distance} km)")
                            print(f"UIT (Ho Chi Minh City) to Hanoi should be ~1600+ km")
                        elif distance > 2000:
                            print(f"⚠️ WARNING: Distance seems too long ({distance} km)")
                        else:
                            print(f"✅ Distance looks reasonable: {distance} km")
                    else:
                        print(f"❌ Route calculation failed: {route_result.get('error')}")
                else:
                    print(f"❌ Route calculation HTTP error: {route_response.status_code}")
                    print(f"Response: {route_response.text}")
            else:
                print(f"\n❌ Wrong action: {result.get('action')}")
                print(f"Expected: 'distance'")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
        
    return True

if __name__ == "__main__":
    test_uit_hanoi()