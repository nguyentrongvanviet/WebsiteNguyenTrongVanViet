
import requests
import json

def test_chat_thao_cam_vien():
    url = 'http://127.0.0.1:8000/HomeScreen/api/chat/'
    
    payload = {
        "message": "I want to have a journey of 6 locations starting from thao cam vien and then have a cafe and then have a banh mi then go to some park and finally end the trip at the airport"
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
            
            if data.get('start_location'):
                print(f"\nSUCCESS: Start location found: {data.get('start_location')}")
            else:
                print("\nFAILURE: Start location NOT found.")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_chat_thao_cam_vien()
