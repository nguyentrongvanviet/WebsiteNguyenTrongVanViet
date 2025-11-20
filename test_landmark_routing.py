#!/usr/bin/env python
"""
Test HCMUS to Landmark 81 distance calculation with Geoapify Routing API
"""

import requests
import json
import time

def test_landmark_81_query():
    """Test the HCMUS to Landmark 81 query"""
    print("🏢 TESTING: HCMUS to Landmark 81")
    print("=" * 50)
    
    query = "distance from HCMUS to landmark 81"
    print(f"Query: {query}")
    
    url = "http://127.0.0.1:8000/HomeScreen/api/chat/"
    payload = {"message": query, "history": []}
    headers = {"Content-Type": "application/json"}
    
    print("\n⏱️ Sending request...")
    start_time = time.time()
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=30)
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n📝 RESPONSE:")
            print(f"Success: {result.get('success')}")
            print(f"Action: {result.get('action')}")
            print(f"Response: {result.get('response')}")
            print(f"Locations found: {result.get('all_locations')}")
            
            # Check if both locations were found
            locations = result.get('all_locations', [])
            if len(locations) >= 2:
                print(f"\n✅ SUCCESS! Found both locations:")
                for i, loc in enumerate(locations):
                    print(f"  {i+1}. {loc}")
            else:
                print(f"\n❌ ISSUE: Only found {len(locations)} location(s)")
                if locations:
                    print(f"Found: {locations}")
                print("Missing: Landmark 81 extraction")
                
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_routing_quality():
    """Test if routing gives more accurate results than Haversine"""
    print(f"\n🗺️ TESTING ROUTING ACCURACY")
    print("=" * 40)
    
    # Test with a well-known route
    query = "distance from HCMUS to UIT"
    
    url = "http://127.0.0.1:8000/HomeScreen/api/chat/"
    payload = {"message": query, "history": []}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Query: {query}")
            print(f"Action: {result.get('action')}")
            print(f"Response: {result.get('response')}")
            
            # If the calculate_route endpoint is called, check the result
            if result.get('action') == 'distance':
                print("\n🧪 This should trigger the Geoapify Routing API")
                print("Expected: More accurate road distance vs straight-line")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_landmark_81_query()
    test_routing_quality()