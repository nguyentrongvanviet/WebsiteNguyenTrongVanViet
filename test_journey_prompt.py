import os
import sys

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')

import django

django.setup()

from HomeScreen.views import design_best_journey_plan

message = "I want to start from HCMUS then drinking something and then go to landmark end the trip by going to a reutaurant"
plan = design_best_journey_plan(message)

print('SUMMARY:', plan['summary'])
print('STOPS:')
for stop in plan['journey']:
    print(f"  {stop['order']}. {stop['name']} ({stop.get('category')})")
