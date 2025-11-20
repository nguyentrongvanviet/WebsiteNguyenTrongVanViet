#!/usr/bin/env python
"""
Test script for chatbot functionality
Run this to test the key components without starting the full Django server
"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')
django.setup()

from HomeScreen.views import (
    extract_locations_with_gemini_ai, 
    geocode_location, 
    extract_journey_info_with_gemini
)

def test_location_extraction():
    """Test location extraction with Gemini AI"""
    print("🧪 Testing Location Extraction...")
    
    test_queries = [
        "What's the distance from UIT to Hanoi?",
        "How far is Ho Chi Minh City from Da Nang?",
        "Plan a trip from Bach Khoa University to Ben Nha",
        "Distance between University of Information Technology and Vung Tau"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        try:
            locations = extract_locations_with_gemini_ai(query)
            print(f"✅ Extracted locations: {locations}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_geocoding():
    """Test geocoding functionality"""
    print("\n🧪 Testing Geocoding...")
    
    test_locations = [
        "Ho Chi Minh City",
        "University of Information Technology",
        "Hanoi",
        "Da Nang",
        "Test Location Not In Cache"
    ]
    
    for location in test_locations:
        print(f"\n📍 Location: {location}")
        try:
            coords = geocode_location(location)
            if coords:
                print(f"✅ Coordinates: [{coords[0]}, {coords[1]}]")
            else:
                print(f"❌ Could not geocode location")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_journey_extraction():
    """Test journey planning extraction"""
    print("\n🧪 Testing Journey Extraction...")
    
    test_queries = [
        "Plan a journey from UIT visiting restaurants and cafes",
        "I want to explore Ho Chi Minh City, show me shopping malls and parks",
        "From Hanoi, plan a trip to museums and tourist attractions"
    ]
    
    for query in test_queries:
        print(f"\n🗺️ Query: {query}")
        try:
            info = extract_journey_info_with_gemini(query)
            print(f"✅ Start location: {info.get('start_location')}")
            print(f"✅ Categories: {info.get('categories')}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Chatbot Functionality Tests\n")
    print("=" * 50)
    
    test_location_extraction()
    test_geocoding()
    test_journey_extraction()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")