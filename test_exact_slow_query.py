#!/usr/bin/env python
"""
Test the EXACT query that's causing the slow via issue
"""

import requests
import json
import time

def test_fixed_query():
    """Test that the Calculating query is now fixed"""
    print("🔍 TESTING FIXED 'CALCULATING' QUERY")
    print("=" * 50)
    
    # The exact query you mentioned
    query = "Calculating route from HCMUS to 60/24 Nguyen Trai"
    print(f"Query: {query}")
    
    # Test the chat API endpoint
    url = "http://127.0.0.1:8000/HomeScreen/api/chat/"
    
    payload = {
        "message": query,
        "history": []
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("\n⏱️ Sending request...")
    start_time = time.time()
    
    try:
        response = requests.post(url, 
                               data=json.dumps(payload), 
                               headers=headers, 
                               timeout=15)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"Response time: {response_time:.3f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📝 RESPONSE ANALYSIS")
            print("-" * 30)
            print(f"Success: {result.get('success')}")
            print(f"Action: {result.get('action')}")
            print(f"Response: {result.get('response')}")
            print(f"All locations: {result.get('all_locations')}")
            
            # Check for via in response
            response_text = result.get('response', '')
            if 'via' in response_text.lower():
                print(f"\n❌ STILL HAS VIA!")
                print(f"Full response: {response_text}")
                all_locs = result.get('all_locations', [])
                print(f"Locations found: {len(all_locs)} - {all_locs}")
            else:
                print(f"\n✅ FIXED! No 'via' in response")
                
            # Check action type
            if result.get('action') == 'distance':
                print("✅ Correct action: simple distance calculation")
            elif result.get('action') == 'multi_route':
                print("❌ Still triggering multi-route")
                
            # Check location count
            locations = result.get('all_locations', [])
            if len(locations) == 2:
                print(f"✅ Perfect: Found exactly 2 locations")
                print(f"  Start: {locations[0]}")
                print(f"  End: {locations[1]}")
            else:
                print(f"⚠️ Found {len(locations)} locations instead of 2")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_other_variations():
    """Test other query variations to ensure they work"""
    print(f"\n🧪 TESTING OTHER VARIATIONS")
    print("=" * 30)
    
    test_queries = [
        "Calculate distance from HCMUS to Nguyen Trai",
        "Find route from HCMUS to 60/24 Nguyen Trai",
        "Show me the way from HCMUS to Nguyen Trai district 5"
    ]
    
    for query in test_queries:
        print(f"\nTesting: {query}")
        
        payload = {"message": query, "history": []}
        headers = {"Content-Type": "application/json"}
        url = "http://127.0.0.1:8000/HomeScreen/api/chat/"
        
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                locations = result.get('all_locations', [])
                has_via = 'via' in result.get('response', '').lower()
                
                print(f"  Locations: {len(locations)} - {locations}")
                print(f"  Action: {result.get('action')}")
                print(f"  Has 'via': {has_via}")
                
                if len(locations) == 2 and not has_via:
                    print("  ✅ Perfect!")
                else:
                    print("  ⚠️ Needs attention")
            else:
                print(f"  ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")

if __name__ == "__main__":
    test_fixed_query()
    test_other_variations()