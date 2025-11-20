import os
import sys

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')

import django

django.setup()

import HomeScreen.views as views

COORDS = {
    'start': [106.677, 10.762],
    'hcmus': [106.677, 10.762],
    'landmark 81': [106.721, 10.795],
    'landmark': [106.721, 10.795]
}

def mock_parse_intent(user_text):
    return {
        'start_location': 'HCMUS',
        'destination_count': 5,
        'must_visit_locations': [
            {'name': 'HCMUS', 'position': 'start'},
            {'name': 'Landmark 81', 'position': 'any'},
        ],
        'category_requests': [
            {'category': 'cafe', 'count': 1},
            {'category': 'landmark', 'count': 1},
            {'category': 'restaurant', 'count': 1, 'position': 'end'}
        ],
        'notes': '',
        'raw_text': user_text
    }

def mock_geocode(name):
    if not name:
        return None
    key = name.lower()
    for known, coord in COORDS.items():
        if known in key:
            return coord
    return [106.7, 10.776]

def mock_find_nearby_places(coords, category, option_number):
    return views.create_mock_journey_option(coords, category, option_number)

def mock_route(coords_list):
    return None

views.parse_best_journey_intent = mock_parse_intent
views.geocode_location_with_geoapify = mock_geocode
views.find_nearby_places = mock_find_nearby_places
views.calculate_route_with_geoapify_api = mock_route

design_best_journey_plan = views.design_best_journey_plan

message = "I want to start from HCMUS then drinking something and then go to landmark end the trip by going to a reutaurant"
plan = design_best_journey_plan(message)

lines = [str(plan['summary'])]
for stop in plan['journey']:
    lines.append(f"{stop['order']}. {stop['name']} ({stop['category']})")

output = '\n'.join(lines)
print(output)
with open('journey_mocked_output.txt', 'w', encoding='utf-8') as fh:
    fh.write(output)
