#!/usr/bin/env python
"""
Debug the Gemini AI location extraction to see why it's still finding >2 locations
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

from HomeScreen.views import extract_locations_with_vietnam_context, extract_locations_with_gemini_ai

def debug_location_extraction():
    """Debug both extraction methods to see where the extra locations come from"""
    print("🔍 DEBUGGING LOCATION EXTRACTION METHODS")
    print("=" * 60)
    
    query = "What's the distance from HCMUS to 60/24 Nguyen Trai district 5 Ho chi minh city?"
    print(f"Test Query: {query}")
    print()
    
    # Test 1: Fast extraction (our fixed method)
    print("📍 Method 1: extract_locations_with_vietnam_context()")
    print("-" * 50)
    try:
        fast_locations = extract_locations_with_vietnam_context(query)
        print(f"Fast extraction result: {fast_locations}")
        print(f"Count: {len(fast_locations)}")
        print("Status: ✅ This should be 2 locations")
    except Exception as e:
        print(f"❌ Fast extraction error: {e}")
    
    print()
    
    # Test 2: Gemini AI extraction (potential culprit)
    print("🤖 Method 2: extract_locations_with_gemini_ai()")
    print("-" * 50)
    try:
        ai_locations = extract_locations_with_gemini_ai(query)
        print(f"Gemini AI extraction result: {ai_locations}")
        print(f"Count: {len(ai_locations)}")
        
        if len(ai_locations) > 2:
            print("⚠️ THIS IS THE PROBLEM! Gemini AI is finding >2 locations")
            print(f"Extra locations: {ai_locations[2:]}")
        else:
            print("✅ Gemini AI also finds only 2 locations")
    except Exception as e:
        print(f"❌ Gemini AI extraction error: {e}")
    
    print()
    print("🔧 SOLUTION ANALYSIS")
    print("-" * 30)
    
    # Show the logic flow
    try:
        fast_count = len(extract_locations_with_vietnam_context(query))
        ai_count = len(extract_locations_with_gemini_ai(query))
        
        print(f"1. Fast extraction finds: {fast_count} locations")
        print(f"2. Since {fast_count} >= 2, AI fallback should NOT be used")
        print(f"3. But if AI fallback IS used, it finds: {ai_count} locations")
        
        if fast_count >= 2 and ai_count > 2:
            print("\n💡 ISSUE: The logic should stick with fast extraction results!")
            print("   The fallback to AI is causing the multi-route problem.")
        elif fast_count >= 2 and ai_count <= 2:
            print("\n🤔 MYSTERY: Both methods find <=2 locations, but multi-route still triggers")
            print("   Need to check if there's another location extraction happening somewhere.")
    except Exception as e:
        print(f"❌ Analysis error: {e}")

if __name__ == "__main__":
    debug_location_extraction()