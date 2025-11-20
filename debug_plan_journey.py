import requests
import json

def test_plan_journey():
    url = 'http://127.0.0.1:8000/HomeScreen/api/plan-journey/'
    
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
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                print("\n✅ Journey planned successfully!")
                if data.get('route_coordinates'):
                    print(f"✅ Route coordinates found: {len(data['route_coordinates'])} points")
                else:
                    print("❌ No route coordinates returned")
            else:
                print(f"\n❌ Failed: {data.get('error')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_plan_journey()
