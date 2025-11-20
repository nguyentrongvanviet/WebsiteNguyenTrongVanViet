#!/usr/bin/env python
"""
Quick test for Gemini-based geocoding
"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')
django.setup()

from HomeScreen.views import geocode_location_with_gemini

def test_gemini_geocoding():
    """Test the new Gemini-based geocoding system"""
    print("🤖 Testing Gemini-based Geocoding System\n")
    
    test_locations = [
        'UIT',
        'HCMUS', 
        'University of Information Technology',
        'Ho Chi Minh City University of Science',
        'Hanoi',
        'Da Nang'
    ]
    
    for location in test_locations:
        print(f"📍 Testing: {location}")
        try:
            coords = geocode_location_with_gemini(location)
            if coords:
                print(f"   ✅ Success: [{coords[0]:.6f}, {coords[1]:.6f}]")
            else:
                print(f"   ❌ Failed to geocode")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()

if __name__ == "__main__":
    test_gemini_geocoding()
    print("🎯 Gemini geocoding test completed!")