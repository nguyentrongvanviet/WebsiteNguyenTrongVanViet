import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')
django.setup()

from HomeScreen.views import extract_locations_with_vietnam_context

# Test the problematic query
query = "What's the distance from UIT to Hanoi?"
print(f"Testing: {query}")

try:
    locations = extract_locations_with_vietnam_context(query)
    print(f"Extracted locations: {locations}")
    print(f"Number of locations: {len(locations)}")
    
    if len(locations) >= 2:
        print("✅ SUCCESS: Found both locations")
    else:
        print("❌ FAILURE: Missing locations")
        print("Expected: UIT and Hanoi")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()