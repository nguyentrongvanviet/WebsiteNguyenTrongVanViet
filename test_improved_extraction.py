#!/usr/bin/env python
"""
Test improved location extraction for complex addresses
"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')
django.setup()

from HomeScreen.views import extract_locations_with_vietnam_context

def test_improved_extraction():
    """Test the improved location extraction"""
    print("🔍 Testing Improved Location Extraction")
    print("=" * 50)
    
    test_queries = [
        "What's the distance from HCMUS to 60/24 Nguyen Trai district 5 Ho chi minh city?",
        "Distance from UIT to 123 Le Van Sy District 3 HCMC",
        "How far is University of Information Technology from 456/78 Vo Van Tan Street District 1?",
        "Plan route from HCMUS to 60/24 Nguyen Trai",
        "From Bach Khoa to 789 Nguyen Hue Boulevard District 1 Ho Chi Minh City"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        locations = extract_locations_with_vietnam_context(query)
        print(f"   Extracted: {locations}")
        
        # Check if we got at least 2 locations for distance queries
        if len(locations) >= 2:
            print("   ✅ Good - Found multiple locations")
        elif len(locations) == 1:
            print("   ⚠️ Only found 1 location")
        else:
            print("   ❌ No locations found")

if __name__ == "__main__":
    test_improved_extraction()