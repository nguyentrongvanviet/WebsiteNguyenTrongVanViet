import os
import sys

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NTVVietBlog.settings')

import django

django.setup()

import json
import google.generativeai as genai
from HomeScreen.views import parse_json_fragment, normalize_category_name

message = "I want to start from HCMUS then drinking something and then go to landmark end the trip by going to a reutaurant"

prompt = f"""
You are an expert Vietnam travel planner. Extract structured journey requirements from the user request.
Text: "{message}"

Return STRICT JSON with this schema:
{{
  "start_location": "name or null",
  "destination_count": integer or null,
  "must_visit_locations": [
    {{"name": "Landmark 81", "position": "start|any|end", "category": "landmark", "notes": "optional"}}
  ],
  "category_requests": [
    {{"category": "restaurant", "count": 1, "must_visit": true|false, "near": "optional anchor location"}}
  ],
  "must_visit_categories": ["category names if user explicitly mentioned"],
  "notes": "short summary"
}}

Rules:
- destination_count should reflect explicit numbers or remain null if unspecified.
- must_visit_locations includes any landmark/building/university mentioned.
- use "end" position if the user says something like "at the end of the trip".
- category_requests should capture intents like shopping, cafes, restaurants, sightseeing.
- If the user mentions "near LOCATION", set the "near" field to that location name.
- Keep the JSON minimal with no trailing comments.
"""

generation_config = genai.types.GenerationConfig(
    temperature=0.15,
    max_output_tokens=400,
    candidate_count=1
)

model = genai.GenerativeModel('models/gemini-2.5-flash')
response = model.generate_content(prompt, generation_config=generation_config)

print("RAW RESPONSE OBJECT:", response)
if getattr(response, 'candidates', None):
    print("CANDIDATE COUNT:", len(response.candidates))
    print("FIRST CANDIDATE FINISH REASON:", response.candidates[0].finish_reason)
    print("RAW TEXT:\n", response.text)
else:
    print("No candidates returned. Prompt feedback:", getattr(response, 'prompt_feedback', None))

parsed = parse_json_fragment(getattr(response, 'text', ''))
print("PARSED JSON:", parsed)
