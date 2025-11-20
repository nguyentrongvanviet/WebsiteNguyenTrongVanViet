import requests
import json

url = 'http://127.0.0.1:8000/HomeScreen/api/plan-journey/'
data = {
    "message": "I want to start from hcmus and then to landmark and have a cafe at last "
}

try:
    print(f"Sending request to {url}...")
    print(f"Payload: {json.dumps(data, indent=2)}")
    response = requests.post(url, json=data)
    
    print(f"\nStatus Code: {response.status_code}")
    if response.status_code == 200:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
        with open('test_output.json', 'w') as f:
            json.dump(response.json(), f, indent=2)
    else:
        print("Error Response:")
        print(response.text)
except Exception as e:
    print(f"Failed to connect: {e}")
    print("Make sure the Django server is running on port 8000")
