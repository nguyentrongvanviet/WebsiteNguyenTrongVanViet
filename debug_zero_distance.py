import os
import django
import json
import sys

# Add the project root to the python path
sys.path.append('v:\\WebSiteNguyenTrongVanViet')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')
django.setup()

from HomeScreen.views import execute_journey_plan, analyze_journey_request

def test_zero_distance():
    user_message = "I want to eat catering starting from tan son nhat"
    print(f"Testing message: '{user_message}'")
    
    # 1. Analyze Intent
    print("\n--- Analyzing Intent ---")
    try:
        intent = analyze_journey_request(user_message)
        print(json.dumps(intent, indent=2))
    except Exception as e:
        print(f"Intent analysis failed: {e}")
        return

    # 2. Execute Plan
    print("\n--- Executing Plan ---")
    try:
        result = execute_journey_plan(intent)
        
        print(f"Success: {result.get('success')}")
        if result.get('success'):
            summary = result.get('summary', {})
            print(f"Total Distance: {summary.get('total_distance_km')} km")
            print(f"Stops Planned: {summary.get('stops_planned')}")
            
            print("\nJourney Stops:")
            for stop in result.get('journey', []):
                print(f"- {stop.get('name')} ({stop.get('category')}) [Lat: {stop.get('lat')}, Lon: {stop.get('lon')}]")
                
            if summary.get('total_distance_km') == 0:
                print("\n!!! ZERO DISTANCE DETECTED !!!")
                if len(result.get('journey', [])) < 2:
                    print("Reason: Less than 2 stops found.")
                else:
                    print("Reason: Route calculation returned 0 or failed.")
        else:
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"Execution failed: {e}")

if __name__ == "__main__":
    test_zero_distance()
