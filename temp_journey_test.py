import os
import sys

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')

import django

django.setup()

import HomeScreen.views as views


def mock_find_nearby_places(coords, category, option_number):
    return views.create_mock_journey_option(coords, category, option_number)


views.find_nearby_places = mock_find_nearby_places
design_best_journey_plan = views.design_best_journey_plan

message = "I want to start from HCMUS then drinking something and then go to landmark end the trip by going to a reutaurant"
plan = design_best_journey_plan(message)
output_lines = [str(plan['summary'])]
for stop in plan['journey']:
    output_lines.append(f"{stop['order']}. {stop['name']} ({stop['category']})")

print('\n'.join(output_lines))

with open('journey_test_output.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(output_lines))
