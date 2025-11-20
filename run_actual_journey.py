import os
import sys

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')

import django

django.setup()

from HomeScreen.views import design_best_journey_plan

message = "I want to start from HCMUS then drinking something and then go to landmark end the trip by going to a reutaurant"
plan = design_best_journey_plan(message)

lines = [str(plan['summary'])]
for stop in plan['journey']:
    lines.append(f"{stop['order']}. {stop['name']} ({stop['category']})")

output = '\n'.join(lines)
print(output)

with open('journey_actual_output.txt', 'w', encoding='utf-8') as fh:
    fh.write(output)
