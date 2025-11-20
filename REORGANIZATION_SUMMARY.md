# Code Reorganization Summary

## Overview
The journey planning system has been reorganized into modular components to separate concerns and improve maintainability.

## New File Structure

### 1. `HomeScreen/utils.py` - Shared Utilities
**Purpose**: Common utilities used by both route calculation and journey planning

**Functions**:
- `haversine_distance()` - Calculate distance between coordinates
- `geocode_location_with_geoapify()` - Convert location names to coordinates
- `geocode_location_direct()` - Fallback geocoding
- `geoapify_autocomplete_lookup()` - Fast location lookup
- `calculate_route_with_geoapify_api()` - Calculate routes with Geoapify
- `normalize_category_name()` - Normalize category names
- `estimate_stay_minutes()` - Estimate time to stay at each location

### 2. `HomeScreen/route_calculator.py` - TASK 1: Basic Route Planning
**Purpose**: Simple distance and route calculations between locations

**Functions**:
- `calculate_route_between_locations()` - Main route calculation function
- `search_places_nearby_geoapify()` - Fallback place search using Geoapify

**Features**:
- Geocodes multiple locations
- Calculates routes using Geoapify Routing API
- Falls back to Haversine calculation if API unavailable
- Returns distance, duration, and route coordinates

### 3. `HomeScreen/journey_planner.py` - TASK 2: Advanced Journey Planning
**Purpose**: Intelligent route planning with SerpAPI integration

**Functions**:
- `execute_journey_plan()` - Main journey planning orchestrator
- `search_places_serpapi()` - Search for places using SerpAPI
- `get_place_details_serpapi()` - Get detailed place information
- `is_open_at_time()` - Check if place is open at specific time

**Features**:
- Uses SerpAPI for real-world place data
- Extracts ratings and operating hours
- Intelligent scheduling algorithm that:
  - Scores places based on rating and distance
  - Checks opening hours
  - Optimizes visit sequence
  - Estimates arrival times

**Scoring Algorithm**:
```python
# For must-go destinations:
score = -distance  # Closer is better
if open: score += 100
else: score -= 100

# For category places:
score = (rating * 10) - distance
if open: score += 100
else: score -= 100
```

### 4. `HomeScreen/views.py` - Django Views (Streamlined)
**Purpose**: HTTP request handlers and AI integration

**Remaining Functions**:
- `Welcome()` - Homepage view
- `search_location()` - Location search API
- `reverse_geocode()` - Reverse geocoding API  
- `calculate_distance()` - Simple distance calculation
- `get_map_config()` - Map configuration
- `save_marker()`, `get_markers()`, `delete_marker()` - Database operations
- `chat()` - Chatbot endpoint with intent detection
- `calculate_route()` - **TASK 1 endpoint** (delegates to `route_calculator`)
- `plan_journey()` - **TASK 2 endpoint** (delegates to `journey_planner`)
- `analyze_journey_request()` - Gemini AI intent extraction
- `extract_locations_with_vietnam_context()` - Location extraction from text
- `extract_categories()` - Category extraction from text
- All other text processing and AI functions

## Current Status

### ✅ Created Files:
- `HomeScreen/utils.py`
- `HomeScreen/route_calculator.py`
- `HomeScreen/journey_planner.py`

### ⚠️ Partial Update:
- `HomeScreen/views.py` - Imports added but duplicate functions still present

## Next Steps to Complete Reorganization

### Option 1: Manual Cleanup (Recommended)
1. Open `views.py`
2. Remove these duplicate functions (they're now in separate modules):
   - `execute_journey_plan()` (line ~485)
   - `search_places_serpapi()` (line ~710)
   - `get_place_details_serpapi()` (line ~746)
   - `is_open_at_time()` (line ~779)
   - `search_places_nearby()` (line ~806) - replace calls with `search_places_nearby_geoapify()`
   - `geocode_location_with_geoapify()` (line ~1413)
   - `geocode_location_direct()` (line ~1432)
   - `calculate_route_with_geoapify_api()` (line ~1462)
   - `haversine_distance()` (line ~1532)

3. Verify imports at top of file are correct:
```python
from .route_calculator import calculate_route_between_locations
from .journey_planner import execute_journey_plan  
from .utils import geocode_location_with_geoapify, haversine_distance
```

### Option 2: Test Current State First
The server should still work even with duplicates, since Python will use the first definition it finds. You can:
1. Restart the server
2. Test with "I want to eat catering starting from tan son nhat"
3. Verify the journey planning works
4. Then cleanup duplicates later

## Benefits of New Structure

1. **Separation of Concerns**: Each file has a clear, single purpose
2. **Maintainability**: Easier to find and update specific functionality
3. **Testability**: Can test each module independently
4. **Clarity**: Task 1 and Task 2 are clearly separated
5. **Reusability**: Utils can be used by both modules and future features

## Import Graph
```
views.py
├── route_calculator.py (TASK 1)
│   └── utils.py
├── journey_planner.py (TASK 2)
│   └── utils.py
└── utils.py (Shared)
```
