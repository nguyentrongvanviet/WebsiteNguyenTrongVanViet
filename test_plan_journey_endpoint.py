import requests
import json
import time

def test_plan_journey():
    url = 'http://127.0.0.1:8000/HomeScreen/api/plan-journey/'
    
    # Simulate the payload sent by the frontend after receiving response from chat API
    payload = {
        "message": "I want to start from hcmus to landmark 81 and have a cafe at the end",
        "start_location": "hcmus",
        "categories": ["cafe"],
        "preferences": {
            "distance_preference": "moderate",
            "price_range": "any",
            "rating_minimum": 3.5
        }
    }
    
    print(f"Sending request to {url}...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse Summary:")
            print(f"Success: {data.get('success')}")
            
            if data.get('success'):
                journey = data.get('journey', [])
                print(f"Stops planned: {len(journey)}")
                for stop in journey:
                    print(f" - {stop.get('order')}. {stop.get('name')} ({stop.get('category')}) [Must Visit: {stop.get('must_visit')}]")
                
                summary = data.get('summary', {})
                print(f"\nTotal Distance: {summary.get('total_distance_km')} km")
                print(f"Total Time: {summary.get('estimated_total_minutes')} min")
                
                if data.get('route_coordinates'):
                    print(f"Route coordinates points: {len(data.get('route_coordinates'))}")
            else:
                print(f"Error in response: {data.get('error')}")
                print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_plan_journey()
