import requests
import json

def test_query():
    url = 'http://127.0.0.1:8000/HomeScreen/api/plan-journey/'
    
    payload = {
        "message": "I want to start from HCMUS and then landmark81 and have a cafe at the end"
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
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_query()
