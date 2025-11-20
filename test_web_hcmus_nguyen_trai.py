#!/usr/bin/env python
"""
Test for HCMUS to Nguyen Trai address using web interface simulation
"""

import os
import sys
import django
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')
django.setup()

from django.test import RequestFactory
from HomeScreen.views import chat

def test_chat_interface():
    """Test the chat interface with HCMUS to Nguyen Trai query"""
    print("💬 Testing Chat Interface for HCMUS to Nguyen Trai")
    print("=" * 60)
    
    factory = RequestFactory()
    
    # Test query
    query = "What's the distance from HCMUS to 60/24 Nguyen Trai district 5 Ho chi minh city?"
    print(f"Query: {query}")
    
    # Create mock request
    request_data = {
        'message': query,
        'history': []
    }
    
    request = factory.post('/api/chat/', 
                          data=json.dumps(request_data),
                          content_type='application/json')
    
    try:
        print("\\n🔄 Processing chat request...")
        response = chat(request)
        
        if hasattr(response, 'content'):
            result = json.loads(response.content.decode('utf-8'))
            
            print(f"\\n✅ Chat Response:")
            print(f"Success: {result.get('success', False)}")
            
            if result.get('success'):
                print(f"Response: {result.get('response', '')}")
                print(f"Action: {result.get('action', 'None')}")
                print(f"Start Location: {result.get('start_location', 'None')}")
                print(f"End Location: {result.get('end_location', 'None')}")
                print(f"All Locations: {result.get('all_locations', 'None')}")
                
                # If it's a distance action, we can expect route calculation to follow
                if result.get('action') == 'distance':
                    print("\\n📏 Distance calculation action detected!")
                    print("The system should now call calculate_route with these locations.")
                    
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print("❌ No response content received")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_manual_coordinates():
    """Manually test with known coordinates"""
    print("\\n\\n🎯 Manual Coordinate Test")
    print("=" * 60)
    
    # Known approximate coordinates for testing
    # HCMUS (District 1) - approximate location
    hcmus_lat = 10.7625
    hcmus_lon = 106.6817
    
    # 60/24 Nguyen Trai, District 5 - approximate location
    # Nguyen Trai street runs through District 5
    nguyen_trai_lat = 10.7589  # Approximate for District 5 area
    nguyen_trai_lon = 106.6711
    
    print(f"Using approximate coordinates:")
    print(f"HCMUS: [{hcmus_lon:.6f}, {hcmus_lat:.6f}]")
    print(f"60/24 Nguyen Trai: [{nguyen_trai_lon:.6f}, {nguyen_trai_lat:.6f}]")
    
    # Calculate distance using Haversine formula
    import math
    
    R = 6371  # Earth's radius in km
    dlat = math.radians(nguyen_trai_lat - hcmus_lat)
    dlon = math.radians(nguyen_trai_lon - hcmus_lon)
    
    a = math.sin(dlat/2)**2 + math.cos(math.radians(hcmus_lat)) * \
        math.cos(math.radians(nguyen_trai_lat)) * math.sin(dlon/2)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    print(f"\\n📏 Calculated Distance: {distance:.2f} km")
    print(f"⏱️ Estimated time (30 km/h avg): {distance/30*60:.1f} minutes")
    print(f"⏱️ Estimated time (40 km/h avg): {distance/40*60:.1f} minutes")
    
    # Distance validation
    if 1 <= distance <= 10:
        print("✅ Distance seems reasonable for locations within HCMC")
    elif distance < 1:
        print("⚠️ Very short distance - locations are very close")
    else:
        print("⚠️ Distance seems large for locations within the same city")

def provide_web_test_instructions():
    """Provide instructions for manual web testing"""
    print("\\n\\n🌐 Web Interface Testing Instructions")
    print("=" * 60)
    print("To test this in your web browser:")
    print()
    print("1. Start your Django server:")
    print("   python manage.py runserver")
    print()
    print("2. Open your browser and go to:")
    print("   http://127.0.0.1:8000/HomeScreen/Welcome/")
    print()
    print("3. Click the chat button (💬) in the bottom-right corner")
    print()
    print("4. Type this exact query:")
    print("   'What's the distance from HCMUS to 60/24 Nguyen Trai district 5 Ho chi minh city?'")
    print()
    print("5. Expected behavior:")
    print("   - Bot should recognize 'HCMUS' as Ho Chi Minh City University of Science")
    print("   - Bot should recognize the full address")
    print("   - Bot should calculate distance and show route on map")
    print("   - Distance should be approximately 2-5 km")
    print()
    print("6. Alternative queries to test:")
    print("   - 'Distance from HCMUS to 60 Nguyen Trai District 5'")
    print("   - 'How far is Ho Chi Minh City University of Science from 60/24 Nguyen Trai?'")
    print("   - 'Plan route from HCMUS to Nguyen Trai street District 5'")

if __name__ == "__main__":
    test_chat_interface()
    test_manual_coordinates()
    provide_web_test_instructions()
    
    print("\\n" + "=" * 60)
    print("🎯 HCMUS to Nguyen Trai Test Summary")
    print("=" * 60)
    print("This test checks the system's ability to handle:")
    print("• University abbreviations (HCMUS)")
    print("• Specific street addresses with house numbers (60/24)")
    print("• Vietnamese street names (Nguyen Trai)")
    print("• District specifications (District 5)")
    print("• Mixed address formats")
    print()
    print("The system should provide accurate geocoding and distance calculation")
    print("between these two specific locations in Ho Chi Minh City.")