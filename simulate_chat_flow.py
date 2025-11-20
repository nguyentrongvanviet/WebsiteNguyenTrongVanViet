#!/usr/bin/env python
"""
Simulate the exact chat flow to identify why multi-route is triggered
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
from HomeScreen.views import chat, extract_locations_with_vietnam_context, extract_locations_with_gemini_ai

def simulate_chat_flow():
    """Simulate the exact logic flow in the chat function"""
    print("🔍 SIMULATING EXACT CHAT FLOW")
    print("=" * 50)
    
    user_message = "What's the distance from HCMUS to 60/24 Nguyen Trai district 5 Ho chi minh city?"
    print(f"User message: {user_message}")
    message_lower = user_message.lower()
    
    # Check if it's a distance request
    distance_keywords = ['distance', 'time', 'how far', 'how long', 'travel', 'route', 'shortest path', 'way', 'from', 'to']
    is_distance_request = any(word in message_lower for word in distance_keywords)
    print(f"Is distance request: {is_distance_request}")
    
    if is_distance_request:
        print("\n📍 STEP 1: Fast extraction")
        all_locations = extract_locations_with_vietnam_context(user_message)
        print(f"Fast extraction result: {all_locations}")
        print(f"Count: {len(all_locations)}")
        
        print(f"\n🤖 STEP 2: Check if AI fallback needed")
        print(f"Condition: len(all_locations) < 2 = {len(all_locations) < 2}")
        
        if len(all_locations) < 2:
            print("➡️ Using AI fallback")
            try:
                all_locations = extract_locations_with_gemini_ai(user_message)
                print(f"AI extraction result: {all_locations}")
            except Exception as e:
                print(f"AI extraction error: {e}")
        else:
            print("➡️ Skipping AI fallback (fast extraction found enough locations)")
        
        print(f"\n🎯 STEP 3: Final location count check")
        print(f"all_locations = {all_locations}")
        print(f"len(all_locations) = {len(all_locations)}")
        print(f"len(all_locations) >= 2 = {len(all_locations) >= 2}")
        
        if len(all_locations) >= 2:
            start_location = all_locations[0]
            end_location = all_locations[1]
            print(f"Start: {start_location}")
            print(f"End: {end_location}")
            
            print(f"\n🚨 CRITICAL CHECK: Multi-route trigger")
            print(f"len(all_locations) > 2 = {len(all_locations) > 2}")
            
            if len(all_locations) > 2:
                print("❌ MULTI-ROUTE TRIGGERED!")
                print(f"Extra locations: {all_locations[2:]}")
                action = 'multi_route'
                waypoints = ' → '.join(all_locations[1:-1])
                bot_response = f"📍 Calculating route from {start_location} to {end_location} via {waypoints}..."
            else:
                print("✅ SIMPLE DISTANCE CALCULATION")
                action = 'distance'
                bot_response = f"📍 Calculating route from {start_location} to {end_location}..."
            
            print(f"Action: {action}")
            print(f"Response: {bot_response}")
        else:
            print("❌ Not enough locations found")

def test_real_chat():
    """Test the actual chat endpoint"""
    print(f"\n" + "=" * 50)
    print("🌐 TESTING REAL CHAT ENDPOINT")
    print("=" * 50)
    
    factory = RequestFactory()
    request_data = {
        'message': "What's the distance from HCMUS to 60/24 Nguyen Trai district 5 Ho chi minh city?",
        'history': []
    }
    
    request = factory.post('/api/chat/', 
                          data=json.dumps(request_data),
                          content_type='application/json')
    
    try:
        response = chat(request)
        if hasattr(response, 'content'):
            result = json.loads(response.content.decode('utf-8'))
            
            print(f"Success: {result.get('success')}")
            print(f"Action: {result.get('action')}")
            print(f"Response: {result.get('response')}")
            print(f"All locations: {result.get('all_locations')}")
            
            if 'via' in result.get('response', ''):
                print("🚨 CONFIRMED: Multi-route is being triggered!")
            else:
                print("✅ Simple distance calculation")
                
    except Exception as e:
        print(f"❌ Chat error: {e}")

if __name__ == "__main__":
    simulate_chat_flow()
    test_real_chat()