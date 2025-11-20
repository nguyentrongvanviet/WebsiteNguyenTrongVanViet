#!/usr/bin/env python
"""
Simple test for HCMUS to Nguyen Trai address
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

def quick_test():
    """Quick test for the specific address"""
    print("🏛️ Quick Test: HCMUS to 60/24 Nguyen Trai")
    print("=" * 50)
    
    # Test HCMUS geocoding
    print("📍 Testing HCMUS...")
    hcmus_coords = geocode_location_with_gemini("HCMUS")
    if hcmus_coords:
        print(f"✅ HCMUS: [{hcmus_coords[0]:.6f}, {hcmus_coords[1]:.6f}]")
    else:
        print("❌ HCMUS geocoding failed")
    
    # Test address geocoding
    print("\n📍 Testing 60/24 Nguyen Trai address...")
    address = "60/24 Nguyen Trai district 5 Ho chi minh city"
    address_coords = geocode_location_with_gemini(address)
    if address_coords:
        print(f"✅ Address: [{address_coords[0]:.6f}, {address_coords[1]:.6f}]")
    else:
        print("❌ Address geocoding failed")
    
    # Calculate distance if both succeeded
    if hcmus_coords and address_coords:
        import math
        
        lat1, lon1 = hcmus_coords[1], hcmus_coords[0]
        lat2, lon2 = address_coords[1], address_coords[0]
        
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        print(f"\n📏 Calculated Distance: {distance:.2f} km")
        print(f"⏱️ Estimated time (by car): {distance/40*60:.1f} minutes")
        
        print(f"\n🎯 Test Summary:")
        print(f"From: HCMUS (Ho Chi Minh City University of Science)")
        print(f"To: 60/24 Nguyen Trai, District 5, Ho Chi Minh City")
        print(f"Distance: {distance:.2f} km")

if __name__ == "__main__":
    quick_test()