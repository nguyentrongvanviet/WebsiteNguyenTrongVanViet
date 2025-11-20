#!/usr/bin/env python
"""
Quick test for performance improvements
Tests the fast location extraction vs AI extraction
"""

import os
import sys
import time
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')
django.setup()

from HomeScreen.views import (
    extract_locations_with_vietnam_context,
    geocode_location_with_gemini
)

def test_performance():
    """Test performance of location extraction and geocoding"""
    print("🚀 Testing Performance Improvements...\n")
    
    # Test queries
    test_queries = [
        "What's the distance from UIT to Hanoi?",
        "How far is Ho Chi Minh City from Da Nang?", 
        "Distance between University of Information Technology and Vung Tau",
        "Plan a trip from HCMC to Ben Nha"
    ]
    
    print("📍 Testing Fast Location Extraction...")
    for query in test_queries:
        start_time = time.time()
        locations = extract_locations_with_vietnam_context(query)
        end_time = time.time()
        print(f"Query: {query}")
        print(f"Locations: {locations}")
        print(f"Time: {(end_time - start_time)*1000:.2f}ms\n")
    
    print("🗺️ Testing Gemini-based Geocoding...")
    test_locations = ["UIT", "Ho Chi Minh City", "Hanoi", "Da Nang", "University of Information Technology"]
    
    for location in test_locations:
        start_time = time.time()
        coords = geocode_location_with_gemini(location)
        end_time = time.time()
        print(f"Location: {location}")
        print(f"Coordinates: {coords}")
        print(f"Time: {(end_time - start_time)*1000:.2f}ms\n")

if __name__ == "__main__":
    test_performance()
    print("✅ Performance test completed!")