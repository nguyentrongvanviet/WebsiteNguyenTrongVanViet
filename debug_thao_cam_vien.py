
import re
import json

def extract_locations_with_vietnam_context(text):
    """Extract all location names from text - improved for complex addresses"""
    locations = []
    normalized_text = text or ""

    # Normalize leading bullets and fancy quotes so the fallback parser sees clean words
    bullet_translation = str.maketrans({
        '\u2022': ' ',  # •
        '\u25aa': ' ',  # ▪
        '\u25ab': ' ',  # ▫
        '\u25e6': ' ',  # ◦
        '\u25cf': ' ',  # ●
        '\u00b7': ' ',  # ·
    })
    normalized_text = normalized_text.translate(bullet_translation)
    normalized_text = (normalized_text
                       .replace('“', '"')
                       .replace('”', '"')
                       .replace('‘', "'")
                       .replace('’', "'"))
    normalized_text = normalized_text.strip()
    strip_chars = " \"'`´.,;:?!•*-()[]{}"
    text_lower = normalized_text.lower()
    
    print(f"DEBUG: Extracting locations from: '{normalized_text}'")
    
    # Only basic university abbreviations - let Gemini AI handle all other locations
    vietnam_abbrev = {
        'uit': 'UIT',
        'hcmus': 'HCMUS',
        'vnu': 'VNU',
        'bk': 'Bach Khoa',
    }
    
    # Check abbreviations with word boundaries
    for abbrev, full_name in vietnam_abbrev.items():
        if f' {abbrev} ' in f' {text_lower} ' or text_lower.startswith(abbrev + ' ') or text_lower.endswith(f' {abbrev}'):
            if full_name not in locations:
                locations.append(full_name)
    
    # Special handling for addresses with numbers and street names
    # Pattern for Vietnamese addresses: number/number street_name district number city
    address_pattern = r'(\d+/\d+\s+[A-Za-z\s]+(?:district|quan|quận)\s*\d+[^?]*(?:ho chi minh city|hcmc|tp hcm))'
    address_matches = re.findall(address_pattern, normalized_text, re.IGNORECASE)
    for match in address_matches:
        cleaned = match.strip(strip_chars)
        if cleaned not in locations:
            locations.append(cleaned)
    
    # Pattern for street addresses: number street_name
    street_pattern = r'(\d+/\d+\s+[A-Za-z\s]+(?:street|đường)?)'
    street_matches = re.findall(street_pattern, normalized_text, re.IGNORECASE)
    for match in street_matches:
        cleaned = match.strip(strip_chars)
        # Only add if it's not already covered by full address
        if cleaned not in locations and len(cleaned) > 5:
            locations.append(cleaned)
    
    # Skip Gemini for this local test
    additional_locations = []

    # Fallback extraction if Gemini failed or returned nothing
    if not additional_locations:
        print("DEBUG: Entering fallback extraction block")
        # Improved fallback extraction for landmarks and buildings
        words = normalized_text.split()
        print(f"DEBUG FALLBACK: Processing {len(words)} words: {words}")
        i = 0
        while i < len(words):
            word = words[i].strip(strip_chars)
            
            # Check for landmark patterns like "landmark 81", "building 123", "tower 456"
            # Also handle joined cases like "landmark81"
            if 'landmark' in word.lower() or 'building' in word.lower() or 'tower' in word.lower():
                # Case 1: "landmark81" (joined)
                if any(char.isdigit() for char in word):
                     if word not in locations:
                        locations.append(word.title())
                        print(f"Extracted joined landmark: {word.title()}")
                     i += 1
                     continue
                
                # Case 2: "landmark 81" (separated)
                if i + 1 < len(words):
                    next_word = words[i + 1].strip(strip_chars)
                    if next_word.isdigit() or (next_word and next_word[0].isupper()):
                        landmark_name = f"{word.title()} {next_word}"  # Capitalize properly
                        if landmark_name not in locations:
                            locations.append(landmark_name)
                            print(f"Extracted landmark: {landmark_name}")
                        i += 2
                        continue
            
            # Regular capitalized word extraction for fallback
            elif (len(word) > 2 and 
                word[0].isupper() and 
                word not in locations and
                word.lower() not in ['what', 'how', 'can', 'the', 'distance', 'from', 'to', 'calculating', 'design', 'trip', 'finish', 'locations']):
                
                print(f"DEBUG FALLBACK: Found capitalized word: '{word}'")
                
                # Check if it's part of a multi-word location
                location_phrase = word
                j = i + 1
                while j < len(words) and j < i + 3:  # Max 3 words for location
                    if j < len(words):
                        next_word = words[j].strip(strip_chars)
                        if (len(next_word) > 0 and 
                            (next_word[0].isupper() or 
                             next_word.lower() in ['of', 'and', 'city', 'university', 'technology', 'science'])):
                            location_phrase += ' ' + next_word
                            j += 1
                        else:
                            break
                    else:
                        break
                
                if location_phrase not in locations:
                    locations.append(location_phrase)
                    print(f"DEBUG FALLBACK: Added location: '{location_phrase}'")
                i = j if j > i + 1 else i + 1
            else:
                i += 1
    
    return locations

def test():
    query = "I want to have a journey of 6 locations starting from thao cam vien and then have a cafe and then have a banh mi then go to some park and finally end the trip at the airport"
    print(f"Testing query: {query}")
    locations = extract_locations_with_vietnam_context(query)
    print(f"Extracted locations: {locations}")

if __name__ == "__main__":
    test()
