import os
import django
import json
import sys

# Add the project root to the python path
sys.path.append('v:\\WebSiteNguyenTrongVanViet')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')
django.setup()

from HomeScreen.views import execute_journey_plan

def test_execution():
    # Simulated intent from the previous step
    intent = {
        "start_location": "Thao Cam Vien",
        "must_go_destinations": [], 
        "must_go_categories": ["coffee", "restaurant", "park"],
        "travel_period": "whole day",
        "destination_count": 5
    }
    
    print(f"Testing execution with intent: {json.dumps(intent, indent=2)}")
    
    try:
        result = execute_journey_plan(intent)
        
        if result.get('success'):
            print("\nSUCCESS: Journey planned successfully!")
            print(f"Total Distance: {result['summary']['total_distance_km']} km")
            print(f"Total Time: {result['summary']['estimated_total_minutes']} min")
            print("\nItinerary:")
            for stop in result['journey']:
                print(f"- {stop['order']}. {stop['name']}")
                print(f"  Type: {stop['category']}")
                print(f"  Address: {stop.get('address', 'N/A')}")
        else:
            print(f"\nFAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"\nEXCEPTION: {e}")

if __name__ == "__main__":
    test_execution()
